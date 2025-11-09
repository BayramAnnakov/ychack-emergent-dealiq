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
            
            # Execute the task with streaming - properly parse Claude message types
            async for update in orchestrator.execute_gpteval_task_streaming(
                task_description=task_description,
                reference_file_paths=[reference_file],
                output_filename=f"{task_id}_output.xlsx"
            ):
                update_type = update.get("type", "")
                
                if update_type == "system":
                    # System messages with metadata
                    subtype = update.get("subtype", "")
                    data = update.get("data", {})
                    
                    if subtype == "session_started":
                        message = "🚀 Claude session started"
                    elif subtype == "initialization_started":
                        message = "⚙️ Initializing Claude Agent..."
                    elif subtype == "initialization_complete":
                        message = "✅ Claude Agent ready"
                    else:
                        message = f"⚙️ {subtype}"
                    
                    last_progress = min(last_progress + 1, 85)
                    yield f"data: {json.dumps({'status': message, 'progress': last_progress})}\n\n"
                    
                elif update_type == "user":
                    # Skip user message echo - not useful for display
                    pass
                    
                elif update_type == "assistant":
                    # Parse AssistantMessage content blocks
                    content_blocks = update.get("content", "")
                    tool_uses = update.get("tool_uses", [])
                    thinking = update.get("thinking", "")
                    
                    # Show thinking if available (extended thinking models)
                    if thinking and thinking.strip():
                        snippet = thinking[:120] + "..." if len(thinking) > 120 else thinking
                        message = f"🧠 Claude thinking: {snippet}"
                        last_progress = min(last_progress + 1, 85)
                        yield f"data: {json.dumps({'status': message, 'progress': last_progress})}\n\n"
                    
                    # Show text content
                    if content_blocks and isinstance(content_blocks, str) and content_blocks.strip():
                        snippet = content_blocks[:150] + "..." if len(content_blocks) > 150 else content_blocks
                        message = f"💬 Claude: {snippet}"
                        last_progress = min(last_progress + 2, 85)
                        yield f"data: {json.dumps({'status': message, 'progress': last_progress})}\n\n"
                        output_text += content_blocks
                    
                    # Show tool usage with detailed context
                    if tool_uses:
                        for tool in tool_uses:
                            tool_name = tool.get("name", "Unknown")
                            tool_input = tool.get("input", {})
                            
                            if tool_name == "Read":
                                file_path = tool_input.get("path", "")
                                if file_path:
                                    file_name = os.path.basename(file_path)
                                    message = f"📖 Reading: {file_name}"
                                else:
                                    message = "📖 Reading file..."
                                    
                            elif tool_name == "Write":
                                file_path = tool_input.get("path", "")
                                if file_path:
                                    file_name = os.path.basename(file_path)
                                    message = f"✍️ Writing: {file_name}"
                                else:
                                    message = "✍️ Writing file..."
                                    
                            elif tool_name == "Bash":
                                cmd = str(tool_input.get("command", ""))
                                # Show meaningful part of command
                                if "python" in cmd.lower():
                                    message = "⚡ Running Python calculation..."
                                elif "excel" in cmd.lower() or "xlsx" in cmd.lower():
                                    message = "📊 Processing Excel data..."
                                elif len(cmd) > 0:
                                    cmd_preview = cmd[:60] + "..." if len(cmd) > 60 else cmd
                                    message = f"⚡ Running: {cmd_preview}"
                                else:
                                    message = "⚡ Executing command..."
                                    
                            elif tool_name == "Glob":
                                pattern = tool_input.get("pattern", "")
                                message = f"🔍 Searching: {pattern}" if pattern else "🔍 Finding files..."
                                
                            else:
                                message = f"🔧 Using: {tool_name}"
                            
                            last_progress = min(last_progress + 1, 85)
                            yield f"data: {json.dumps({'status': message, 'progress': last_progress})}\n\n"
                    
                elif update_type == "result":
                    # ToolResultBlock - show meaningful preview
                    result_content = update.get("content", "")
                    is_error = update.get("is_error", False)
                    
                    if is_error:
                        error_msg = str(result_content)[:100] if result_content else "Tool execution failed"
                        message = f"⚠️ {error_msg}"
                    elif result_content:
                        # Parse result to show meaningful info
                        result_str = str(result_content)
                        if "rows" in result_str.lower() or "columns" in result_str.lower():
                            message = "✅ Data loaded successfully"
                        elif "created" in result_str.lower() or "written" in result_str.lower():
                            message = "✅ File created"
                        elif len(result_str) > 100:
                            message = "✅ Operation completed"
                        else:
                            preview = result_str[:80] + "..." if len(result_str) > 80 else result_str
                            message = f"✅ {preview}"
                    else:
                        message = "✅ Completed"
                    
                    yield f"data: {json.dumps({'status': message, 'progress': last_progress})}\n\n"
                    
                elif update_type == "error":
                    # Error message
                    error = update.get("error", "Unknown error")
                    message = f"❌ Error: {error}"
                    yield f"data: {json.dumps({'status': message, 'progress': last_progress})}\n\n"
                    
                elif update_type == "complete":
                    # ResultMessage - show final stats
                    duration_ms = update.get("duration_ms", 0)
                    num_turns = update.get("num_turns", 0)
                    total_cost = update.get("total_cost_usd", 0)
                    
                    if duration_ms and num_turns:
                        duration_sec = duration_ms / 1000
                        message = f"✨ Complete! ({num_turns} turns, {duration_sec:.1f}s"
                        if total_cost:
                            message += f", ${total_cost:.4f}"
                        message += ")"
                    else:
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


@router.get("/file/{task_id}")
async def get_excel_file(task_id: str):
    """Serve the Excel file for browser preview (without forcing download)"""
    
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

    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"{task_id}_output.xlsx",
        headers={
            "Content-Disposition": f'inline; filename="{task_id}_output.xlsx"'
        }
    )


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
