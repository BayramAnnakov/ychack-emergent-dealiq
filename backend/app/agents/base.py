"""
Base Agent class for DealIQ multi-agent system using Claude Agents SDK
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, AsyncIterator
import asyncio
import os
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, TextBlock, ResultMessage

from app.core.config import settings


class BaseAgent(ABC):
    """Base class for all DealIQ agents using Claude SDK with continuous conversations"""

    def __init__(self, name: str, description: str, tools: Optional[List] = None):
        self.name = name
        self.description = description
        self.custom_tools = tools or []
        self.session = None
        self.client = None

        # Ensure API key is set in environment for SDK
        os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY

        # Create agent-specific system prompt
        system_prompt = f"""You are {name}, a specialized agent for {description}.

Your role is to analyze sales/CRM data and provide actionable insights for sales teams.
Focus on being specific, data-driven, and providing clear recommendations.
When analyzing data, look for patterns, anomalies, trends, and opportunities."""

        # Create ClaudeAgentOptions with proper configuration
        self.options = ClaudeAgentOptions(
            system_prompt=system_prompt,
            model="sonnet",  # SDK expects "sonnet", "haiku", or "opus"
            max_turns=15,  # Increased to allow more comprehensive analysis
            permission_mode="default",  # Provides complete analysis with non-root appuser
            allowed_tools=self.custom_tools if self.custom_tools else [],
            # continue_conversation=True,  # REMOVED - causes hanging issues
        )

    async def __aenter__(self):
        """Enter async context manager - initialize SDK client"""
        # ClaudeSDKClient with options parameter
        self.client = ClaudeSDKClient(options=self.options)
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
            # Use temporary client for single query with the same options
            async with ClaudeSDKClient(options=self.options) as temp_client:
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
        # Simple prompt building - agent context is already in system_prompt
        full_prompt = prompt

        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            full_prompt = f"Context:\n{context_str}\n\nTask:\n{prompt}"

        return full_prompt

    def _format_message(self, message) -> Dict[str, Any]:
        """Format SDK message to consistent structure"""
        # Handle AssistantMessage type
        if isinstance(message, AssistantMessage):
            content = ""
            for block in message.content:
                if isinstance(block, TextBlock):
                    content += block.text
                elif hasattr(block, 'text'):
                    content += str(block.text)

            return {
                "type": "assistant",
                "content": content,
                "raw": message
            }

        # Handle ResultMessage type
        elif isinstance(message, ResultMessage):
            return {
                "type": "result",
                "content": getattr(message, 'result', ''),
                "duration_ms": getattr(message, 'duration_ms', None),
                "cost": getattr(message, 'total_cost_usd', None),
                "raw": message
            }

        # Handle other message types (SystemMessage, etc.)
        else:
            # Try to extract content from various possible attributes
            content = ""
            if hasattr(message, 'content'):
                content = str(message.content)
            elif hasattr(message, 'text'):
                content = str(message.text)
            elif hasattr(message, 'data'):
                content = str(message.data)

            return {
                "type": getattr(message, 'subtype', 'unknown'),
                "content": content,
                "raw": message
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