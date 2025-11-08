"""
Continuous conversation endpoints for multi-turn agent interactions
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import asyncio
import uuid

from app.agents.data_ingestion import DataIngestionAgent
from app.agents.analytics import AnalyticsAgent
from app.agents.predictive import PredictiveAgent
from app.agents.insight import InsightAgent
from app.agents.hypothesis import HypothesisAgent
from app.core.config import settings

router = APIRouter()

# Store active agent sessions
active_sessions: Dict[str, Any] = {}


class SessionRequest(BaseModel):
    """Model for session creation request"""
    agent_type: str
    initial_data: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    """Model for continuous query request"""
    session_id: str
    prompt: str
    context: Optional[Dict[str, Any]] = None


@router.post("/session/start")
async def start_continuous_session(request: SessionRequest):
    """
    Start a continuous conversation session with an agent
    """
    # Create agent based on type
    agent_map = {
        "ingestion": DataIngestionAgent,
        "analytics": AnalyticsAgent,
        "predictive": PredictiveAgent,
        "insight": InsightAgent,
        "hypothesis": HypothesisAgent
    }

    if request.agent_type not in agent_map:
        raise HTTPException(status_code=400, detail=f"Unknown agent type: {request.agent_type}")

    try:
        # Create session ID
        session_id = str(uuid.uuid4())

        # Initialize agent
        agent_class = agent_map[request.agent_type]
        agent = agent_class()

        # Start continuous session
        await agent.__aenter__()

        # Store session
        active_sessions[session_id] = {
            "agent": agent,
            "type": request.agent_type,
            "created_at": asyncio.get_event_loop().time()
        }

        # Process initial data if provided
        initial_response = None
        if request.initial_data:
            initial_response = await agent.process(request.initial_data)

        return {
            "session_id": session_id,
            "agent_type": request.agent_type,
            "status": "active",
            "initial_response": initial_response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/query")
async def query_continuous_session(request: QueryRequest):
    """
    Send a follow-up query in an existing continuous session
    """
    if request.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        session = active_sessions[request.session_id]
        agent = session["agent"]

        # Send follow-up query
        response = await agent.follow_up(request.prompt)

        return {
            "session_id": request.session_id,
            "response": response,
            "conversation_length": len(agent.get_conversation_history())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/history")
async def get_session_history(session_id: str):
    """
    Get the conversation history for a session
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]
    agent = session["agent"]

    return {
        "session_id": session_id,
        "agent_type": session["type"],
        "history": agent.get_conversation_history()
    }


@router.delete("/session/{session_id}")
async def end_continuous_session(session_id: str):
    """
    End a continuous conversation session
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        session = active_sessions[session_id]
        agent = session["agent"]

        # End the session
        await agent.__aexit__(None, None, None)

        # Remove from active sessions
        del active_sessions[session_id]

        return {
            "session_id": session_id,
            "status": "closed"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def list_active_sessions():
    """
    List all active continuous sessions
    """
    sessions = []
    for session_id, session_data in active_sessions.items():
        sessions.append({
            "session_id": session_id,
            "agent_type": session_data["type"],
            "created_at": session_data["created_at"],
            "conversation_length": len(session_data["agent"].get_conversation_history())
        })

    return {
        "active_sessions": sessions,
        "total": len(sessions)
    }


@router.websocket("/session/stream")
async def continuous_stream_session(websocket: WebSocket):
    """
    WebSocket endpoint for streaming continuous conversations
    """
    await websocket.accept()
    session_id = None
    agent = None

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "start":
                # Start new session
                agent_type = message.get("agent_type", "ingestion")

                # Create agent
                if agent_type == "ingestion":
                    agent = DataIngestionAgent()
                elif agent_type == "analytics":
                    agent = AnalyticsAgent()
                else:
                    agent = DataIngestionAgent()  # Default

                # Start session
                await agent.__aenter__()
                session_id = str(uuid.uuid4())

                await websocket.send_json({
                    "type": "session_started",
                    "session_id": session_id
                })

            elif message.get("type") == "query" and agent:
                # Process query
                prompt = message.get("prompt")
                context = message.get("context")

                # Stream responses
                async for response in agent.query_continuous(prompt, context):
                    await websocket.send_json({
                        "type": "response",
                        "data": response
                    })

                # Send completion signal
                await websocket.send_json({
                    "type": "complete"
                })

            elif message.get("type") == "end" and agent:
                # End session
                await agent.__aexit__(None, None, None)
                await websocket.send_json({
                    "type": "session_ended"
                })
                break

    except WebSocketDisconnect:
        print(f"Client disconnected from session {session_id}")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        # Cleanup
        if agent:
            try:
                await agent.__aexit__(None, None, None)
            except:
                pass
        await websocket.close()


# Cleanup function for old sessions
async def cleanup_old_sessions(max_age_seconds: int = 3600):
    """
    Clean up sessions older than max_age_seconds
    """
    current_time = asyncio.get_event_loop().time()
    sessions_to_remove = []

    for session_id, session_data in active_sessions.items():
        age = current_time - session_data["created_at"]
        if age > max_age_seconds:
            sessions_to_remove.append(session_id)

    for session_id in sessions_to_remove:
        try:
            agent = active_sessions[session_id]["agent"]
            await agent.__aexit__(None, None, None)
            del active_sessions[session_id]
            print(f"Cleaned up old session: {session_id}")
        except Exception as e:
            print(f"Error cleaning up session {session_id}: {e}")