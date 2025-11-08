"""
Agent management and interaction endpoints
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import asyncio

from app.agents.orchestrator import OrchestratorAgent
from app.core.config import settings

router = APIRouter()


class AgentQuery(BaseModel):
    """Model for agent query requests"""
    agent_type: str
    query: str
    context: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Model for agent responses"""
    agent_type: str
    response: Dict[str, Any]
    processing_time: float
    status: str


@router.get("/")
async def list_agents():
    """
    List all available agents and their capabilities
    """
    agents = [
        {
            "name": "DataIngestionAgent",
            "description": "Handles CSV/CRM data parsing and normalization",
            "capabilities": ["parse_csv", "detect_schema", "clean_data"]
        },
        {
            "name": "AnalyticsAgent",
            "description": "Performs statistical analysis on sales data",
            "capabilities": ["basic_stats", "trend_analysis", "cohort_analysis"]
        },
        {
            "name": "PredictiveAgent",
            "description": "ML-based predictions for deals and revenue",
            "capabilities": ["deal_scoring", "revenue_forecast", "risk_assessment"]
        },
        {
            "name": "InsightAgent",
            "description": "Generates natural language insights and recommendations",
            "capabilities": ["summarize", "identify_patterns", "recommend_actions"]
        },
        {
            "name": "HypothesisAgent",
            "description": "Tests sales hypotheses against historical data",
            "capabilities": ["correlation_analysis", "ab_testing", "playbook_discovery"]
        }
    ]

    return {"agents": agents, "total": len(agents)}


@router.post("/query")
async def query_agent(request: AgentQuery):
    """
    Send a query to a specific agent
    """
    valid_agents = ["ingestion", "analytics", "predictive", "insight", "hypothesis"]

    if request.agent_type not in valid_agents:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent type. Must be one of: {valid_agents}"
        )

    try:
        orchestrator = OrchestratorAgent()

        # Route query to specific agent
        result = await orchestrator.route_to_agent(
            agent_type=request.agent_type,
            query=request.query,
            context=request.context
        )

        return AgentResponse(
            agent_type=request.agent_type,
            response=result,
            processing_time=result.get("processing_time", 0),
            status="success"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/chat")
async def agent_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time agent interaction
    """
    await websocket.accept()

    orchestrator = OrchestratorAgent()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Process through orchestrator
            if message.get("type") == "query":
                # Send initial acknowledgment
                await websocket.send_json({
                    "type": "status",
                    "message": "Processing query...",
                    "status": "processing"
                })

                # Process query
                result = await orchestrator.process_streaming_query(
                    query=message.get("query"),
                    file_id=message.get("file_id"),
                    callback=lambda x: asyncio.create_task(
                        websocket.send_json({
                            "type": "partial",
                            "data": x
                        })
                    )
                )

                # Send final result
                await websocket.send_json({
                    "type": "result",
                    "data": result,
                    "status": "complete"
                })

            elif message.get("type") == "ping":
                # Handle ping
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        await websocket.close()


@router.get("/status")
async def get_agents_status():
    """
    Get the status of all agents
    """
    orchestrator = OrchestratorAgent()
    status = await orchestrator.get_agents_status()

    return {
        "status": status,
        "timestamp": asyncio.get_event_loop().time()
    }