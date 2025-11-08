"""
Insight Agent - Generates natural language insights and recommendations
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.agents.base import BaseAgent


class InsightAgent(BaseAgent):
    """Agent responsible for generating natural language insights"""

    def __init__(self):
        super().__init__(
            name="InsightAgent",
            description="Natural language insight generation and recommendation engine",
            tools=[]  # No special tools needed
        )

    async def process(self, data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate insights from analyzed data"""
        # Get previous results from context
        previous_results = context.get("previous_results", {}) if context else {}

        # Collect insights from all previous agents
        all_insights = []

        # Extract insights from each agent's results
        for agent_name, results in previous_results.items():
            if "insights" in results:
                all_insights.extend(results["insights"])

        # Generate meta-insights
        meta_insights = await self._generate_meta_insights(all_insights, context)

        # Generate recommendations
        recommendations = await self._generate_recommendations(all_insights, previous_results)

        # Create executive summary
        summary = await self._create_executive_summary(all_insights, recommendations)

        return {
            "status": "success",
            "insights": meta_insights,
            "recommendations": recommendations,
            "executive_summary": summary,
            "total_insights": len(all_insights),
            "confidence": self._calculate_overall_confidence(all_insights)
        }

    async def _generate_meta_insights(self, insights: List[Dict], context: Optional[Dict]) -> List[Dict[str, Any]]:
        """Generate higher-level insights from individual insights"""
        meta_insights = []

        # Group insights by type
        insight_groups = {}
        for insight in insights:
            insight_type = insight.get("type", "general")
            if insight_type not in insight_groups:
                insight_groups[insight_type] = []
            insight_groups[insight_type].append(insight)

        # Generate cross-functional insights
        if len(insight_groups) > 2:
            meta_insights.append({
                "type": "cross_functional",
                "title": "Multi-Dimensional Analysis Complete",
                "description": f"Analyzed {len(insight_groups)} different aspects of your sales data, providing comprehensive coverage",
                "confidence": 0.9,
                "data": {
                    "dimensions_analyzed": list(insight_groups.keys())
                }
            })

        # Identify critical insights
        high_confidence_insights = [i for i in insights if i.get("confidence", 0) > 0.8]
        if high_confidence_insights:
            meta_insights.append({
                "type": "critical_findings",
                "title": "High Confidence Findings",
                "description": f"Identified {len(high_confidence_insights)} insights with >80% confidence that require attention",
                "confidence": 0.95,
                "data": {
                    "critical_count": len(high_confidence_insights)
                }
            })

        # Use Claude for advanced meta-insights if available
        if self.client and insights:
            query = context.get("query", "") if context else ""
            prompt = f"""
            Based on these insights from sales data analysis:
            {[i.get('description', '') for i in insights[:5]]}

            User query: {query}

            Provide one strategic meta-insight that ties these findings together.
            Be specific and actionable.
            """

            ai_meta_insight = await self.think(prompt)
            if ai_meta_insight:
                meta_insights.append({
                    "type": "strategic",
                    "title": "Strategic Synthesis",
                    "description": ai_meta_insight[:300],
                    "confidence": 0.75,
                    "data": {}
                })

        return meta_insights

    async def _generate_recommendations(self, insights: List[Dict], previous_results: Dict) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on insights"""
        recommendations = []

        # Analyze insights for specific patterns
        for insight in insights:
            insight_type = insight.get("type", "")

            if insight_type == "win_rate" and insight.get("data", {}).get("win_rate", 0) < 0.25:
                recommendations.append({
                    "priority": "high",
                    "category": "process_improvement",
                    "title": "Improve Win Rate",
                    "description": "Your win rate is below industry average. Consider reviewing qualification criteria and sales methodology.",
                    "actions": [
                        "Implement stricter qualification criteria",
                        "Review and update sales playbooks",
                        "Increase discovery call quality"
                    ]
                })

            elif insight_type == "sales_cycle" and insight.get("data", {}).get("avg_cycle", 0) > 90:
                recommendations.append({
                    "priority": "medium",
                    "category": "velocity",
                    "title": "Accelerate Sales Cycles",
                    "description": "Long sales cycles are impacting velocity. Focus on removing friction points.",
                    "actions": [
                        "Identify and remove approval bottlenecks",
                        "Implement parallel evaluation processes",
                        "Create urgency through time-limited offers"
                    ]
                })

            elif insight_type == "pipeline_health" and insight.get("data", {}).get("health_score", 0) < 0.6:
                recommendations.append({
                    "priority": "high",
                    "category": "pipeline",
                    "title": "Pipeline Health Requires Attention",
                    "description": "Pipeline health indicators suggest risk. Immediate action needed.",
                    "actions": [
                        "Increase prospecting activities",
                        "Review and clean stale opportunities",
                        "Focus on deal advancement strategies"
                    ]
                })

        # Add general recommendations if none were generated
        if not recommendations:
            recommendations.append({
                "priority": "low",
                "category": "general",
                "title": "Continue Monitoring",
                "description": "No critical issues identified. Continue current practices while monitoring key metrics.",
                "actions": [
                    "Maintain current activity levels",
                    "Track KPIs weekly",
                    "Document successful patterns"
                ]
            })

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return recommendations[:5]  # Return top 5 recommendations

    async def _create_executive_summary(self, insights: List[Dict], recommendations: List[Dict]) -> str:
        """Create an executive summary of findings"""
        if not insights:
            return "No significant insights were generated from the data analysis."

        # Calculate key metrics
        total_insights = len(insights)
        high_priority_recs = len([r for r in recommendations if r.get("priority") == "high"])
        avg_confidence = np.mean([i.get("confidence", 0.5) for i in insights])

        # Build summary
        summary_parts = [
            f"Analysis generated {total_insights} insights with {avg_confidence:.0%} average confidence."
        ]

        if high_priority_recs > 0:
            summary_parts.append(f"Identified {high_priority_recs} high-priority recommendations requiring immediate attention.")

        # Add key findings
        top_insights = sorted(insights, key=lambda x: x.get("confidence", 0), reverse=True)[:3]
        if top_insights:
            summary_parts.append("Key findings include:")
            for i, insight in enumerate(top_insights, 1):
                summary_parts.append(f"{i}. {insight.get('title', 'Insight')}: {insight.get('description', '')[:100]}")

        # Use Claude for better summary if available
        if self.client and len(insights) > 5:
            prompt = f"""
            Create a 2-3 sentence executive summary of these sales analytics findings:
            - Total insights: {total_insights}
            - High priority recommendations: {high_priority_recs}
            - Key areas analyzed: {', '.join(set([i.get('type', 'general') for i in insights[:10]]))}

            Make it concise and actionable for sales leadership.
            """

            ai_summary = await self.think(prompt)
            if ai_summary:
                return ai_summary

        return " ".join(summary_parts)

    def _calculate_overall_confidence(self, insights: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not insights:
            return 0.5

        confidences = [i.get("confidence", 0.5) for i in insights]
        return float(np.mean(confidences))