"""
Wrapper file for supervisor compatibility
Imports the FastAPI app from app.main
"""
from app.main import app

__all__ = ['app']
