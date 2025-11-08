"""
Base Agent class for DealIQ multi-agent system using Claude Agents SDK
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, AsyncIterator
import asyncio
from claude_agent_sdk import ClaudeSDKClient

from app.core.config import settings


class BaseAgent(ABC):
    """Base class for all DealIQ agents using Claude SDK with continuous conversations"""

    def __init__(self, name: str, description: str, tools: Optional[List] = None):
        self.name = name
        self.description = description
        self.custom_tools = tools or []
        self.session = None
        self.client = None

        # Configuration for Claude SDK
        self.sdk_options = {
            "api_key": settings.ANTHROPIC_API_KEY,
            "model": settings.CLAUDE_MODEL,
            "max_turns": 10,
            "system_prompt": {
                "type": "preset",
                "preset": "claude_code",
                "append": f"""You are {name}, a specialized agent for {description}.

Your role is to analyze sales/CRM data and provide actionable insights for sales teams.
Focus on being specific, data-driven, and providing clear recommendations.
When analyzing data, look for patterns, anomalies, trends, and opportunities."""
            }
        }

        # Add custom tools if provided
        if self.custom_tools:
            self.sdk_options["tools"] = self.custom_tools

    async def __aenter__(self):
        """Enter async context manager - initialize SDK client"""
        self.client = ClaudeSDKClient(self.sdk_options)
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager - cleanup SDK client"""
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    @abstractmethod
    async def process(self, data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process data and return results - to be implemented by subclasses"""
        pass

    async def query_continuous(self, prompt: str, context: Optional[Dict] = None) -> AsyncIterator[Dict[str, Any]]:
        """Execute a query in continuous conversation mode"""
        if not self.client:
            raise RuntimeError("Agent must be used within async context manager")

        try:
            # Build the full prompt with context
            full_prompt = self._build_prompt(prompt, context)

            # Send query to Claude
            await self.client.query(full_prompt)

            # Stream responses
            async for message in self.client.receive_response():
                yield self._format_message(message)

        except Exception as e:
            print(f"Error in continuous query: {e}")
            yield {
                "type": "error",
                "content": str(e)
            }

    async def query_single(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Execute a single query and return the complete response"""
        if not self.client:
            # Use temporary client for single query
            async with ClaudeSDKClient(self.sdk_options) as temp_client:
                full_prompt = self._build_prompt(prompt, context)
                await temp_client.query(full_prompt)

                result = ""
                async for message in temp_client.receive_response():
                    formatted = self._format_message(message)
                    if formatted.get("type") == "assistant":
                        result += formatted.get("content", "")

                return result or "No response generated"
        else:
            # Use existing client
            full_prompt = self._build_prompt(prompt, context)
            await self.client.query(full_prompt)

            result = ""
            async for message in self.client.receive_response():
                formatted = self._format_message(message)
                if formatted.get("type") == "assistant":
                    result += formatted.get("content", "")

            return result or "No response generated"

    async def think(self, prompt: str, context: Optional[str] = None) -> str:
        """Use Claude to process complex reasoning tasks (compatibility method)"""
        return await self.query_single(prompt, {"context": context} if context else None)

    def _build_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Build a complete prompt with context"""
        full_prompt = prompt

        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            full_prompt = f"Context:\n{context_str}\n\nTask:\n{prompt}"

        return full_prompt

    def _format_message(self, message) -> Dict[str, Any]:
        """Format SDK message to consistent structure"""
        # Handle different message types from SDK
        if hasattr(message, '__dict__'):
            msg_dict = message.__dict__
        elif isinstance(message, dict):
            msg_dict = message
        else:
            msg_dict = {"content": str(message)}

        # Extract type and content
        msg_type = msg_dict.get("type", "assistant")
        content = msg_dict.get("content", msg_dict.get("text", ""))

        return {
            "type": msg_type,
            "content": content,
            "raw": msg_dict
        }

    async def collaborate(self, other_agent: 'BaseAgent', data: Any) -> Dict[str, Any]:
        """Collaborate with another agent"""
        # Send data to other agent and get results
        result = await other_agent.process(data, context={"from_agent": self.name})
        return result

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "status": "active" if self.client else "ready",
            "has_session": self.client is not None,
            "tools": len(self.custom_tools) if self.custom_tools else 0
        }


class ContinuousAgent(BaseAgent):
    """Agent with built-in continuous conversation support"""

    def __init__(self, name: str, description: str, tools: Optional[List] = None):
        super().__init__(name, description, tools)
        self.conversation_history = []

    async def process(self, data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process data with conversation history maintained"""
        # Store the request
        self.conversation_history.append({
            "role": "user",
            "data": data,
            "context": context
        })

        # Process using continuous conversation
        response = await self.query_single(str(data), context)

        # Store the response
        self.conversation_history.append({
            "role": "assistant",
            "response": response
        })

        return {
            "status": "success",
            "response": response,
            "conversation_length": len(self.conversation_history)
        }

    async def follow_up(self, prompt: str) -> str:
        """Send a follow-up query in the same conversation context"""
        if not self.client:
            raise RuntimeError("No active conversation. Use within async context.")

        # This will use the existing conversation context
        await self.client.query(prompt)

        result = ""
        async for message in self.client.receive_response():
            formatted = self._format_message(message)
            if formatted.get("type") == "assistant":
                result += formatted.get("content", "")

        return result

    def get_conversation_history(self) -> List[Dict]:
        """Get the full conversation history"""
        return self.conversation_history


class AgentPool:
    """Manages a pool of agents for parallel processing"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.active_sessions: Dict[str, ClaudeSDKClient] = {}

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
                # Each agent processes independently
                async_tasks.append(self._process_with_agent(agent, data, context))

        results = await asyncio.gather(*async_tasks)
        return results

    async def _process_with_agent(self, agent: BaseAgent, data: Any, context: Optional[Dict]) -> Dict[str, Any]:
        """Process data with a specific agent in its own context"""
        async with agent:
            return await agent.process(data, context)

    async def start_continuous_session(self, agent_name: str) -> bool:
        """Start a continuous session for an agent"""
        if agent_name in self.agents:
            agent = self.agents[agent_name]
            await agent.__aenter__()
            self.active_sessions[agent_name] = agent
            return True
        return False

    async def end_continuous_session(self, agent_name: str) -> bool:
        """End a continuous session for an agent"""
        if agent_name in self.active_sessions:
            agent = self.active_sessions[agent_name]
            await agent.__aexit__(None, None, None)
            del self.active_sessions[agent_name]
            return True
        return False

    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            agent_name: agent.get_status()
            for agent_name, agent in self.agents.items()
        }

    def get_active_sessions(self) -> List[str]:
        """Get list of agents with active sessions"""
        return list(self.active_sessions.keys())