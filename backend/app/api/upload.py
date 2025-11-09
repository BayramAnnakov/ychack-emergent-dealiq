"""
File upload endpoints for CRM data
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import os
import uuid
from datetime import datetime
from typing import Optional

from app.core.config import settings
from app.services.data_processor import DataProcessor

router = APIRouter()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post("/csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload and process a CSV file containing CRM data
    """
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )

    # Check file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.1f}MB"
        )

    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_ext}")

    try:
        # Save file
        with open(file_path, "wb") as f:
            f.write(contents)

        # Process file based on type
        if file_ext == ".csv":
            df = pd.read_csv(file_path)
        elif file_ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        elif file_ext == ".json":
            df = pd.read_json(file_path)

        # Get basic statistics
        processor = DataProcessor()
        stats = processor.get_basic_stats(df)
        
        # Detect CRM schema and calculate pipeline metrics
        schema = processor.detect_crm_schema(df)
        if schema:
            # Clean data based on detected schema
            df_clean = processor.clean_data(df, schema)
            # Calculate pipeline-specific metrics
            pipeline_metrics = processor.calculate_pipeline_metrics(df_clean, schema)
            # Merge pipeline metrics into stats
            stats.update(pipeline_metrics)

        return {
            "file_id": file_id,
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "stats": stats,
            "upload_time": datetime.utcnow().isoformat(),
            "status": "success"
        }

    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{file_id}")
async def get_upload_status(file_id: str):
    """
    Get the status of an uploaded file
    """
    # Check if file exists
    file_patterns = [f"{file_id}{ext}" for ext in settings.ALLOWED_EXTENSIONS]
    file_path = None

    for pattern in file_patterns:
        potential_path = os.path.join(settings.UPLOAD_DIR, pattern)
        if os.path.exists(potential_path):
            file_path = potential_path
            break

    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")

    # Get file info
    file_stats = os.stat(file_path)

    return {
        "file_id": file_id,
        "exists": True,
        "size": file_stats.st_size,
        "created": datetime.fromtimestamp(file_stats.st_ctime).isoformat()
    }


@router.delete("/{file_id}")
async def delete_upload(file_id: str):
    """
    Delete an uploaded file
    """
    # Check if file exists and delete
    file_patterns = [f"{file_id}{ext}" for ext in settings.ALLOWED_EXTENSIONS]
    deleted = False

    for pattern in file_patterns:
        potential_path = os.path.join(settings.UPLOAD_DIR, pattern)
        if os.path.exists(potential_path):
            os.remove(potential_path)
            deleted = True
            break

    if not deleted:
        raise HTTPException(status_code=404, detail="File not found")

    return {"status": "deleted", "file_id": file_id}