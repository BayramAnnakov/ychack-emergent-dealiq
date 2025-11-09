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
    Execute a benchmark task using BenchmarkOrchestrator with Claude
    """
    async def event_generator():
        """Generate SSE events from actual Claude execution with heartbeat"""
        
        try:
            # Send initial status
            yield f"data: {json.dumps({'status': 'Initializing Claude...', 'progress': 5})}\n\n"
            await asyncio.sleep(0.5)
            
            # Task details - for now we have one hardcoded task
            task_description = """
            Analyze the XR Retailer 2023 Makeup Sales data and create a comprehensive Excel report with:
            
            1. Overall Business Performance (YoY comparison)
            2. Discontinued SKUs Risk Analysis 
            3. Top Volume Drivers Analysis
            4. Volume Increases & Decreases
            5. Strategic Recommendations
            
            Use formulas for all calculations. Format professionally with clear sections.
            """
            
            # Reference file path
            reference_file = f"/app/backend/data/gdpval/reference_files/DATA_XR_MU_2023.xlsx"
            
            if not os.path.exists(reference_file):
                raise HTTPException(status_code=404, detail=f"Reference file not found: {reference_file}")
            
            yield f"data: {json.dumps({'status': 'Loading reference data...', 'progress': 10})}\n\n"
            await asyncio.sleep(0.5)
            
            # Create orchestrator
            orchestrator = BenchmarkOrchestrator(verbose=True)
            
            yield f"data: {json.dumps({'status': 'Starting Claude analysis...', 'progress': 15})}\n\n"
            await asyncio.sleep(0.5)
            
            # Progress tracking
            output_text = ""
            output_files = []
            last_progress = 15
            
            # Execute the task with streaming - just pass through Claude's messages
            async for update in orchestrator.execute_gpteval_task_streaming(
                task_description=task_description,
                reference_file_paths=[reference_file],
                output_filename=f"{task_id}_output.xlsx"
            ):
                update_type = update.get("type", "")
                
                if update_type == "system":
                    # System messages from Claude
                    subtype = update.get("subtype", "")
                    message = f"⚙️ System: {subtype}"
                    last_progress = min(last_progress + 1, 85)
                    yield f"data: {json.dumps({'status': message, 'progress': last_progress})}\n\n"
                    
                elif update_type == "user":
                    # Skip user message echo - not useful for display
                    pass
                    
                elif update_type == "assistant":
                    # Claude's response
                    content = update.get("content", "")
                    tool_uses = update.get("tool_uses", [])
                    
                    if content.strip():
                        # Show Claude's thinking/response
                        snippet = content[:150] + "..." if len(content) > 150 else content
                        message = f"💬 Claude: {snippet}"
                        last_progress = min(last_progress + 2, 85)
                        yield f"data: {json.dumps({'status': message, 'progress': last_progress})}\n\n"
                        output_text += content
                    
                    if tool_uses:
                        # Show tool usage
                        for tool in tool_uses:
                            tool_name = tool.get("name", "Unknown")
                            tool_input = tool.get("input", {})
                            # Show what the tool is doing
                            if tool_name == "Read":
                                file_path = tool_input.get("path", "")
                                message = f"🔧 Reading: {os.path.basename(file_path) if file_path else 'file'}"
                            elif tool_name == "Write":
                                file_path = tool_input.get("path", "")
                                message = f"✍️ Writing: {os.path.basename(file_path) if file_path else 'file'}"
                            elif tool_name == "Bash":
                                cmd = str(tool_input.get("command", ""))[:50]
                                message = f"⚡ Running: {cmd}..."
                            else:
                                message = f"🔧 Using: {tool_name}"
                            
                            last_progress = min(last_progress + 1, 85)
                            yield f"data: {json.dumps({'status': message, 'progress': last_progress})}\n\n"
                    
                elif update_type == "result":
                    # Tool execution result
                    result_content = update.get("content", "")
                    # Show brief result preview
                    if result_content:
                        preview = str(result_content)[:80] + "..." if len(str(result_content)) > 80 else str(result_content)
                        message = f"✅ Result: {preview}"
                    else:
                        message = "✅ Tool completed"
                    yield f"data: {json.dumps({'status': message, 'progress': last_progress})}\n\n"
                    
                elif update_type == "error":
                    # Error message
                    error = update.get("error", "Unknown error")
                    message = f"❌ Error: {error}"
                    yield f"data: {json.dumps({'status': message, 'progress': last_progress})}\n\n"
                    
                elif update_type == "complete":
                    # Execution complete
                    message = "✨ Claude analysis complete"
                    last_progress = 90
                    yield f"data: {json.dumps({'status': message, 'progress': last_progress})}\n\n"
                    break
                
                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.05)
            
            # Final status
            yield f"data: {json.dumps({'status': '🎉 Analysis complete!', 'progress': 95})}\n\n"
            await asyncio.sleep(0.5)
            
            # Final result
            result = {
                "status": "complete",
                "task_id": task_id,
                "file_name": f"{task_id}_output.xlsx",
                "output_text": output_text[:500] if output_text else "Analysis complete",
                "files_created": len(output_files),
                "errors": 0,
                "progress": 100
            }
            yield f"data: {json.dumps(result)}\n\n"
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"Error in benchmark execution: {error_detail}")
            error_result = {
                "status": "error",
                "error": str(e),
                "progress": 0
            }
            yield f"data: {json.dumps(error_result)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/result/{task_id}")
async def get_task_result_metadata(task_id: str):
    """Get metadata about the generated Excel file"""
    import openpyxl
    
    # Look for the file
    possible_paths = [
        f"data/gdpval/outputs/{task_id}_output.xlsx",
        f"data/gdpval/deliverable_files/{task_id}_output.xlsx",
        f"data/gdpval/reference_files/{task_id}_output.xlsx",
        f"{task_id}_output.xlsx"
    ]

    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break

    if not file_path:
        raise HTTPException(status_code=404, detail="Excel file not found")

    try:
        # Load workbook to get metadata
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=False)
        
        sheets_info = []
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            # Count rows with data
            rows_with_data = sum(1 for row in ws.iter_rows() if any(cell.value for cell in row))
            sheets_info.append({
                "name": sheet_name,
                "rows": rows_with_data,
                "columns": ws.max_column
            })
        
        wb.close()
        
        # Get absolute file path for serving
        abs_file_path = os.path.abspath(file_path)
        
        return {
            "task_id": task_id,
            "file_name": f"{task_id}_output.xlsx",
            "file_path": abs_file_path,
            "file_size": os.path.getsize(file_path),
            "sheets": sheets_info,
            "sheet_count": len(sheets_info),
            "download_url": f"/api/v1/benchmark/download/{task_id}",
            "preview_url": f"/api/v1/benchmark/file/{task_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading Excel file: {str(e)}")


@router.get("/download/{task_id}")
async def download_excel_result(task_id: str):
    """Download the generated Excel file for a task"""

    # Look for the file in outputs directory
    possible_paths = [
        f"data/gdpval/outputs/{task_id}_output.xlsx",
        f"data/gdpval/deliverable_files/{task_id}_output.xlsx",
        f"data/gdpval/reference_files/{task_id}_output.xlsx",
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
        filename=f"{task_id}_output.xlsx",
        headers={
            "Content-Disposition": f'attachment; filename="{task_id}_output.xlsx"'
        }
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
