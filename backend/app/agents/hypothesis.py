"""
Hypothesis Agent - Tests sales hypotheses against historical data
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from scipy import stats as scipy_stats
from sklearn.preprocessing import LabelEncoder

from app.agents.base import BaseAgent
from app.services.data_processor import DataProcessor


class HypothesisAgent(BaseAgent):
    """Agent responsible for testing sales hypotheses"""

    def __init__(self):
        super().__init__(
            name="HypothesisAgent",
            description="Statistical hypothesis testing for sales strategies",
            tools=[]
        )
        self.processor = DataProcessor()

    async def process(self, data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Test hypotheses on the data"""
        if isinstance(data, pd.DataFrame):
            df = data
        else:
            return {"status": "error", "message": "Hypothesis testing requires DataFrame input"}

        # Get hypothesis from context
        hypothesis = context.get("hypothesis", "") if context else ""
        schema = context.get("previous_results", {}).get("DataIngestionAgent", {}).get("schema", {})

        if not schema:
            schema = self.processor.detect_crm_schema(df)

        # Test the hypothesis
        test_results = await self._test_hypothesis(df, hypothesis, schema)

        # Discover patterns
        patterns = self._discover_patterns(df, schema)

        # Generate insights
        insights = await self._generate_hypothesis_insights(test_results, patterns, hypothesis)

        return {
            "status": "success",
            "hypothesis": hypothesis,
            "result": test_results.get("result", "inconclusive"),
            "confidence": test_results.get("confidence", 0.5),
            "evidence": test_results.get("evidence", []),
            "patterns": patterns,
            "insights": insights,
            "recommendation": test_results.get("recommendation", "")
        }

    async def _test_hypothesis(self, df: pd.DataFrame, hypothesis: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """Test a specific hypothesis against the data"""
        hypothesis_lower = hypothesis.lower()

        # Pattern matching for common hypotheses
        if "multi" in hypothesis_lower and "thread" in hypothesis_lower:
            return await self._test_multi_threading_hypothesis(df, schema)

        elif "size" in hypothesis_lower and ("cycle" in hypothesis_lower or "time" in hypothesis_lower):
            return await self._test_deal_size_cycle_hypothesis(df, schema)

        elif "stage" in hypothesis_lower and ("win" in hypothesis_lower or "success" in hypothesis_lower):
            return await self._test_stage_success_hypothesis(df, schema)

        elif "owner" in hypothesis_lower or "rep" in hypothesis_lower:
            return await self._test_rep_performance_hypothesis(df, schema)

        else:
            # Generic hypothesis testing using Claude
            return await self._test_generic_hypothesis(df, hypothesis, schema)

    async def _test_multi_threading_hypothesis(self, df: pd.DataFrame, schema: Dict[str, str]) -> Dict[str, Any]:
        """Test if multi-threaded deals close faster/better"""
        # Simplified for MVP - in production would look for contact count
        evidence = []
        confidence = 0.5

        if "owner" in schema and "close_date" in schema and "created_date" in schema:
            # Simulate multi-threading by looking at deal complexity
            # (In real implementation, would count contacts per deal)
            df["cycle_days"] = (pd.to_datetime(df[schema["close_date"]], errors="coerce") -
                              pd.to_datetime(df[schema["created_date"]], errors="coerce")).dt.days

            # Use deal amount as proxy for complexity/multi-threading
            if "amount" in schema:
                high_value = df[schema["amount"]] > df[schema["amount"]].median()
                avg_cycle_high = df[high_value]["cycle_days"].mean()
                avg_cycle_low = df[~high_value]["cycle_days"].mean()

                if pd.notna(avg_cycle_high) and pd.notna(avg_cycle_low):
                    # Perform t-test
                    t_stat, p_value = scipy_stats.ttest_ind(
                        df[high_value]["cycle_days"].dropna(),
                        df[~high_value]["cycle_days"].dropna()
                    )

                    confidence = 1 - p_value if p_value < 0.5 else 0.5

                    evidence.append(f"High-value deals (likely multi-threaded): {avg_cycle_high:.0f} days average cycle")
                    evidence.append(f"Low-value deals: {avg_cycle_low:.0f} days average cycle")
                    evidence.append(f"Statistical significance: p-value = {p_value:.3f}")

                    result = "supported" if p_value < 0.05 else "not supported"
                    recommendation = "Focus on multi-threading for complex deals" if result == "supported" else "Multi-threading may not significantly impact cycle time"

                    return {
                        "result": result,
                        "confidence": float(confidence),
                        "evidence": evidence,
                        "recommendation": recommendation
                    }

        return {
            "result": "inconclusive",
            "confidence": 0.3,
            "evidence": ["Insufficient data to test multi-threading hypothesis"],
            "recommendation": "Need contact/stakeholder data to properly test this hypothesis"
        }

    async def _test_deal_size_cycle_hypothesis(self, df: pd.DataFrame, schema: Dict[str, str]) -> Dict[str, Any]:
        """Test relationship between deal size and sales cycle"""
        evidence = []

        if all(col in schema for col in ["amount", "created_date", "close_date"]):
            # Calculate cycle days
            df["cycle_days"] = (pd.to_datetime(df[schema["close_date"]], errors="coerce") -
                              pd.to_datetime(df[schema["created_date"]], errors="coerce")).dt.days

            # Remove invalid data
            valid_data = df[(df["cycle_days"] > 0) & (df["cycle_days"] < 365)].copy()

            if len(valid_data) > 10:
                # Calculate correlation
                correlation = valid_data[schema["amount"]].corr(valid_data["cycle_days"])

                evidence.append(f"Correlation between deal size and cycle length: {correlation:.3f}")

                # Segment analysis
                quartiles = valid_data[schema["amount"]].quantile([0.25, 0.5, 0.75])
                for i, q in enumerate([0.25, 0.5, 0.75], 1):
                    segment = valid_data[valid_data[schema["amount"]] <= quartiles[q]]
                    if len(segment) > 0:
                        avg_cycle = segment["cycle_days"].mean()
                        evidence.append(f"Q{i} deals (≤${quartiles[q]:,.0f}): {avg_cycle:.0f} days average")

                # Determine result
                if abs(correlation) > 0.3:
                    result = "supported"
                    relationship = "longer" if correlation > 0 else "shorter"
                    recommendation = f"Larger deals tend to have {relationship} sales cycles. Adjust forecasting accordingly."
                    confidence = min(abs(correlation) + 0.3, 0.9)
                else:
                    result = "not supported"
                    recommendation = "Deal size does not significantly impact sales cycle. Other factors may be more important."
                    confidence = 0.6

                return {
                    "result": result,
                    "confidence": float(confidence),
                    "evidence": evidence,
                    "recommendation": recommendation,
                    "correlation": float(correlation)
                }

        return {
            "result": "inconclusive",
            "confidence": 0.3,
            "evidence": ["Insufficient data to test deal size vs cycle hypothesis"],
            "recommendation": "Need complete deal lifecycle data"
        }

    async def _test_stage_success_hypothesis(self, df: pd.DataFrame, schema: Dict[str, str]) -> Dict[str, Any]:
        """Test which stages predict success"""
        evidence = []

        if "stage" in schema:
            stage_col = schema["stage"]

            # Define success (closed won deals)
            success_keywords = ["closed won", "won", "success", "closed-won"]
            df["is_success"] = df[stage_col].str.lower().apply(
                lambda x: any(keyword in str(x) for keyword in success_keywords)
            )

            # Analyze stage distribution for successful vs unsuccessful
            stage_counts = df[stage_col].value_counts()
            success_by_stage = df.groupby(stage_col)["is_success"].mean()

            # Find stages with high success rates
            high_success_stages = success_by_stage[success_by_stage > 0.5]

            if len(high_success_stages) > 0:
                for stage, rate in high_success_stages.items():
                    evidence.append(f"Stage '{stage}': {rate*100:.1f}% success rate")

                result = "supported"
                recommendation = f"Focus on advancing deals to: {', '.join(high_success_stages.index[:3])}"
                confidence = 0.75
            else:
                result = "not supported"
                recommendation = "No clear stage predictor of success found. Review sales process."
                confidence = 0.5
                evidence.append("No stages show >50% success rate")

            return {
                "result": result,
                "confidence": float(confidence),
                "evidence": evidence,
                "recommendation": recommendation
            }

        return {
            "result": "inconclusive",
            "confidence": 0.3,
            "evidence": ["Stage data not available"],
            "recommendation": "Need stage progression data"
        }

    async def _test_rep_performance_hypothesis(self, df: pd.DataFrame, schema: Dict[str, str]) -> Dict[str, Any]:
        """Test rep performance differences"""
        evidence = []

        if "owner" in schema and "amount" in schema:
            owner_col = schema["owner"]
            amount_col = schema["amount"]

            # Calculate rep metrics
            rep_stats = df.groupby(owner_col)[amount_col].agg(["sum", "mean", "count"])
            rep_stats = rep_stats.sort_values("sum", ascending=False)

            # Statistical test for performance differences
            if len(rep_stats) > 2:
                # ANOVA test for differences
                groups = [group[amount_col].dropna() for name, group in df.groupby(owner_col)]
                groups = [g for g in groups if len(g) > 1]  # Filter out single-value groups

                if len(groups) > 2:
                    f_stat, p_value = scipy_stats.f_oneway(*groups)

                    evidence.append(f"Performance variance across {len(rep_stats)} reps")
                    evidence.append(f"Top performer: {rep_stats.index[0]} with ${rep_stats.iloc[0]['sum']:,.0f}")
                    evidence.append(f"Statistical significance of differences: p={p_value:.3f}")

                    if p_value < 0.05:
                        result = "supported"
                        recommendation = "Significant performance differences exist. Share best practices from top performers."
                        confidence = 0.8
                    else:
                        result = "not supported"
                        recommendation = "Rep performance is relatively uniform. Focus on system-wide improvements."
                        confidence = 0.6

                    return {
                        "result": result,
                        "confidence": float(confidence),
                        "evidence": evidence,
                        "recommendation": recommendation
                    }

        return {
            "result": "inconclusive",
            "confidence": 0.3,
            "evidence": ["Insufficient data to test rep performance hypothesis"],
            "recommendation": "Need owner and outcome data"
        }

    async def _test_generic_hypothesis(self, df: pd.DataFrame, hypothesis: str, schema: Dict[str, str]) -> Dict[str, Any]:
        """Test a generic hypothesis using AI"""
        if self.client:
            # Prepare data summary
            data_summary = {
                "rows": len(df),
                "columns": list(df.columns),
                "schema": schema,
                "numeric_summary": df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {}
            }

            prompt = f"""
            Test this hypothesis: "{hypothesis}"

            Data summary:
            - Total records: {data_summary['rows']}
            - Available fields: {', '.join(schema.keys())}

            Based on the data structure, provide:
            1. Whether the hypothesis is likely supported, not supported, or inconclusive
            2. Key evidence points
            3. A recommendation

            Be specific and data-driven.
            """

            ai_analysis = await self.think(prompt, str(data_summary))

            # Parse AI response into structured format
            return {
                "result": "ai_analyzed",
                "confidence": 0.6,
                "evidence": [ai_analysis[:500]],
                "recommendation": "AI-generated analysis provided above"
            }

        return {
            "result": "inconclusive",
            "confidence": 0.3,
            "evidence": ["Unable to test custom hypothesis without AI assistance"],
            "recommendation": "Try a more specific hypothesis or enable AI analysis"
        }

    def _discover_patterns(self, df: pd.DataFrame, schema: Dict[str, str]) -> List[Dict[str, Any]]:
        """Discover interesting patterns in the data"""
        patterns = []

        # Pattern 1: Day of week analysis
        if "created_date" in schema:
            df["day_of_week"] = pd.to_datetime(df[schema["created_date"]], errors="coerce").dt.dayofweek
            dow_counts = df["day_of_week"].value_counts()

            if len(dow_counts) > 0:
                best_day = dow_counts.idxmax()
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                patterns.append({
                    "type": "temporal",
                    "pattern": f"Most deals created on {days[best_day]}",
                    "strength": 0.7
                })

        # Pattern 2: Round number bias
        if "amount" in schema:
            amounts = df[schema["amount"]].dropna()
            round_numbers = amounts[amounts % 1000 == 0]
            if len(amounts) > 0:
                round_pct = len(round_numbers) / len(amounts)
                if round_pct > 0.3:
                    patterns.append({
                        "type": "behavioral",
                        "pattern": f"{round_pct*100:.0f}% of deals have round numbers (psychological pricing)",
                        "strength": 0.8
                    })

        # Pattern 3: Seasonality
        if "created_date" in schema:
            df["month"] = pd.to_datetime(df[schema["created_date"]], errors="coerce").dt.month
            month_counts = df["month"].value_counts()

            if len(month_counts) > 0:
                peak_month = month_counts.idxmax()
                months = ["", "January", "February", "March", "April", "May", "June",
                         "July", "August", "September", "October", "November", "December"]
                patterns.append({
                    "type": "seasonal",
                    "pattern": f"Peak activity in {months[peak_month]}",
                    "strength": 0.6
                })

        return patterns

    async def _generate_hypothesis_insights(self, test_results: Dict, patterns: List[Dict],
                                           hypothesis: str) -> List[Dict[str, Any]]:
        """Generate insights from hypothesis testing"""
        insights = []

        # Insight from test result
        result = test_results.get("result", "inconclusive")
        confidence = test_results.get("confidence", 0.5)

        insights.append({
            "type": "hypothesis_test",
            "title": "Hypothesis Test Result",
            "description": f"Hypothesis '{hypothesis[:100]}' is {result} with {confidence*100:.0f}% confidence",
            "confidence": confidence,
            "data": {
                "result": result,
                "evidence_count": len(test_results.get("evidence", []))
            }
        })

        # Insights from patterns
        if patterns:
            strong_patterns = [p for p in patterns if p.get("strength", 0) > 0.7]
            if strong_patterns:
                insights.append({
                    "type": "pattern_discovery",
                    "title": "Strong Patterns Detected",
                    "description": f"Found {len(strong_patterns)} strong patterns in your data",
                    "confidence": 0.8,
                    "data": {
                        "patterns": [p["pattern"] for p in strong_patterns[:3]]
                    }
                })

        # Recommendation insight
        if test_results.get("recommendation"):
            insights.append({
                "type": "actionable",
                "title": "Recommended Action",
                "description": test_results["recommendation"],
                "confidence": confidence * 0.9,
                "data": {}
            })

        return insights