"""
Data Ingestion Agent - Handles data parsing and normalization
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import json

from app.agents.base import BaseAgent
from app.services.data_processor import DataProcessor


class DataIngestionAgent(BaseAgent):
    """Agent responsible for data ingestion and normalization"""

    def __init__(self):
        super().__init__(
            name="DataIngestionAgent",
            description="Intelligent CRM data parsing and normalization"
        )
        self.processor = DataProcessor()

    async def process(self, data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process incoming data"""
        if isinstance(data, pd.DataFrame):
            df = data
        else:
            # Attempt to convert to DataFrame
            df = self._convert_to_dataframe(data)

        # Detect CRM schema
        schema = self.processor.detect_crm_schema(df)

        # Clean data
        df_clean = self.processor.clean_data(df, schema)

        # Get basic stats
        stats = self.processor.get_basic_stats(df_clean)

        # Detect data quality issues
        quality_issues = self._detect_quality_issues(df_clean)

        # Generate ingestion insights
        insights = await self._generate_ingestion_insights(df_clean, schema, quality_issues)

        return {
            "status": "success",
            "schema": schema,
            "stats": stats,
            "quality_issues": quality_issues,
            "insights": insights,
            "confidence": self._calculate_data_quality_score(quality_issues),
            "output_data": df_clean  # Pass cleaned data to next agent
        }

    def _convert_to_dataframe(self, data: Any) -> pd.DataFrame:
        """Convert various data formats to DataFrame"""
        if isinstance(data, dict):
            return pd.DataFrame(data)
        elif isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, str):
            # Assume JSON string
            try:
                json_data = json.loads(data)
                return pd.DataFrame(json_data)
            except:
                raise ValueError("Unable to parse string data")
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")

    def _detect_quality_issues(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect data quality issues"""
        issues = []

        # Check for missing values
        null_counts = df.isnull().sum()
        high_null_cols = null_counts[null_counts > len(df) * 0.3]
        if not high_null_cols.empty:
            for col in high_null_cols.index:
                issues.append({
                    "type": "high_null_percentage",
                    "column": col,
                    "severity": "warning",
                    "percentage": float(null_counts[col] / len(df)),
                    "description": f"Column '{col}' has {null_counts[col]} missing values ({null_counts[col]/len(df)*100:.1f}%)"
                })

        # Check for duplicates
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            issues.append({
                "type": "duplicates",
                "severity": "info",
                "count": int(duplicate_count),
                "description": f"Found {duplicate_count} duplicate rows"
            })

        # Check for outliers in numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            outliers = ((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum()

            if outliers > 0:
                issues.append({
                    "type": "outliers",
                    "column": col,
                    "severity": "info",
                    "count": int(outliers),
                    "description": f"Column '{col}' has {outliers} potential outliers"
                })

        return issues

    async def _generate_ingestion_insights(self, df: pd.DataFrame, schema: Dict[str, str], issues: List[Dict]) -> List[Dict[str, Any]]:
        """Generate insights about the ingested data"""
        insights = []

        # Data completeness insight
        completeness = (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        insights.append({
            "type": "data_completeness",
            "title": "Data Completeness",
            "description": f"Your data is {completeness:.1f}% complete",
            "confidence": 0.95,
            "data": {"completeness_percentage": completeness}
        })

        # Schema detection insight
        detected_fields = len(schema)
        expected_fields = 10  # Common CRM fields
        schema_coverage = min(detected_fields / expected_fields, 1.0) * 100

        insights.append({
            "type": "schema_detection",
            "title": "CRM Field Detection",
            "description": f"Detected {detected_fields} standard CRM fields",
            "confidence": 0.9,
            "data": {
                "detected_fields": list(schema.keys()),
                "coverage": schema_coverage
            }
        })

        # Data quality insight
        if issues:
            severity_counts = {}
            for issue in issues:
                severity = issue.get("severity", "info")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            insights.append({
                "type": "data_quality",
                "title": "Data Quality Analysis",
                "description": f"Found {len(issues)} data quality considerations",
                "confidence": 0.85,
                "data": {
                    "total_issues": len(issues),
                    "by_severity": severity_counts
                }
            })

        # Use Claude for advanced insights if available
        if self.client and len(df) > 10:
            prompt = f"""
            Analyze this CRM data structure and provide one key insight:
            Columns: {list(df.columns)}
            Schema detected: {schema}
            Data types: {df.dtypes.to_dict()}
            Row count: {len(df)}

            Provide a brief, actionable insight about this data.
            """

            ai_insight = await self.think(prompt)
            if ai_insight:
                insights.append({
                    "type": "ai_analysis",
                    "title": "AI Data Analysis",
                    "description": ai_insight[:200],
                    "confidence": 0.75,
                    "data": {}
                })

        return insights

    def _calculate_data_quality_score(self, issues: List[Dict]) -> float:
        """Calculate overall data quality score"""
        if not issues:
            return 1.0

        # Weight issues by severity
        severity_weights = {
            "error": 0.3,
            "warning": 0.2,
            "info": 0.1
        }

        total_penalty = 0
        for issue in issues:
            severity = issue.get("severity", "info")
            total_penalty += severity_weights.get(severity, 0.1)

        # Cap the penalty at 0.5
        total_penalty = min(total_penalty, 0.5)

        return 1.0 - total_penalty