"""
Analytics Agent - Performs statistical analysis on sales data
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from scipy import stats

from app.agents.base import BaseAgent
from app.services.data_processor import DataProcessor


class AnalyticsAgent(BaseAgent):
    """Agent responsible for statistical analysis of sales data"""

    def __init__(self):
        super().__init__(
            name="AnalyticsAgent",
            description="Statistical analysis and metrics calculation for sales data"
        )
        self.processor = DataProcessor()

    async def process(self, data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process data for analytics"""
        if isinstance(data, pd.DataFrame):
            df = data
        else:
            return {"status": "error", "message": "Analytics requires DataFrame input"}

        # Get schema from context or detect it
        schema = context.get("previous_results", {}).get("DataIngestionAgent", {}).get("schema", {})
        if not schema:
            schema = self.processor.detect_crm_schema(df)

        # Calculate various metrics
        pipeline_metrics = self.processor.calculate_pipeline_metrics(df, schema)
        trend_analysis = self._analyze_trends(df, schema)
        cohort_metrics = self._perform_cohort_analysis(df, schema)
        velocity_metrics = self._calculate_velocity_metrics(df, schema)

        # Generate analytical insights
        insights = await self._generate_analytical_insights(
            df, pipeline_metrics, trend_analysis, cohort_metrics, velocity_metrics
        )

        return {
            "status": "success",
            "pipeline_metrics": pipeline_metrics,
            "trend_analysis": trend_analysis,
            "cohort_metrics": cohort_metrics,
            "velocity_metrics": velocity_metrics,
            "insights": insights,
            "confidence": 0.85
        }

    def _analyze_trends(self, df: pd.DataFrame, schema: Dict[str, str]) -> Dict[str, Any]:
        """Analyze trends in the data"""
        trends = {}

        # Deal value trends
        if "amount" in schema and "created_date" in schema:
            amount_col = schema["amount"]
            date_col = schema["created_date"]

            # Convert to datetime if not already
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

            # Group by month
            df_with_dates = df[df[date_col].notna()].copy()
            if len(df_with_dates) > 0:
                df_with_dates["month"] = df_with_dates[date_col].dt.to_period("M")

                monthly_stats = df_with_dates.groupby("month")[amount_col].agg([
                    "sum", "mean", "count"
                ]).to_dict("index")

                # Calculate growth rates
                months = sorted(monthly_stats.keys())
                if len(months) > 1:
                    growth_rates = []
                    for i in range(1, len(months)):
                        prev_sum = monthly_stats[months[i-1]]["sum"]
                        curr_sum = monthly_stats[months[i]]["sum"]
                        if prev_sum > 0:
                            growth = ((curr_sum - prev_sum) / prev_sum) * 100
                            growth_rates.append(growth)

                    trends["monthly_growth_rate"] = np.mean(growth_rates) if growth_rates else 0

                trends["monthly_stats"] = {str(k): v for k, v in monthly_stats.items()}

        # Stage progression trends
        if "stage" in schema:
            stage_col = schema["stage"]
            stage_distribution = df[stage_col].value_counts(normalize=True).to_dict()
            trends["stage_distribution"] = stage_distribution

        return trends

    def _perform_cohort_analysis(self, df: pd.DataFrame, schema: Dict[str, str]) -> Dict[str, Any]:
        """Perform cohort analysis"""
        cohorts = {}

        if "created_date" in schema and "amount" in schema:
            date_col = schema["created_date"]
            amount_col = schema["amount"]

            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df_with_dates = df[df[date_col].notna()].copy()

            if len(df_with_dates) > 0:
                # Create quarterly cohorts
                df_with_dates["cohort"] = df_with_dates[date_col].dt.to_period("Q")

                cohort_stats = df_with_dates.groupby("cohort").agg({
                    amount_col: ["sum", "mean", "count"]
                })

                cohorts["quarterly_cohorts"] = {
                    str(cohort): {
                        "total_value": float(stats[amount_col]["sum"]),
                        "avg_deal_size": float(stats[amount_col]["mean"]),
                        "deal_count": int(stats[amount_col]["count"])
                    }
                    for cohort, stats in cohort_stats.iterrows()
                }

                # Analyze by owner if available
                if "owner" in schema:
                    owner_col = schema["owner"]
                    owner_stats = df_with_dates.groupby(owner_col)[amount_col].agg([
                        "sum", "mean", "count"
                    ]).sort_values("sum", ascending=False)

                    cohorts["top_performers"] = owner_stats.head(5).to_dict("index")

        return cohorts

    def _calculate_velocity_metrics(self, df: pd.DataFrame, schema: Dict[str, str]) -> Dict[str, Any]:
        """Calculate sales velocity metrics"""
        velocity = {}

        # Pipeline velocity
        if "created_date" in schema and "close_date" in schema:
            created_col = schema["created_date"]
            close_col = schema["close_date"]

            df[created_col] = pd.to_datetime(df[created_col], errors="coerce")
            df[close_col] = pd.to_datetime(df[close_col], errors="coerce")

            closed_deals = df[df[close_col].notna()].copy()
            if len(closed_deals) > 0:
                closed_deals["cycle_days"] = (closed_deals[close_col] - closed_deals[created_col]).dt.days

                velocity["avg_sales_cycle"] = float(closed_deals["cycle_days"].mean())
                velocity["median_sales_cycle"] = float(closed_deals["cycle_days"].median())
                velocity["cycle_stddev"] = float(closed_deals["cycle_days"].std())

                # Stage velocity if available
                if "stage" in schema:
                    stage_col = schema["stage"]
                    stage_velocity = closed_deals.groupby(stage_col)["cycle_days"].mean().to_dict()
                    velocity["stage_velocity"] = stage_velocity

        # Deal velocity (deals per time period)
        if "created_date" in schema:
            date_col = schema["created_date"]
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df_with_dates = df[df[date_col].notna()]

            if len(df_with_dates) > 0:
                date_range = (df_with_dates[date_col].max() - df_with_dates[date_col].min()).days
                if date_range > 0:
                    velocity["deals_per_day"] = len(df_with_dates) / date_range
                    velocity["deals_per_month"] = velocity["deals_per_day"] * 30

        return velocity

    async def _generate_analytical_insights(self, df: pd.DataFrame, pipeline_metrics: Dict,
                                           trend_analysis: Dict, cohort_metrics: Dict,
                                           velocity_metrics: Dict) -> List[Dict[str, Any]]:
        """Generate analytical insights from metrics"""
        insights = []

        # Pipeline health insight
        if "total_pipeline_value" in pipeline_metrics:
            total_value = pipeline_metrics["total_pipeline_value"]
            avg_deal = pipeline_metrics.get("average_deal_size", 0)

            insights.append({
                "type": "pipeline_health",
                "title": "Pipeline Value Analysis",
                "description": f"Total pipeline value: ${total_value:,.0f} across {len(df)} deals with average size ${avg_deal:,.0f}",
                "confidence": 0.9,
                "data": {
                    "total_value": total_value,
                    "deal_count": len(df),
                    "avg_deal_size": avg_deal
                }
            })

        # Win rate insight
        if "win_rate" in pipeline_metrics:
            win_rate = pipeline_metrics["win_rate"]
            performance = "above average" if win_rate > 0.25 else "below average"

            insights.append({
                "type": "win_rate",
                "title": "Win Rate Analysis",
                "description": f"Current win rate is {win_rate*100:.1f}%, which is {performance} for the industry",
                "confidence": 0.85,
                "data": {
                    "win_rate": win_rate,
                    "benchmark": 0.25
                }
            })

        # Sales cycle insight
        if "avg_sales_cycle" in velocity_metrics:
            avg_cycle = velocity_metrics["avg_sales_cycle"]
            median_cycle = velocity_metrics.get("median_sales_cycle", avg_cycle)

            insights.append({
                "type": "sales_cycle",
                "title": "Sales Cycle Duration",
                "description": f"Average sales cycle is {avg_cycle:.0f} days (median: {median_cycle:.0f} days)",
                "confidence": 0.9,
                "data": {
                    "avg_cycle": avg_cycle,
                    "median_cycle": median_cycle
                }
            })

        # Growth trend insight
        if "monthly_growth_rate" in trend_analysis:
            growth_rate = trend_analysis["monthly_growth_rate"]
            trend = "growing" if growth_rate > 0 else "declining"

            insights.append({
                "type": "growth_trend",
                "title": "Revenue Growth Trend",
                "description": f"Pipeline is {trend} at {abs(growth_rate):.1f}% month-over-month",
                "confidence": 0.75,
                "data": {
                    "growth_rate": growth_rate,
                    "trend": trend
                }
            })

        # Top performers insight
        if "top_performers" in cohort_metrics:
            top_performers = cohort_metrics["top_performers"]
            if top_performers:
                top_rep = list(top_performers.keys())[0]
                top_value = top_performers[top_rep]["sum"]

                insights.append({
                    "type": "top_performers",
                    "title": "Top Sales Performers",
                    "description": f"Top performer '{top_rep}' generated ${top_value:,.0f} in pipeline value",
                    "confidence": 0.95,
                    "data": {
                        "top_performers": list(top_performers.keys())[:3]
                    }
                })

        # Use Claude for advanced insights if available
        if self.client:
            prompt = f"""
            Analyze these sales metrics and provide one key strategic insight:
            - Total deals: {len(df)}
            - Pipeline value: ${pipeline_metrics.get('total_pipeline_value', 0):,.0f}
            - Win rate: {pipeline_metrics.get('win_rate', 0)*100:.1f}%
            - Avg cycle: {velocity_metrics.get('avg_sales_cycle', 0):.0f} days
            - Growth rate: {trend_analysis.get('monthly_growth_rate', 0):.1f}%

            Provide a brief, actionable recommendation.
            """

            ai_insight = await self.think(prompt)
            if ai_insight:
                insights.append({
                    "type": "strategic_recommendation",
                    "title": "Strategic Recommendation",
                    "description": ai_insight[:200],
                    "confidence": 0.7,
                    "data": {}
                })

        return insights