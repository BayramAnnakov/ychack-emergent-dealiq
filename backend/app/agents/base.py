"""
Base Agent class for DealIQ multi-agent system using Claude Agents SDK
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, AsyncIterator
import asyncio
import time
import os
from claude_agent_sdk import Agent, query, Tool
from anthropic import AsyncAnthropic

from app.core.config import settings


class BaseAgent(ABC):
    """Base class for all DealIQ agents using Claude Agents SDK"""

    def __init__(self, name: str, description: str, tools: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.allowed_tools = tools or []
        self.session_id = None

        # Fallback client for direct API calls if needed
        self.client = None
        if settings.ANTHROPIC_API_KEY:
            self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

        # Agent configuration for subagents
        self.agent_config = {
            "description": description,
            "prompt": f"You are {name}, a specialized agent for {description}. Analyze data and provide actionable insights for sales teams.",
            "tools": self.allowed_tools,
            "model": settings.CLAUDE_MODEL
        }

    @abstractmethod
    async def process(self, data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process data and return results"""
        pass

    async def stream_query(self, prompt: str, context: Optional[Dict] = None) -> AsyncIterator[Dict[str, Any]]:
        """Execute a streaming query using Claude SDK"""
        try:
            # Build the full prompt with context
            full_prompt = self._build_prompt(prompt, context)

            # Generate messages for streaming mode
            async def generate_messages():
                yield {
                    "type": "user",
                    "message": {
                        "role": "user",
                        "content": full_prompt
                    }
                }

            # Stream the query with agent configuration
            options = {
                "maxTurns": 10,
                "allowedTools": self.allowed_tools,
                "systemPrompt": {
                    "type": "preset",
                    "preset": "claude_code",
                    "append": f"You are {self.name}, a specialized agent for {self.description}."
                }
            }

            # Use the query function from SDK
            async for message in query(prompt=generate_messages(), options=options):
                # Capture session ID for potential resumption
                if message.get("type") == "system" and "session_id" in message:
                    self.session_id = message["session_id"]

                yield message

        except Exception as e:
            print(f"Error in streaming query: {e}")
            # Fallback to simple response
            yield {
                "type": "assistant",
                "content": self._fallback_processing(prompt)
            }

    async def single_query(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Execute a single query (non-streaming) using Claude SDK"""
        try:
            # Build the full prompt
            full_prompt = self._build_prompt(prompt, context)

            options = {
                "maxTurns": 1,
                "allowedTools": self.allowed_tools,
                "systemPrompt": {
                    "type": "preset",
                    "preset": "claude_code",
                    "append": f"You are {self.name}, a specialized agent for {self.description}."
                }
            }

            # Execute single query
            result = ""
            async for message in query(prompt=full_prompt, options=options):
                if message.get("type") == "assistant":
                    result += str(message.get("content", ""))

            return result if result else self._fallback_processing(prompt)

        except Exception as e:
            print(f"Error in single query: {e}")
            return self._fallback_processing(prompt)

    async def think(self, prompt: str, context: Optional[str] = None) -> str:
        """Use Claude to process complex reasoning tasks using SDK streaming"""
        # Use single_query which already implements proper Claude SDK
        return await self.single_query(prompt, {"context": context} if context else None)

    def _build_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Build a complete prompt with context"""
        full_prompt = prompt

        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            full_prompt = f"Context:\n{context_str}\n\nTask:\n{prompt}"

        return full_prompt

    def _fallback_processing(self, prompt: str) -> str:
        """Fallback processing when Claude API is not available"""
        # Basic rule-based processing as fallback
        return f"Processed by {self.name}: {prompt[:100]}..."

    async def collaborate(self, other_agent: 'BaseAgent', data: Any) -> Dict[str, Any]:
        """Collaborate with another agent"""
        # Send data to other agent and get results
        result = await other_agent.process(data, context={"from_agent": self.name})
        return result

    async def resume_session(self, prompt: str, session_id: str, fork: bool = False) -> AsyncIterator[Dict[str, Any]]:
        """Resume a previous session"""
        try:
            options = {
                "resume": session_id,
                "forkSession": fork,
                "maxTurns": 10,
                "allowedTools": self.allowed_tools
            }

            async for message in query(prompt=prompt, options=options):
                yield message

        except Exception as e:
            print(f"Error resuming session: {e}")
            yield {
                "type": "error",
                "content": f"Failed to resume session: {str(e)}"
            }

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "status": "ready",
            "has_claude": self.client is not None,
            "session_id": self.session_id,
            "tools": self.allowed_tools
        }


class AgentPool:
    """Manages a pool of agents for parallel processing"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        """Register an agent in the pool"""
        self.agents[agent.name] = agent

    async def process_parallel(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple tasks in parallel using different agents"""
        async_tasks = []

        for task in tasks:
            agent_name = task.get("agent")
            data = task.get("data")
            context = task.get("context")

            if agent_name in self.agents:
                agent = self.agents[agent_name]
                async_tasks.append(agent.process(data, context))

        results = await asyncio.gather(*async_tasks)
        return results

    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            agent_name: agent.get_status()
            for agent_name, agent in self.agents.items()
        }

    def get_agents_config(self) -> Dict[str, Dict[str, Any]]:
        """Get configuration for all agents (for subagent system)"""
        return {
            agent.name: agent.agent_config
            for agent in self.agents.values()
        }