"""
Streaming analysis endpoints using Server-Sent Events (SSE)
Bridges the new StreamingOrchestrator with the existing frontend
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import os
import re
import asyncio
import logging

from app.agents.orchestrator_streaming import StreamingOrchestrator
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

router = APIRouter()


class StreamingAnalysisRequest(BaseModel):
    """Request model for streaming analysis"""
    file_id: str
    query: str
    analysis_type: Optional[str] = "general"


def parse_markdown_to_insights(markdown_text: str) -> list:
    """
    Parse Claude's markdown output into structured insights

    Extracts sections from markdown and converts to insight format
    expected by frontend
    """
    insights = []

    # Split by major headers (##)
    sections = re.split(r'\n##\s+', markdown_text)

    for i, section in enumerate(sections):
        if not section.strip():
            continue

        # Extract title (first line)
        lines = section.strip().split('\n', 1)
        if not lines:
            continue

        title = lines[0].strip().replace('#', '').strip()

        # Extract content
        content = lines[1] if len(lines) > 1 else ""

        # Determine insight type based on keywords
        insight_type = "general"
        title_lower = title.lower()

        if any(word in title_lower for word in ["metric", "kpi", "statistics", "stats"]):
            insight_type = "metrics"
        elif any(word in title_lower for word in ["trend", "pattern", "analysis"]):
            insight_type = "trend"
        elif any(word in title_lower for word in ["recommendation", "action", "priority"]):
            insight_type = "action"
        elif any(word in title_lower for word in ["risk", "warning", "issue", "problem"]):
            insight_type = "risk"
        elif any(word in title_lower for word in ["opportunity", "quick win", "potential"]):
            insight_type = "opportunity"

        # Calculate pseudo-confidence based on content specificity
        # More specific content (numbers, bullets) = higher confidence
        has_numbers = bool(re.search(r'\d+', content))
        has_bullets = bool(re.search(r'[-*]\s', content))
        has_tables = bool(re.search(r'\|', content))

        confidence = 0.6
        if has_numbers:
            confidence += 0.1
        if has_bullets:
            confidence += 0.1
        if has_tables:
            confidence += 0.15
        confidence = min(confidence, 0.95)

        insights.append({
            "source": "ClaudeAnalysis",
            "type": insight_type,
            "title": title,
            "description": content.strip()[:500],  # First 500 chars
            "full_content": content.strip(),
            "confidence": confidence,
            "data": {
                "section_index": i,
                "has_metrics": has_numbers,
                "has_recommendations": has_bullets
            }
        })

    # If no sections found, treat entire text as one insight
    if not insights:
        insights.append({
            "source": "ClaudeAnalysis",
            "type": "general",
            "title": "Analysis Results",
            "description": markdown_text[:500],
            "full_content": markdown_text,
            "confidence": 0.75,
            "data": {}
        })

    return insights


def resolve_file_path(file_id: str) -> str:
    """
    Resolve file_id to actual file path for uploaded files

    Args:
        file_id: UUID of uploaded file

    Returns:
        Relative path from project root (for Claude SDK cwd)

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    # Try each allowed extension
    for ext in settings.ALLOWED_EXTENSIONS:
        # Path relative to project root
        relative_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")

        # Check if file exists (absolute path for checking)
        absolute_path = os.path.abspath(relative_path)

        if os.path.exists(absolute_path):
            return relative_path

    raise FileNotFoundError(f"No file found for ID: {file_id}")


async def stream_analysis(file_id: str, query: str, analysis_type: str = "general"):
    """
    Generator that yields SSE-formatted events for streaming analysis
    """
    try:
        logger.info(f"=== STREAMING ANALYSIS STARTED ===")
        logger.info(f"File ID: {file_id}")
        logger.info(f"Query: {query}")
        logger.info(f"Analysis Type: {analysis_type}")

        # Resolve file path
        logger.info(f"Resolving file path for file_id: {file_id}")
        file_path = resolve_file_path(file_id)
        logger.info(f"Resolved file path: {file_path}")

        # Send initial status
        logger.info("Sending initial status to client")
        yield f"data: {json.dumps({'type': 'status', 'message': 'Initializing analysis...', 'progress': 0})}\n\n"

        # Create orchestrator
        logger.info("Creating StreamingOrchestrator instance")
        orchestrator = StreamingOrchestrator(verbose=False)
        logger.info("StreamingOrchestrator created successfully")

        # Track complete markdown for final insights
        complete_markdown = ""
        progress = 0

        # Stream analysis
        logger.info("Starting analyze_file_streaming...")
        async for update in orchestrator.analyze_file_streaming(
            file_path=file_path,
            analysis_type=analysis_type,
            description=query
        ):
            logger.info(f"Received update: type={update.get('type')}")

            if update["type"] == "system":
                logger.info("Received SystemMessage")
                yield f"data: {json.dumps({'type': 'status', 'message': 'Connecting to Claude...', 'progress': 5})}\n\n"
                progress = 5

            elif update["type"] == "assistant":
                logger.info(f"Received AssistantMessage, content length={len(update.get('content', ''))}")
                content = update.get("content", "")
                complete_markdown += content

                # Send partial content with better status messages
                if content.strip():
                    # Determine what phase we're in based on content
                    if not complete_markdown or len(complete_markdown) < 100:
                        status_msg = "🤖 Claude is analyzing your data..."
                        progress = 30
                    elif len(complete_markdown) < 1000:
                        status_msg = "📊 Calculating metrics and statistics..."
                        progress = 50
                    elif len(complete_markdown) < 3000:
                        status_msg = "💡 Generating insights and recommendations..."
                        progress = 70
                    else:
                        status_msg = "✨ Finalizing comprehensive analysis..."
                        progress = 85

                    yield f"data: {json.dumps({'type': 'partial', 'content': content, 'progress': progress, 'message': status_msg})}\n\n"

                # Send tool usage updates
                tool_uses = update.get("tool_uses", [])
                for tool in tool_uses:
                    tool_name = tool.get("name", "Unknown")
                    tool_input = tool.get("input", {})

                    # Create more descriptive message based on tool type
                    if tool_name == "Read":
                        file_path = tool_input.get("file_path", "")
                        filename = file_path.split('/')[-1] if file_path else "file"
                        message = f"📖 Reading CRM data from {filename}"
                        progress = 25
                    elif tool_name == "Grep":
                        pattern = tool_input.get("pattern", "")[:30]
                        message = f"🔍 Searching for: {pattern}"
                        progress = min(progress + 5, 85)
                    elif tool_name == "Bash":
                        command = tool_input.get("command", "")[:40]
                        message = f"⚙️  Running: {command}..."
                        progress = min(progress + 5, 85)
                    elif tool_name == "Glob":
                        pattern = tool_input.get("pattern", "")
                        message = f"📁 Finding files: {pattern}"
                        progress = min(progress + 5, 85)
                    else:
                        message = f"🔧 Using {tool_name}"
                        progress = min(progress + 5, 85)

                    yield f"data: {json.dumps({'type': 'tool', 'tool_name': tool_name, 'message': message, 'progress': progress})}\n\n"
                    logger.info(f"Tool usage sent to client: {message}")

            elif update["type"] == "result":
                # Parse markdown into structured insights
                insights = parse_markdown_to_insights(complete_markdown)

                # Send final result
                result = {
                    "type": "complete",
                    "query": query,
                    "insights": insights,
                    "confidence": sum(i["confidence"] for i in insights) / len(insights) if insights else 0.75,
                    "processing_time": update.get("duration_ms", 0) / 1000,
                    "cost_usd": update.get("cost_usd", 0),
                    "markdown": complete_markdown,
                    "progress": 100
                }
                
                # Save analysis to history
                try:
                    import os
                    import json
                    from datetime import datetime
                    
                    history_dir = "data/crm_analyses"
                    os.makedirs(history_dir, exist_ok=True)
                    
                    analysis_id = f"{file_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    history_file = f"{history_dir}/{analysis_id}_analysis.json"
                    
                    history_data = {
                        "analysis_id": analysis_id,
                        "query": query,
                        "query_type": analysis_type,
                        "file_id": file_id,
                        "insights": insights,
                        "confidence": result["confidence"],
                        "processing_time": result["processing_time"],
                        "markdown": complete_markdown,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    with open(history_file, 'w') as f:
                        json.dump(history_data, f, indent=2)
                    
                    logger.info(f"Saved analysis to history: {analysis_id}")
                except Exception as e:
                    logger.error(f"Failed to save analysis history: {e}")

                yield f"data: {json.dumps(result)}\n\n"

            elif update["type"] == "error":
                logger.error(f"Received error: {update.get('error')}")
                yield f"data: {json.dumps({'type': 'error', 'message': update.get('error', 'Unknown error')})}\n\n"

        logger.info("=== STREAMING ANALYSIS COMPLETED ===")

    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    except Exception as e:
        logger.error(f"Analysis failed with exception: {str(e)}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'message': f'Analysis failed: {str(e)}'})}\n\n"


@router.post("/analyze-stream")
async def analyze_stream(request: StreamingAnalysisRequest):
    """
    Stream analysis results using Server-Sent Events (SSE)

    This endpoint bridges the new StreamingOrchestrator with the existing
    frontend by converting Claude's markdown output into structured insights.
    """
    logger.info(f"=== STREAMING ENDPOINT CALLED ===")
    logger.info(f"Request: file_id={request.file_id}, query={request.query[:50]}..., type={request.analysis_type}")

    return StreamingResponse(
        stream_analysis(
            file_id=request.file_id,
            query=request.query,
            analysis_type=request.analysis_type
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/status")
async def streaming_status():
    """Check if streaming service is available"""
    try:
        # Quick health check
        orchestrator = StreamingOrchestrator(verbose=False)
        return {
            "status": "available",
            "orchestrator": "StreamingOrchestrator",
            "features": ["sse_streaming", "claude_sdk", "file_based_analysis"]
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Streaming service unavailable: {str(e)}")
