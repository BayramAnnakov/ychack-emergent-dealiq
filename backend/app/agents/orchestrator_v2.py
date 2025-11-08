"""
DealIQ Orchestrator using Claude SDK with Subagents
This is the main coordinator that uses SDK subagents for multi-agent processing
"""
import os
from typing import Dict, Any, Optional, List, AsyncIterator
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage,
    AgentDefinition
)

from app.core.config import settings


class DealIQOrchestrator:
    """Main orchestrator that coordinates multiple subagents for CRM intelligence"""

    def __init__(self):
        # Ensure API key is set
        os.environ["ANTHROPIC_API_KEY"] = settings.ANTHROPIC_API_KEY

        # Define all DealIQ subagents using AgentDefinition
        self.subagents = {
            'data-ingestion': AgentDefinition(
                description='CRM data parsing and validation expert. Use for initial data processing, cleaning, and structure detection.',
                prompt="""You are a data ingestion specialist for CRM/sales data.

Your responsibilities:
- Parse and validate incoming CRM data
- Detect data structure and schema
- Clean and standardize data fields
- Identify data quality issues
- Extract key entities (deals, contacts, companies)

Always provide structured output with clear data insights.""",
                tools=['Read', 'Grep', 'Glob'],
                model='sonnet'
            ),

            'analytics': AgentDefinition(
                description='Sales analytics expert. Use for statistical analysis, metrics calculation, and trend detection.',
                prompt="""You are a sales analytics specialist focused on CRM data analysis.

Your expertise includes:
- Pipeline analysis and metrics
- Win rate calculations
- Sales cycle analysis
- Revenue forecasting
- Trend identification
- Cohort analysis

Provide data-driven insights with specific metrics and percentages.""",
                tools=['Read', 'Grep'],
                model='sonnet'
            ),

            'predictive': AgentDefinition(
                description='Predictive modeling expert. Use for forecasting, risk assessment, and outcome prediction.',
                prompt="""You are a predictive analytics specialist for sales data.

Focus on:
- Deal scoring and probability calculations
- Revenue forecasting
- Churn prediction
- Sales cycle prediction
- Risk assessment
- Opportunity identification

Provide confidence levels with your predictions.""",
                tools=['Read', 'Grep'],
                model='sonnet'
            ),

            'insight': AgentDefinition(
                description='Business insight generator. Use for actionable recommendations and strategic analysis.',
                prompt="""You are a business insight specialist who transforms data into actionable intelligence.

Your role:
- Generate actionable recommendations
- Identify improvement opportunities
- Highlight critical issues
- Suggest optimization strategies
- Provide competitive insights

Always prioritize insights by impact and feasibility.""",
                tools=['Read', 'Grep'],
                model='sonnet'
            ),

            'hypothesis': AgentDefinition(
                description='Hypothesis testing expert. Use for validating assumptions and testing business theories.',
                prompt="""You are a hypothesis testing specialist for sales and business data.

Your approach:
- Formulate testable hypotheses
- Design validation strategies
- Analyze statistical significance
- Identify correlation vs causation
- Test assumptions
- Provide evidence-based conclusions

Be rigorous in your statistical approach.""",
                tools=['Read', 'Grep'],
                model='sonnet'
            )
        }

        # Create main orchestrator prompt
        self.system_prompt = """You are the DealIQ Orchestrator, coordinating multiple specialized agents to provide comprehensive CRM intelligence.

Your role is to:
1. Analyze incoming CRM/sales data requests
2. Coordinate the appropriate subagents for analysis
3. Synthesize their outputs into cohesive insights
4. Provide actionable recommendations for sales teams

Available subagents:
- data-ingestion: For data parsing and validation
- analytics: For statistical analysis and metrics
- predictive: For forecasting and predictions
- insight: For actionable recommendations
- hypothesis: For testing business assumptions

Coordinate these agents effectively to provide comprehensive analysis."""

        # Create options with subagents
        self.options = ClaudeAgentOptions(
            system_prompt=self.system_prompt,
            model="sonnet",  # SDK expects "sonnet", "haiku", or "opus"
            max_turns=15,
            permission_mode="bypassPermissions",  # Use valid permission mode
            # agents=self.subagents,
            # continue_conversation=True
        )

    async def analyze(self, data: Dict[str, Any], analysis_type: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
        """
        Analyze CRM data using multi-agent coordination

        Args:
            data: The CRM data to analyze
            analysis_type: Optional specific type of analysis requested

        Yields:
            Analysis results as they become available
        """
        # Build the analysis prompt
        prompt = self._build_analysis_prompt(data, analysis_type)

        # Execute analysis with subagents
        async with ClaudeSDKClient(options=self.options) as client:
            await client.query(prompt)

            async for message in client.receive_response():
                formatted = self._format_message(message)
                if formatted:
                    yield formatted

    async def analyze_complete(self, data: Dict[str, Any], analysis_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze CRM data and return complete results

        Args:
            data: The CRM data to analyze
            analysis_type: Optional specific type of analysis requested

        Returns:
            Complete analysis results
        """
        results = {
            "status": "processing",
            "analysis": "",
            "metrics": {},
            "insights": [],
            "recommendations": []
        }

        async for update in self.analyze(data, analysis_type):
            if update.get("type") == "assistant":
                results["analysis"] += update.get("content", "")
            elif update.get("type") == "result":
                results["status"] = "success"
                results["metrics"]["duration_ms"] = update.get("duration_ms")
                results["metrics"]["cost_usd"] = update.get("cost")

        return results

    async def process_pipeline(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Specialized method for pipeline analysis"""
        return await self.analyze_complete(
            data=pipeline_data,
            analysis_type="pipeline_analysis"
        )

    async def forecast_revenue(self, historical_data: Dict[str, Any], period: str = "Q2") -> Dict[str, Any]:
        """Specialized method for revenue forecasting"""
        return await self.analyze_complete(
            data=historical_data,
            analysis_type=f"revenue_forecast_{period}"
        )

    async def score_deals(self, deals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Score and prioritize deals"""
        return await self.analyze_complete(
            data={"deals": deals},
            analysis_type="deal_scoring"
        )

    async def identify_risks(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify risks and opportunities"""
        return await self.analyze_complete(
            data=data,
            analysis_type="risk_assessment"
        )

    def _build_analysis_prompt(self, data: Dict[str, Any], analysis_type: Optional[str] = None) -> str:
        """Build the analysis prompt for the orchestrator"""
        import json

        # Format data
        try:
            data_str = json.dumps(data, indent=2, default=str)
        except:
            data_str = str(data)

        # Build base prompt
        prompt = f"""Analyze this CRM/sales data using the appropriate subagents:

{data_str}

"""

        # Add specific analysis instructions if provided
        if analysis_type:
            analysis_instructions = {
                "pipeline_analysis": """Focus on:
- Pipeline health metrics
- Stage conversion rates
- Bottlenecks and issues
- Improvement opportunities""",

                "deal_scoring": """Focus on:
- Score each deal (0-100)
- Identify high-priority opportunities
- Risk factors for each deal
- Recommended actions per deal""",

                "risk_assessment": """Focus on:
- Identify key risks
- Quantify risk impact
- Suggest mitigation strategies
- Highlight opportunities""",
            }

            if analysis_type in analysis_instructions:
                prompt += f"\nSpecific analysis requested:\n{analysis_instructions[analysis_type]}"
            elif analysis_type.startswith("revenue_forecast"):
                period = analysis_type.split("_")[-1]
                prompt += f"\nProvide revenue forecast for {period} with confidence intervals."

        prompt += """

Coordinate the relevant subagents to provide:
1. Data validation and quality assessment
2. Statistical analysis and metrics
3. Predictions and forecasts
4. Actionable insights and recommendations
5. Risk assessment and opportunities

Synthesize all agent outputs into a comprehensive analysis."""

        return prompt

    def _format_message(self, message) -> Optional[Dict[str, Any]]:
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
                "content": content
            }

        # Handle ResultMessage type
        elif isinstance(message, ResultMessage):
            return {
                "type": "result",
                "content": getattr(message, 'result', ''),
                "duration_ms": getattr(message, 'duration_ms', None),
                "cost": getattr(message, 'total_cost_usd', None)
            }

        # Skip system messages
        elif hasattr(message, 'subtype') and message.subtype == 'init':
            return None

        return None


# Convenience function for quick analysis
async def analyze_crm_data(data: Dict[str, Any], analysis_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Quick function to analyze CRM data using the orchestrator

    Args:
        data: CRM data to analyze
        analysis_type: Optional specific analysis type

    Returns:
        Analysis results
    """
    orchestrator = DealIQOrchestrator()
    return await orchestrator.analyze_complete(data, analysis_type)