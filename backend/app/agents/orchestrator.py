"""
Orchestrator Agent - Coordinates all other agents
"""
import asyncio
from typing import Dict, Any, Optional, List, Callable
import time
import json

from app.agents.base import BaseAgent, AgentPool
from app.agents.data_ingestion import DataIngestionAgent
from app.agents.analytics import AnalyticsAgent
from app.agents.predictive import PredictiveAgent
from app.agents.insight import InsightAgent
from app.agents.hypothesis import HypothesisAgent
from app.services.data_processor import DataProcessor


class OrchestratorAgent(BaseAgent):
    """Orchestrates and coordinates all other agents"""

    def __init__(self):
        super().__init__(
            name="OrchestratorAgent",
            description="Coordinates multi-agent workflows for CRM intelligence"
        )
        self.agent_pool = AgentPool()
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize and register all specialized agents"""
        self.agent_pool.register(DataIngestionAgent())
        self.agent_pool.register(AnalyticsAgent())
        self.agent_pool.register(PredictiveAgent())
        self.agent_pool.register(InsightAgent())
        self.agent_pool.register(HypothesisAgent())

    async def process(self, data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a request by orchestrating multiple agents"""
        start_time = time.time()

        # Determine which agents to involve based on the request
        query_type = context.get("query_type", "general") if context else "general"

        workflow = self._determine_workflow(query_type)
        results = await self._execute_workflow(workflow, data, context)

        return {
            "results": results,
            "workflow": workflow,
            "processing_time": time.time() - start_time
        }

    def _determine_workflow(self, query_type: str) -> List[str]:
        """Determine which agents to involve based on query type"""
        workflows = {
            "general": ["DataIngestionAgent", "AnalyticsAgent", "InsightAgent"],
            "prediction": ["DataIngestionAgent", "AnalyticsAgent", "PredictiveAgent"],
            "hypothesis": ["DataIngestionAgent", "HypothesisAgent", "InsightAgent"],
            "full_analysis": ["DataIngestionAgent", "AnalyticsAgent", "PredictiveAgent", "InsightAgent", "HypothesisAgent"]
        }

        return workflows.get(query_type, workflows["general"])

    async def _execute_workflow(self, workflow: List[str], data: Any, context: Optional[Dict]) -> Dict[str, Any]:
        """Execute a workflow of agents"""
        results = {}
        current_data = data

        for agent_name in workflow:
            if agent_name in self.agent_pool.agents:
                agent = self.agent_pool.agents[agent_name]

                # Pass previous results as context
                agent_context = context or {}
                agent_context["previous_results"] = results

                # Process with agent
                agent_result = await agent.process(current_data, agent_context)
                results[agent_name] = agent_result

                # Use output as input for next agent if applicable
                if "output_data" in agent_result:
                    current_data = agent_result["output_data"]

        return results

    async def process_query(self, file_id: str, query: str, insight_type: str = "general") -> Dict[str, Any]:
        """Process a natural language query on uploaded data"""
        start_time = time.time()

        try:
            # Load the data
            processor = DataProcessor()
            df = processor.load_file(file_id)

            # Determine workflow based on query
            workflow = await self._analyze_query(query)

            # Execute workflow
            context = {
                "query": query,
                "insight_type": insight_type,
                "file_id": file_id
            }

            results = await self._execute_workflow(workflow, df, context)

            # Generate final insights
            insights = await self._synthesize_results(results, query)

            return {
                "query": query,
                "insights": insights,
                "confidence": self._calculate_confidence(results),
                "processing_time": time.time() - start_time
            }

        except Exception as e:
            raise Exception(f"Error processing query: {str(e)}")

    async def _analyze_query(self, query: str) -> List[str]:
        """Analyze query to determine optimal workflow"""
        query_lower = query.lower()

        # Pattern matching for query type
        if any(word in query_lower for word in ["predict", "forecast", "will", "future"]):
            return ["DataIngestionAgent", "AnalyticsAgent", "PredictiveAgent", "InsightAgent"]
        elif any(word in query_lower for word in ["hypothesis", "test", "correlation", "relationship"]):
            return ["DataIngestionAgent", "HypothesisAgent", "InsightAgent"]
        elif any(word in query_lower for word in ["analyze", "insights", "summary"]):
            return ["DataIngestionAgent", "AnalyticsAgent", "InsightAgent"]
        else:
            return ["DataIngestionAgent", "AnalyticsAgent", "InsightAgent"]

    async def _synthesize_results(self, results: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """Synthesize results from multiple agents into coherent insights"""
        insights = []

        # Extract key insights from each agent
        for agent_name, result in results.items():
            if "insights" in result:
                for insight in result["insights"]:
                    insights.append({
                        "source": agent_name,
                        "type": insight.get("type", "general"),
                        "title": insight.get("title", "Insight"),
                        "description": insight.get("description", ""),
                        "confidence": insight.get("confidence", 0.5),
                        "data": insight.get("data", {})
                    })

        # Sort by confidence
        insights.sort(key=lambda x: x["confidence"], reverse=True)

        return insights[:10]  # Return top 10 insights

    def _calculate_confidence(self, results: Dict[str, Any]) -> float:
        """Calculate overall confidence based on agent results"""
        confidences = []

        for agent_name, result in results.items():
            if "confidence" in result:
                confidences.append(result["confidence"])

        if confidences:
            return sum(confidences) / len(confidences)
        return 0.5

    async def generate_quick_insights(self, file_id: str) -> List[Dict[str, Any]]:
        """Generate quick insights without specific query"""
        # Use a general workflow
        workflow = ["DataIngestionAgent", "AnalyticsAgent", "InsightAgent"]

        processor = DataProcessor()
        df = processor.load_file(file_id)

        context = {
            "mode": "quick_insights",
            "file_id": file_id
        }

        results = await self._execute_workflow(workflow, df, context)
        return await self._synthesize_results(results, "general analysis")

    async def test_hypothesis(self, file_id: str, hypothesis: str) -> Dict[str, Any]:
        """Test a specific hypothesis"""
        workflow = ["DataIngestionAgent", "HypothesisAgent", "InsightAgent"]

        processor = DataProcessor()
        df = processor.load_file(file_id)

        context = {
            "hypothesis": hypothesis,
            "file_id": file_id
        }

        results = await self._execute_workflow(workflow, df, context)

        # Extract hypothesis test results
        hypothesis_results = results.get("HypothesisAgent", {})

        return {
            "hypothesis": hypothesis,
            "result": hypothesis_results.get("result", "inconclusive"),
            "confidence": hypothesis_results.get("confidence", 0.5),
            "evidence": hypothesis_results.get("evidence", []),
            "recommendation": hypothesis_results.get("recommendation", "")
        }

    async def generate_predictions(self, file_id: str, prediction_type: str, target: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate predictions based on data"""
        workflow = ["DataIngestionAgent", "AnalyticsAgent", "PredictiveAgent"]

        processor = DataProcessor()
        df = processor.load_file(file_id)

        context = {
            "prediction_type": prediction_type,
            "target": target,
            "file_id": file_id
        }

        results = await self._execute_workflow(workflow, df, context)

        # Extract predictions
        predictions = results.get("PredictiveAgent", {}).get("predictions", [])

        return predictions

    async def process_streaming_query(self, query: str, file_id: str, callback: Callable) -> Dict[str, Any]:
        """Process query with streaming updates"""
        # Send updates as processing happens
        await callback({"status": "Loading data..."})

        processor = DataProcessor()
        df = processor.load_file(file_id)

        await callback({"status": "Analyzing query..."})
        workflow = await self._analyze_query(query)

        await callback({"status": f"Executing {len(workflow)} agents..."})

        results = {}
        for i, agent_name in enumerate(workflow):
            await callback({"status": f"Processing with {agent_name}...", "progress": (i + 1) / len(workflow)})

            if agent_name in self.agent_pool.agents:
                agent = self.agent_pool.agents[agent_name]
                agent_result = await agent.process(df, {"query": query})
                results[agent_name] = agent_result

        await callback({"status": "Generating insights..."})
        insights = await self._synthesize_results(results, query)

        return {
            "query": query,
            "insights": insights,
            "workflow": workflow
        }

    async def route_to_agent(self, agent_type: str, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Route a query to a specific agent"""
        agent_map = {
            "ingestion": "DataIngestionAgent",
            "analytics": "AnalyticsAgent",
            "predictive": "PredictiveAgent",
            "insight": "InsightAgent",
            "hypothesis": "HypothesisAgent"
        }

        agent_name = agent_map.get(agent_type)
        if agent_name and agent_name in self.agent_pool.agents:
            agent = self.agent_pool.agents[agent_name]
            return await agent.process(query, context)

        raise ValueError(f"Unknown agent type: {agent_type}")

    async def get_agents_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return self.agent_pool.get_all_status()