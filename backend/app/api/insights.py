"""
Insights generation endpoints
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import os
import json

from app.agents.orchestrator import OrchestratorAgent
from app.core.config import settings

router = APIRouter()


class InsightQuery(BaseModel):
    """Model for insight query requests"""
    file_id: str
    query: str
    insight_type: Optional[str] = "general"


class InsightResponse(BaseModel):
    """Model for insight responses"""
    query: str
    insights: List[Dict[str, Any]]
    confidence: float
    processing_time: float


@router.post("/analyze", response_model=InsightResponse)
async def analyze_data(request: InsightQuery):
    """
    Analyze uploaded data and generate insights based on natural language query
    """
    try:
        # Initialize orchestrator agent
        orchestrator = OrchestratorAgent()

        # Process the query
        result = await orchestrator.process_query(
            file_id=request.file_id,
            query=request.query,
            insight_type=request.insight_type
        )

        return InsightResponse(**result)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quick/{file_id}")
async def get_quick_insights(file_id: str):
    """
    Get quick insights from uploaded file without specific query
    """
    try:
        orchestrator = OrchestratorAgent()

        # Generate default insights
        insights = await orchestrator.generate_quick_insights(file_id)

        return {
            "file_id": file_id,
            "insights": insights,
            "status": "success"
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hypothesis")
async def test_hypothesis(
    file_id: str = Body(...),
    hypothesis: str = Body(...),
):
    """
    Test a sales hypothesis against the data

    Example: "Deals with multiple stakeholders close faster"
    """
    try:
        orchestrator = OrchestratorAgent()

        # Test hypothesis
        result = await orchestrator.test_hypothesis(
            file_id=file_id,
            hypothesis=hypothesis
        )

        return {
            "hypothesis": hypothesis,
            "result": result,
            "status": "success"
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict")
async def predict_outcomes(
    file_id: str = Body(...),
    prediction_type: str = Body(...),
    target: Optional[str] = Body(None)
):
    """
    Generate predictions based on historical data

    Types: deal_closure, quota_attainment, pipeline_health
    """
    valid_types = ["deal_closure", "quota_attainment", "pipeline_health", "churn_risk"]

    if prediction_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid prediction type. Must be one of: {valid_types}"
        )

    try:
        orchestrator = OrchestratorAgent()

        # Generate predictions
        predictions = await orchestrator.generate_predictions(
            file_id=file_id,
            prediction_type=prediction_type,
            target=target
        )

        return {
            "prediction_type": prediction_type,
            "predictions": predictions,
            "status": "success"
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_analysis_history():
    """Get history of CRM analyses from saved files"""
    from datetime import datetime
    
    history_dir = "data/crm_analyses"
    os.makedirs(history_dir, exist_ok=True)
    
    analyses = []
    
    if os.path.exists(history_dir):
        for filename in os.listdir(history_dir):
            if filename.endswith("_analysis.json"):
                file_path = os.path.join(history_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    file_stat = os.stat(file_path)
                    
                    analyses.append({
                        "analysis_id": filename.replace("_analysis.json", ""),
                        "query": data.get("query", ""),
                        "query_type": data.get("query_type", "analyze"),
                        "insight_count": len(data.get("insights", [])),
                        "created_at": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        "file_name": data.get("original_filename", ""),
                        "preview": data.get("insights", [{}])[0].get("description", "")[:150] if data.get("insights") else ""
                    })
                except Exception as e:
                    print(f"Error loading analysis {filename}: {e}")
                    continue
    
    # Sort by created time (newest first)
    analyses.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "analyses": analyses,
        "total": len(analyses)
    }


@router.get("/history/{analysis_id}")
async def get_analysis_detail(analysis_id: str):
    """Get full details of a saved analysis"""
    
    file_path = f"data/crm_analyses/{analysis_id}_analysis.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    return data




@router.post("/export-pdf/{analysis_id}")
async def export_insights_as_pdf(analysis_id: str):
    """
    Export saved analysis as a professional PDF report using Claude pdf skill
    """
    from app.agents.benchmark_orchestrator import BenchmarkOrchestrator
    
    # Load the analysis
    file_path = f"data/crm_analyses/{analysis_id}_analysis.json"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    with open(file_path, 'r') as f:
        analysis_data = json.load(f)
    
    # Build a prompt for Claude to create a professional PDF
    insights = analysis_data.get("insights", [])
    query = analysis_data.get("query", "")
    
    prompt = f"""Create a professional PDF report summarizing these CRM insights.

**Original Query:** {query}

**Insights to Include:**

"""
    
    for idx, insight in enumerate(insights, 1):
        prompt += f"\n{idx}. **{insight.get('title', 'Insight')}**\n"
        prompt += f"   {insight.get('description', '')}\n"
        if insight.get('data'):
            prompt += f"   Key Data: {insight.get('data')}\n"
        prompt += f"   Confidence: {insight.get('confidence', 0.5) * 100:.0f}%\n"
    
    prompt += f"""

Create a 2-3 page professional PDF report with:
1. Title: "CRM Analysis Report - {query}"
2. Executive Summary section
3. Key Insights section with all {len(insights)} insights
4. Data visualizations or tables where appropriate
5. Professional formatting with proper spacing, headers, and layout

**CRITICAL:** Use proportional column widths and proper text wrapping to avoid overflow.

Save as: {analysis_id}_report.pdf
"""
    
    try:
        # Use BenchmarkOrchestrator with pdf skill to generate PDF
        orchestrator = BenchmarkOrchestrator(verbose=True)
        
        output_filename = f"{analysis_id}_report.pdf"
        
        # Execute with Claude
        async for update in orchestrator.execute_gpteval_task_streaming(
            task_description=prompt,
            reference_file_paths=[],
            output_filename=output_filename
        ):
            # Process but don't stream to client (generate synchronously)
            pass
        
        # Find the generated PDF
        import glob
        pdf_patterns = [
            f"data/crm_analyses/{output_filename}",
            f".claude/skills/pdf/{output_filename}",
            f"{output_filename}"
        ]
        
        pdf_path = None
        for pattern in pdf_patterns:
            matches = glob.glob(pattern)
            if matches:
                pdf_path = max(matches, key=os.path.getmtime)
                break
        
        if not pdf_path:
            raise HTTPException(status_code=500, detail="PDF generation failed")
        
        # Move to crm_analyses directory
        final_path = f"data/crm_analyses/{output_filename}"
        if pdf_path != final_path:
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            import shutil
            shutil.copy(pdf_path, final_path)
        
        return {
            "status": "success",
            "pdf_filename": output_filename,
            "file_size": os.path.getsize(final_path),
            "download_url": f"/api/v1/insights/download-pdf/{analysis_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/download-pdf/{analysis_id}")
async def download_pdf_report(analysis_id: str):
    """Download the PDF report for an analysis"""
    from fastapi.responses import FileResponse
    
    pdf_path = f"data/crm_analyses/{analysis_id}_report.pdf"
    
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF report not found")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{analysis_id}_report.pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{analysis_id}_report.pdf"'
        }
    )
