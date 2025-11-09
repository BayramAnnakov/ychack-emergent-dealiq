"""
DealIQ Orchestrator with Streaming Support
Simplified version without subagents for better debugging and streaming
"""
import os
import asyncio
from typing import Dict, Any, Optional, List, AsyncIterator
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    UserMessage,
    AssistantMessage,
    TextBlock,
    ThinkingBlock,
    ResultMessage,
    SystemMessage,
    ToolUseBlock,
    ToolResultBlock
)
import json

from app.core.config import settings


class StreamingOrchestrator:
    """Orchestrator with full streaming and debug support"""

    def __init__(self, verbose: bool = True):
        # Ensure API key is set
        os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY
        self.verbose = verbose

        # System prompt for the orchestrator
        self.system_prompt = """You are DealIQ, an AI-powered CRM intelligence platform.

Your role is to analyze sales and CRM data to provide:
1. Data validation and quality assessment
2. Statistical analysis and metrics
3. Predictions and forecasts
4. Actionable insights and recommendations
5. Risk assessment and opportunities

Be specific, data-driven, and provide clear recommendations.
Format your responses with clear sections and bullet points."""

        # Create options without subagents
        # Set cwd to backend directory (where data/uploads is located)
        # From: backend/app/agents/orchestrator_streaming.py
        # Explicit path for Emergent environment with appuser
        backend_dir = "/app/backend"  # Explicit path that appuser can access

        # Verify path
        if self.verbose:
            print(f"Backend dir set to: {backend_dir}")
            print(f"Upload dir will be: {os.path.join(backend_dir, 'data/uploads')}")

        self.options = ClaudeAgentOptions(
            system_prompt=self.system_prompt,
            model="sonnet",  # SDK expects "sonnet", "haiku", or "opus"
            max_turns=15,  # Increased for comprehensive analysis
            permission_mode="default",  # Works with non-root user (appuser)
            cwd=backend_dir,  # Set to backend dir where data/uploads is
            cli_path="/home/appuser/node_modules/.bin/claude"  # Path to claude CLI for appuser
            # continue_conversation=True
        )

    async def analyze_streaming(
        self,
        data: Dict[str, Any],
        analysis_type: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream analysis results as they come in

        Args:
            data: The CRM data to analyze
            analysis_type: Optional specific type of analysis

        Yields:
            Streaming updates with type and content
        """
        if self.verbose:
            print("\n" + "="*60)
            print("🔍 STREAMING ANALYSIS STARTING")
            print("="*60)
            print(f"🤖 Model: {settings.CLAUDE_MODEL}")
            print(f"🔑 API Key: {settings.ANTHROPIC_API_KEY[:15]}...")

        # Build the analysis prompt
        prompt = self._build_analysis_prompt(data, analysis_type)


        if self.verbose:
            print(f"📝 Prompt prepared ({len(prompt)} chars)")
            print(f"📊 Data keys: {list(data.keys())}")
            print(f"🎯 Analysis type: {analysis_type or 'general'}")

        try:
            # Create client and send query
            if self.verbose:
                print("\n🤖 Initializing Claude SDK Client...")

            async with ClaudeSDKClient(options=self.options) as client:
                if self.verbose:
                    print("✅ Client initialized successfully")
                    print("📤 Sending query to Claude...")

                # Send the query
                await client.query(prompt)

                if self.verbose:
                    print("✅ Query sent, waiting for response...")
                    print("\n" + "-"*40)
                    print("STREAMING RESPONSE:")
                    print("-"*40)

                # Track message statistics
                message_count = 0
                total_content_length = 0
                start_time = asyncio.get_event_loop().time()

                # Stream responses - receive_response() gives us message-level streaming
                async for message in client.receive_response():
                    message_count += 1
                    current_time = asyncio.get_event_loop().time() - start_time
                    print(message)

                    # Debug: Show what message type we received
                    if self.verbose:
                        print(f"\n🔍 [{current_time:.1f}s] Received: {type(message).__name__}")

                    # Handle different message types
                    if isinstance(message, SystemMessage):
                        if self.verbose:
                            print(f"\n⚙️  [{current_time:.1f}s] System: {message.subtype}")
                        yield {
                            "type": "system",
                            "subtype": message.subtype,
                            "data": getattr(message, 'data', None)
                        }

                    elif isinstance(message, UserMessage):
                        # User message (echo of our query)
                        if self.verbose:
                            print(f"\n👤 [{current_time:.1f}s] User message received")
                        yield {
                            "type": "user",
                            "timestamp": current_time
                        }

                    elif isinstance(message, AssistantMessage):
                        # Process each content block separately for better streaming visibility
                        content = ""
                        tool_uses = []

                        for block in message.content:
                            if isinstance(block, TextBlock):
                                content += block.text
                                if self.verbose and block.text.strip():
                                    preview = block.text[:150] + "..." if len(block.text) > 150 else block.text
                                    print(f"\n💬 [{current_time:.1f}s] Claude says:")
                                    print(f"   {preview}")

                            elif isinstance(block, ThinkingBlock):
                                # Extended thinking (only in some models with extended thinking enabled)
                                thinking_text = block.thinking if hasattr(block, 'thinking') else str(block)
                                if self.verbose and thinking_text:
                                    preview = thinking_text[:150] + "..." if len(thinking_text) > 150 else thinking_text
                                    print(f"\n🧠 [{current_time:.1f}s] Claude thinking:")
                                    print(f"   {preview}")

                            elif isinstance(block, ToolUseBlock):
                                tool_uses.append({
                                    "name": block.name,
                                    "input": block.input
                                })
                                if self.verbose:
                                    print(f"\n🔧 [{current_time:.1f}s] Tool Use: {block.name}")
                                    if block.input:
                                        # Show snippet of input
                                        input_preview = str(block.input)[:100]
                                        print(f"   Input: {input_preview}...")

                            elif isinstance(block, ToolResultBlock):
                                if self.verbose:
                                    result_preview = str(block.content)[:100] if hasattr(block, 'content') else "completed"
                                    print(f"\n✅ [{current_time:.1f}s] Tool Result: {result_preview}...")

                        total_content_length += len(content)

                        # DEBUG: Check what attributes the message actually has
                        print(f"DEBUG ORCHESTRATOR: AssistantMessage attributes: {dir(message)}")
                        
                        # Extract usage if available
                        message_usage = None
                        message_id = None
                        
                        if hasattr(message, 'usage'):
                            message_usage = message.usage
                            print(f"DEBUG ORCHESTRATOR: Found usage attribute: {message_usage}")
                        
                        if hasattr(message, 'id'):
                            message_id = message.id
                            print(f"DEBUG ORCHESTRATOR: Found id attribute: {message_id}")

                        # Yield the message with usage data
                        yield {
                            "type": "assistant",
                            "content": content,
                            "tool_uses": tool_uses,
                            "message_number": message_count,
                            "timestamp": current_time,
                            "id": message_id,
                            "usage": message_usage
                        }

                    elif isinstance(message, ResultMessage):
                        if self.verbose:
                            print(f"\n✅ [{current_time:.1f}s] Final Result:")
                            print(f"   Duration: {getattr(message, 'duration_ms', 0)}ms")
                            print(f"   Cost: ${getattr(message, 'total_cost_usd', 0):.4f}")
                            print(f"   Status: {'Success' if not getattr(message, 'is_error', False) else 'Error'}")
                            print(f"   Turns: {getattr(message, 'num_turns', 0)}")

                        yield {
                            "type": "complete",
                            "duration_ms": getattr(message, 'duration_ms', 0),
                            "total_cost_usd": getattr(message, 'total_cost_usd', 0),
                            "is_error": getattr(message, 'is_error', False),
                            "num_turns": getattr(message, 'num_turns', 0),
                            "total_content": total_content_length,
                            "usage": getattr(message, 'usage', None)
                        }

                    else:
                        if self.verbose:
                            print(f"\n❓ [{current_time:.1f}s] Unknown message type: {type(message).__name__}")
                            print(f"   Message: {message}")

                if self.verbose:
                    print("\n" + "-"*40)
                    print(f"📊 STREAMING COMPLETE")
                    print(f"   Total messages: {message_count}")
                    print(f"   Total content: {total_content_length} chars")
                    print(f"   Total time: {current_time:.1f}s")
                    print("="*60 + "\n")

        except Exception as e:
            if self.verbose:
                print(f"\n❌ ERROR: {str(e)}")
                import traceback
                traceback.print_exc()

            yield {
                "type": "error",
                "error": str(e),
                "traceback": traceback.format_exc() if self.verbose else None
            }

    async def analyze_complete(
        self,
        data: Dict[str, Any],
        analysis_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get complete analysis (non-streaming)

        Returns:
            Complete analysis results
        """
        results = {
            "status": "processing",
            "content": "",
            "metrics": {},
            "messages": []
        }

        async for update in self.analyze_streaming(data, analysis_type):
            results["messages"].append(update)

            if update["type"] == "assistant":
                results["content"] += update["content"]
            elif update["type"] == "result":
                results["status"] = "success" if not update["is_error"] else "error"
                results["metrics"]["duration_ms"] = update["duration_ms"]
                results["metrics"]["cost_usd"] = update["cost_usd"]
            elif update["type"] == "error":
                results["status"] = "error"
                results["error"] = update["error"]

        return results

    async def analyze_file_streaming(
        self,
        file_path: str,
        analysis_type: Optional[str] = None,
        description: Optional[str] = None
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Analyze a CSV file by giving Claude the file path and letting it use Read tool

        Args:
            file_path: Path to the CSV file (relative to cwd or absolute)
            analysis_type: Optional specific type of analysis
            description: Optional description to guide the analysis

        Yields:
            Streaming updates with type and content
        """
        if self.verbose:
            print("\n" + "="*60)
            print("🔍 FILE-BASED STREAMING ANALYSIS")
            print("="*60)
            print(f"📂 File: {file_path}")
            print(f"🎯 Analysis type: {analysis_type or 'general'}")
            print(f"📝 Description: {description or 'N/A'}")

        # Build prompt that asks Claude to read the file
        prompt = f"""Please analyze the CRM data in the file: {file_path}

Use the Read tool to load the CSV file and analyze it.

"""

        # Add specific analysis instructions
        if analysis_type == "pipeline_analysis":
            prompt += """Focus your analysis on:
1. Pipeline health metrics and conversion rates
2. Bottlenecks and stage-specific issues
3. Velocity and cycle time analysis
4. Risk identification
5. Specific improvement recommendations"""

        elif analysis_type == "deal_scoring":
            prompt += """Score and prioritize each deal:
1. Assign a score (0-100) to each deal
2. Identify key risk factors
3. Highlight high-priority opportunities
4. Recommend specific actions per deal
5. Provide confidence levels"""

        elif analysis_type == "risk_assessment":
            prompt += """Perform comprehensive risk assessment:
1. Identify all major risks
2. Quantify potential impact
3. Assess probability of occurrence
4. Suggest mitigation strategies
5. Highlight hidden opportunities"""

        else:
            prompt += """Provide comprehensive analysis including:
1. Data quality and completeness assessment
2. Key metrics and statistics
3. Trends and patterns
4. Actionable insights
5. Prioritized recommendations"""

        if description:
            prompt += f"\n\nAdditional context: {description}"

        if self.verbose:
            print(f"\n📝 Prompt length: {len(prompt)} chars")

        try:
            # Create client and send query
            if self.verbose:
                print("\n🤖 Initializing Claude SDK Client...")

            async with ClaudeSDKClient(options=self.options) as client:
                if self.verbose:
                    print("✅ Client initialized successfully")
                    print("📤 Sending query to Claude...")

                # Send the query
                await client.query(prompt)

                if self.verbose:
                    print("✅ Query sent, Claude will read the file and analyze...")
                    print("\n" + "-"*40)
                    print("STREAMING RESPONSE:")
                    print("-"*40)

                # Track statistics
                message_count = 0
                total_content_length = 0
                start_time = asyncio.get_event_loop().time()

                # Stream responses - receive_response() gives us message-level streaming
                async for message in client.receive_response():
                    message_count += 1
                    current_time = asyncio.get_event_loop().time() - start_time

                    if self.verbose:
                        print(f"\n🔍 [{current_time:.1f}s] Received: {type(message).__name__}")

                    # Handle different message types (same as analyze_streaming)
                    if isinstance(message, SystemMessage):
                        if self.verbose:
                            print(f"\n⚙️  [{current_time:.1f}s] System: {message.subtype}")
                        yield {
                            "type": "system",
                            "subtype": message.subtype,
                            "data": getattr(message, 'data', None)
                        }

                    elif isinstance(message, UserMessage):
                        if self.verbose:
                            print(f"\n👤 [{current_time:.1f}s] User message received")
                        yield {
                            "type": "user",
                            "timestamp": current_time
                        }

                    elif isinstance(message, AssistantMessage):
                        content = ""
                        tool_uses = []

                        for block in message.content:
                            if isinstance(block, TextBlock):
                                content += block.text
                                if self.verbose and block.text.strip():
                                    preview = block.text[:150] + "..." if len(block.text) > 150 else block.text
                                    print(f"\n💬 [{current_time:.1f}s] Claude says:")
                                    print(f"   {preview}")

                            elif isinstance(block, ThinkingBlock):
                                thinking_text = block.thinking if hasattr(block, 'thinking') else str(block)
                                if self.verbose and thinking_text:
                                    preview = thinking_text[:150] + "..." if len(thinking_text) > 150 else thinking_text
                                    print(f"\n🧠 [{current_time:.1f}s] Claude thinking:")
                                    print(f"   {preview}")

                            elif isinstance(block, ToolUseBlock):
                                tool_uses.append({
                                    "name": block.name,
                                    "input": block.input
                                })
                                if self.verbose:
                                    print(f"\n🔧 [{current_time:.1f}s] Tool Use: {block.name}")
                                    if block.input:
                                        input_preview = str(block.input)[:100]
                                        print(f"   Input: {input_preview}...")

                            elif isinstance(block, ToolResultBlock):
                                if self.verbose:
                                    result_preview = str(block.content)[:100] if hasattr(block, 'content') else "completed"
                                    print(f"\n✅ [{current_time:.1f}s] Tool Result: {result_preview}...")

                        total_content_length += len(content)

                        yield {
                            "type": "assistant",
                            "content": content,
                            "tool_uses": tool_uses,
                            "message_number": message_count,
                            "timestamp": current_time
                        }

                    elif isinstance(message, ResultMessage):
                        if self.verbose:
                            print(f"\n✅ [{current_time:.1f}s] Final Result:")
                            print(f"   Duration: {getattr(message, 'duration_ms', 0)}ms")
                            print(f"   Cost: ${getattr(message, 'total_cost_usd', 0):.4f}")
                            print(f"   Status: {'Success' if not getattr(message, 'is_error', False) else 'Error'}")
                            print(f"   Turns: {getattr(message, 'num_turns', 0)}")

                        yield {
                            "type": "complete",
                            "duration_ms": getattr(message, 'duration_ms', 0),
                            "total_cost_usd": getattr(message, 'total_cost_usd', 0),
                            "is_error": getattr(message, 'is_error', False),
                            "num_turns": getattr(message, 'num_turns', 0),
                            "total_content": total_content_length,
                            "usage": getattr(message, 'usage', None)
                        }

                    else:
                        if self.verbose:
                            print(f"\n❓ [{current_time:.1f}s] Unknown message type: {type(message).__name__}")

                if self.verbose:
                    print("\n" + "-"*40)
                    print(f"📊 STREAMING COMPLETE")
                    print(f"   Total messages: {message_count}")
                    print(f"   Total content: {total_content_length} chars")
                    print(f"   Total time: {current_time:.1f}s")
                    print("="*60 + "\n")

        except Exception as e:
            if self.verbose:
                print(f"\n❌ ERROR: {str(e)}")
                import traceback
                traceback.print_exc()

            yield {
                "type": "error",
                "error": str(e),
                "traceback": traceback.format_exc() if self.verbose else None
            }

    def _build_analysis_prompt(self, data: Dict[str, Any], analysis_type: Optional[str] = None) -> str:
        """Build the analysis prompt"""
        # Format data as JSON
        try:
            data_str = json.dumps(data, indent=2, default=str)
        except:
            data_str = str(data)

        # Build base prompt
        prompt = f"""Analyze this CRM/sales data:

{data_str}

"""

        # Add specific analysis instructions
        if analysis_type == "pipeline_analysis":
            prompt += """Focus your analysis on:
1. Pipeline health metrics and conversion rates
2. Bottlenecks and stage-specific issues
3. Velocity and cycle time analysis
4. Risk identification
5. Specific improvement recommendations"""

        elif analysis_type == "deal_scoring":
            prompt += """Score and prioritize each deal:
1. Assign a score (0-100) to each deal
2. Identify key risk factors
3. Highlight high-priority opportunities
4. Recommend specific actions per deal
5. Provide confidence levels"""

        elif analysis_type == "risk_assessment":
            prompt += """Perform comprehensive risk assessment:
1. Identify all major risks
2. Quantify potential impact
3. Assess probability of occurrence
4. Suggest mitigation strategies
5. Highlight hidden opportunities"""

        elif analysis_type and "forecast" in analysis_type.lower():
            prompt += f"""Provide detailed revenue forecast:
1. Forecast for the requested period
2. Include confidence intervals
3. Identify key assumptions
4. Highlight influencing factors
5. Suggest actions to improve forecast"""

        else:
            prompt += """Provide comprehensive analysis including:
1. Data quality and completeness assessment
2. Key metrics and statistics
3. Trends and patterns
4. Actionable insights
5. Prioritized recommendations"""

        return prompt


async def test_streaming():
    """Test the streaming orchestrator"""
    print("🚀 Testing Streaming Orchestrator")

    # Create orchestrator
    orchestrator = StreamingOrchestrator(verbose=True)

    # Test data
    test_data = {
        "pipeline": {
            "leads": 100,
            "qualified": 50,
            "proposals": 20,
            "negotiations": 10,
            "closed_won": 5
        },
        "average_deal_size": 50000,
        "period": "Q1 2024"
    }

    # Run streaming analysis
    print("\n📊 Starting Pipeline Analysis...")
    async for update in orchestrator.analyze_streaming(test_data, "pipeline_analysis"):
        # Updates are already printed by verbose mode
        pass

    print("\n✅ Test complete!")


if __name__ == "__main__":
    # Run test
    asyncio.run(test_streaming())