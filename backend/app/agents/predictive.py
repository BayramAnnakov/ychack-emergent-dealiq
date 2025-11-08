"""
Predictive Agent - ML-based predictions for deals and revenue
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

from app.agents.base import BaseAgent


class PredictiveAgent(BaseAgent):
    """Agent responsible for predictive analytics and ML-based forecasting"""

    def __init__(self):
        super().__init__(
            name="PredictiveAgent",
            description="Machine learning predictions for deal outcomes and revenue"
        )

    async def process(self, data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate predictions based on data"""
        if isinstance(data, pd.DataFrame):
            df = data
        else:
            return {"status": "error", "message": "Predictive analysis requires DataFrame input"}

        # Get context information
        prediction_type = context.get("prediction_type", "deal_closure")
        schema = context.get("previous_results", {}).get("DataIngestionAgent", {}).get("schema", {})

        # Generate predictions based on type
        predictions = []

        if prediction_type == "deal_closure":
            predictions = await self._predict_deal_closure(df, schema)
        elif prediction_type == "quota_attainment":
            predictions = await self._predict_quota_attainment(df, schema)
        elif prediction_type == "pipeline_health":
            predictions = await self._assess_pipeline_health(df, schema)
        elif prediction_type == "churn_risk":
            predictions = await self._predict_churn_risk(df, schema)
        else:
            # Default to deal scoring
            predictions = await self._score_deals(df, schema)

        # Generate predictive insights
        insights = await self._generate_predictive_insights(predictions, prediction_type)

        return {
            "status": "success",
            "prediction_type": prediction_type,
            "predictions": predictions,
            "insights": insights,
            "confidence": self._calculate_prediction_confidence(predictions)
        }

    async def _predict_deal_closure(self, df: pd.DataFrame, schema: Dict[str, str]) -> List[Dict[str, Any]]:
        """Predict which deals will close"""
        predictions = []

        # Check if we have necessary columns
        if "stage" in schema and "amount" in schema:
            stage_col = schema["stage"]
            amount_col = schema["amount"]

            # Simple rule-based prediction for MVP
            # In production, would use trained ML model
            for idx, row in df.iterrows():
                stage = row.get(stage_col, "")
                amount = row.get(amount_col, 0)

                # Scoring based on stage
                stage_scores = {
                    "negotiation": 0.7,
                    "proposal": 0.6,
                    "qualified": 0.4,
                    "demo": 0.3,
                    "discovery": 0.2,
                    "prospecting": 0.1
                }

                base_score = 0.3
                for key, score in stage_scores.items():
                    if key in str(stage).lower():
                        base_score = score
                        break

                # Adjust based on deal size
                if amount > df[amount_col].median():
                    base_score *= 0.9  # Larger deals slightly less likely to close
                else:
                    base_score *= 1.1  # Smaller deals slightly more likely

                # Add some randomness for demo purposes
                final_score = min(base_score + np.random.uniform(-0.1, 0.1), 1.0)
                final_score = max(final_score, 0.0)

                deal_id = row.get(schema.get("deal_id", df.columns[0]))

                predictions.append({
                    "deal_id": str(deal_id),
                    "probability": float(final_score),
                    "prediction": "likely" if final_score > 0.5 else "unlikely",
                    "risk_factors": self._identify_risk_factors(row, schema),
                    "confidence": 0.75
                })

        # Sort by probability
        predictions.sort(key=lambda x: x["probability"], reverse=True)

        return predictions[:20]  # Return top 20 predictions

    async def _predict_quota_attainment(self, df: pd.DataFrame, schema: Dict[str, str]) -> List[Dict[str, Any]]:
        """Predict quota attainment by rep"""
        predictions = []

        if "owner" in schema and "amount" in schema:
            owner_col = schema["owner"]
            amount_col = schema["amount"]

            # Group by owner
            owner_pipeline = df.groupby(owner_col)[amount_col].agg(["sum", "count", "mean"])

            # Simple quota calculation (in production, would use actual quotas)
            assumed_quota = df[amount_col].sum() / len(owner_pipeline) * 1.2

            for owner, stats in owner_pipeline.iterrows():
                current_pipeline = stats["sum"]
                deal_count = stats["count"]
                avg_deal = stats["mean"]

                # Simple prediction based on current pipeline
                attainment_prob = min(current_pipeline / assumed_quota, 1.5)

                predictions.append({
                    "rep": str(owner),
                    "current_pipeline": float(current_pipeline),
                    "assumed_quota": float(assumed_quota),
                    "attainment_probability": float(min(attainment_prob, 1.0)),
                    "projected_attainment": float(attainment_prob * 100),
                    "deal_count": int(deal_count),
                    "avg_deal_size": float(avg_deal),
                    "risk_level": "low" if attainment_prob > 0.8 else "high" if attainment_prob < 0.5 else "medium"
                })

        return predictions

    async def _assess_pipeline_health(self, df: pd.DataFrame, schema: Dict[str, str]) -> List[Dict[str, Any]]:
        """Assess overall pipeline health"""
        health_metrics = []

        # Calculate various health indicators
        total_value = df[schema["amount"]].sum() if "amount" in schema else 0

        # Stage distribution health
        if "stage" in schema:
            stage_col = schema["stage"]
            stage_dist = df[stage_col].value_counts(normalize=True)

            # Ideal funnel shape
            early_stage = sum(stage_dist.get(s, 0) for s in stage_dist.index
                            if any(k in str(s).lower() for k in ["prospect", "qualify", "discovery"]))
            mid_stage = sum(stage_dist.get(s, 0) for s in stage_dist.index
                          if any(k in str(s).lower() for k in ["demo", "proposal"]))
            late_stage = sum(stage_dist.get(s, 0) for s in stage_dist.index
                           if any(k in str(s).lower() for k in ["negotiation", "closing"]))

            funnel_health = "healthy" if early_stage > mid_stage > late_stage else "inverted"

            health_metrics.append({
                "metric": "funnel_shape",
                "status": funnel_health,
                "score": 0.8 if funnel_health == "healthy" else 0.4,
                "details": {
                    "early_stage": float(early_stage),
                    "mid_stage": float(mid_stage),
                    "late_stage": float(late_stage)
                }
            })

        # Deal aging health
        if "created_date" in schema:
            date_col = schema["created_date"]
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df_with_dates = df[df[date_col].notna()]

            if len(df_with_dates) > 0:
                days_old = (datetime.now() - df_with_dates[date_col]).dt.days
                avg_age = days_old.mean()

                aging_score = 1.0 - min(avg_age / 180, 1.0)  # Penalty for old deals

                health_metrics.append({
                    "metric": "deal_aging",
                    "status": "fresh" if avg_age < 30 else "aging" if avg_age < 90 else "stale",
                    "score": float(aging_score),
                    "details": {
                        "avg_days_old": float(avg_age),
                        "oldest_deal_days": float(days_old.max())
                    }
                })

        # Coverage health
        if "owner" in schema:
            owner_col = schema["owner"]
            rep_coverage = df[owner_col].value_counts()
            coverage_variance = rep_coverage.std() / rep_coverage.mean() if len(rep_coverage) > 1 else 0

            coverage_score = 1.0 - min(coverage_variance, 1.0)

            health_metrics.append({
                "metric": "rep_coverage",
                "status": "balanced" if coverage_variance < 0.5 else "imbalanced",
                "score": float(coverage_score),
                "details": {
                    "num_reps": len(rep_coverage),
                    "variance": float(coverage_variance)
                }
            })

        # Overall health score
        if health_metrics:
            overall_score = np.mean([m["score"] for m in health_metrics])
            health_metrics.insert(0, {
                "metric": "overall_health",
                "status": "excellent" if overall_score > 0.8 else "good" if overall_score > 0.6 else "needs_attention",
                "score": float(overall_score),
                "total_pipeline_value": float(total_value)
            })

        return health_metrics

    async def _predict_churn_risk(self, df: pd.DataFrame, schema: Dict[str, str]) -> List[Dict[str, Any]]:
        """Predict deals at risk of churning"""
        at_risk = []

        for idx, row in df.iterrows():
            risk_score = 0
            risk_factors = []

            # Check for stale deals
            if "created_date" in schema:
                created = pd.to_datetime(row.get(schema["created_date"]), errors="coerce")
                if pd.notna(created):
                    days_old = (datetime.now() - created).days
                    if days_old > 90:
                        risk_score += 0.3
                        risk_factors.append(f"Deal is {days_old} days old")

            # Check for low activity (simplified)
            if "stage" in schema:
                stage = str(row.get(schema["stage"], "")).lower()
                if any(k in stage for k in ["prospect", "qualify"]) and risk_score > 0:
                    risk_score += 0.2
                    risk_factors.append("Still in early stage")

            # Check for small deal size
            if "amount" in schema:
                amount = row.get(schema["amount"], 0)
                if amount < df[schema["amount"]].quantile(0.25):
                    risk_score += 0.1
                    risk_factors.append("Below average deal size")

            if risk_score > 0.3:
                deal_id = row.get(schema.get("deal_id", df.columns[0]))
                at_risk.append({
                    "deal_id": str(deal_id),
                    "risk_score": float(min(risk_score, 1.0)),
                    "risk_level": "high" if risk_score > 0.6 else "medium",
                    "risk_factors": risk_factors,
                    "recommended_action": self._get_risk_mitigation(risk_factors)
                })

        # Sort by risk score
        at_risk.sort(key=lambda x: x["risk_score"], reverse=True)

        return at_risk[:10]  # Top 10 at-risk deals

    async def _score_deals(self, df: pd.DataFrame, schema: Dict[str, str]) -> List[Dict[str, Any]]:
        """Score deals based on multiple factors"""
        scored_deals = []

        for idx, row in df.iterrows():
            score = 0.5  # Base score

            # Factor in deal size
            if "amount" in schema:
                amount = row.get(schema["amount"], 0)
                percentile = (df[schema["amount"]] <= amount).mean()
                score += percentile * 0.2

            # Factor in stage
            if "stage" in schema:
                stage = str(row.get(schema["stage"], "")).lower()
                stage_weights = {
                    "negotiation": 0.3,
                    "proposal": 0.2,
                    "demo": 0.1,
                    "qualified": 0.05
                }
                for key, weight in stage_weights.items():
                    if key in stage:
                        score += weight
                        break

            # Factor in age
            if "created_date" in schema:
                created = pd.to_datetime(row.get(schema["created_date"]), errors="coerce")
                if pd.notna(created):
                    days_old = (datetime.now() - created).days
                    if days_old < 30:
                        score += 0.1
                    elif days_old > 90:
                        score -= 0.1

            deal_id = row.get(schema.get("deal_id", df.columns[0]))

            scored_deals.append({
                "deal_id": str(deal_id),
                "score": float(min(max(score, 0), 1)),
                "priority": "high" if score > 0.7 else "medium" if score > 0.4 else "low"
            })

        # Sort by score
        scored_deals.sort(key=lambda x: x["score"], reverse=True)

        return scored_deals[:20]

    def _identify_risk_factors(self, row: pd.Series, schema: Dict[str, str]) -> List[str]:
        """Identify risk factors for a deal"""
        risks = []

        # Check deal age
        if "created_date" in schema:
            created = pd.to_datetime(row.get(schema["created_date"]), errors="coerce")
            if pd.notna(created):
                days_old = (datetime.now() - created).days
                if days_old > 60:
                    risks.append("Aging deal")

        # Check stage
        if "stage" in schema:
            stage = str(row.get(schema["stage"], "")).lower()
            if any(k in stage for k in ["prospect", "qualify"]):
                risks.append("Early stage")

        # Check amount
        if "amount" in schema:
            amount = row.get(schema["amount"], 0)
            if amount == 0:
                risks.append("No value assigned")

        return risks if risks else ["No significant risks identified"]

    def _get_risk_mitigation(self, risk_factors: List[str]) -> str:
        """Get recommended action for risk mitigation"""
        if "Aging deal" in str(risk_factors):
            return "Schedule immediate follow-up to re-engage"
        elif "Early stage" in str(risk_factors):
            return "Accelerate qualification process"
        elif "No value assigned" in str(risk_factors):
            return "Obtain budget confirmation from prospect"
        else:
            return "Monitor closely and maintain regular contact"

    async def _generate_predictive_insights(self, predictions: List[Dict], prediction_type: str) -> List[Dict[str, Any]]:
        """Generate insights from predictions"""
        insights = []

        if not predictions:
            return insights

        if prediction_type == "deal_closure":
            high_prob_deals = [p for p in predictions if p.get("probability", 0) > 0.7]
            low_prob_deals = [p for p in predictions if p.get("probability", 0) < 0.3]

            insights.append({
                "type": "closure_prediction",
                "title": "Deal Closure Forecast",
                "description": f"{len(high_prob_deals)} deals have >70% closure probability, {len(low_prob_deals)} deals at risk",
                "confidence": 0.75,
                "data": {
                    "high_probability_count": len(high_prob_deals),
                    "at_risk_count": len(low_prob_deals)
                }
            })

        elif prediction_type == "pipeline_health":
            overall_score = predictions[0].get("score", 0) if predictions else 0

            insights.append({
                "type": "pipeline_health",
                "title": "Pipeline Health Assessment",
                "description": f"Overall pipeline health score: {overall_score:.1%}",
                "confidence": 0.8,
                "data": {
                    "health_score": overall_score,
                    "metrics": len(predictions)
                }
            })

        elif prediction_type == "churn_risk":
            high_risk = [p for p in predictions if p.get("risk_level") == "high"]

            insights.append({
                "type": "churn_risk",
                "title": "Deals at Risk",
                "description": f"{len(high_risk)} deals at high risk of churning - immediate action required",
                "confidence": 0.7,
                "data": {
                    "high_risk_count": len(high_risk),
                    "total_at_risk": len(predictions)
                }
            })

        return insights

    def _calculate_prediction_confidence(self, predictions: List[Dict]) -> float:
        """Calculate overall confidence in predictions"""
        if not predictions:
            return 0.5

        # Average confidence from individual predictions
        confidences = [p.get("confidence", 0.5) for p in predictions if "confidence" in p]

        if confidences:
            return np.mean(confidences)

        # Default confidence based on prediction count
        return min(0.5 + len(predictions) * 0.01, 0.9)