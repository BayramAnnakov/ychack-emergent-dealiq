"""
Insights generation endpoints
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio

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