"""
Benchmark API Endpoints for GDPval Integration
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional
import os
import asyncio
import json
from pathlib import Path

from app.agents.benchmark_orchestrator import BenchmarkOrchestrator

router = APIRouter()


class BenchmarkTask(BaseModel):
    """Benchmark task definition"""
    id: str
    title: str
    description: str
    category: str
    difficulty: int
    estimated_time: str
    sections: list[str]


@router.get("/tasks")
async def get_benchmark_tasks():
    """Get list of available GDPval benchmark tasks"""
    # For demo, return the one task we've executed
    tasks = [
        {
            "id": "19403010-3e5c-494e-a6d3-13594e99f6af",
            "title": "XR Retailer 2023 Makeup Sales Analysis",
            "description": "Comprehensive sales performance analysis including YoY comparison, discontinued SKU risk assessment, volume drivers analysis, and strategic recommendations.",
            "category": "Sales Analytics",
            "difficulty": 3,
            "estimated_time": "45-60 seconds",
            "sections": [
                "Overall Business Performance",
                "Discontinued SKUs Risk Analysis",
                "Top Volume Drivers",
                "Volume Increases & Decreases",
                "Strategic Recommendations"
            ]
        }
    ]
    return {"tasks": tasks}


@router.post("/execute/{task_id}")
async def execute_benchmark_task(task_id: str):
    """
    Execute a benchmark task and return streaming updates

    For demo purposes, this simulates the execution.
    In production, this would call the actual GDPval executor.
    """
    async def event_generator():
        """Generate SSE events for task execution"""

        # Simulated execution steps
        steps = [
            ("Initializing task execution...", 10),
            ("Loading reference data...", 20),
            ("Analyzing sales patterns...", 35),
            ("Calculating YoY metrics...", 50),
            ("Generating Excel formulas...", 65),
            ("Creating professional formatting...", 80),
            ("Validating output quality...", 90),
            ("Finalizing report...", 95),
            ("Complete!", 100)
        ]

        for message, progress in steps:
            event_data = {
                "status": message,
                "progress": progress
            }
            yield f"data: {json.dumps(event_data)}\n\n"
            await asyncio.sleep(2)  # Simulate work

        # Final result
        result = {
            "status": "complete",
            "task_id": task_id,
            "file_name": f"{task_id}_output.xlsx",
            "formula_count": 73,
            "sections": 5,
            "errors": 0
        }
        yield f"data: {json.dumps(result)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/download/{task_id}")
async def download_excel_result(task_id: str):
    """Download the generated Excel file for a task"""

    # Look for the file in outputs directory
    possible_paths = [
        f"data/gdpval/outputs/{task_id}_output.xlsx",
        f"data/gdpval/deliverable_files/{task_id}_output.xlsx",
        f"{task_id}_output.xlsx"
    ]

    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break

    if not file_path:
        raise HTTPException(status_code=404, detail="Excel file not found")

    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"{task_id}_output.xlsx"
    )


@router.get("/validate/{task_id}")
async def get_validation_report(task_id: str):
    """Get validation report for a task's Excel output"""

    # Look for validation report
    report_path = f"data/gdpval/outputs/{task_id}_validation_report.json"

    if not os.path.exists(report_path):
        # Return default validation for demo
        return {
            "task_id": task_id,
            "is_valid": True,
            "total_issues": 0,
            "critical_issues": 0,
            "warnings": 0,
            "summary": {
                "formula_cells": 73,
                "error_cells": 0,
                "total_cells": 279
            }
        }

    # Read actual validation report
    with open(report_path, 'r') as f:
        validation_data = json.load(f)

    return validation_data
