"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check for deployments"""
    # TODO: Add checks for database, redis, etc.
    return {
        "status": "ready",
        "services": {
            "api": "ready",
            "agents": "ready"
        }
    }