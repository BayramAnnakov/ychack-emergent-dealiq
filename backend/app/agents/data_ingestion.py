"""
Data Ingestion Agent - AI-powered data parsing and analysis using Claude SDK
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import json

from app.agents.base import BaseAgent


class DataIngestionAgent(BaseAgent):
    """AI-powered agent for intelligent CRM data analysis"""

    def __init__(self):
        super().__init__(
            name="DataIngestionAgent",
            description="AI-powered CRM data analysis and insight extraction",
            tools=[]  # No special tools needed for data analysis
        )

    async def process(self, data: Any, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process incoming data using AI analysis"""
        if isinstance(data, pd.DataFrame):
            df = data
        else:
            # Attempt to convert to DataFrame
            df = self._convert_to_dataframe(data)

        # Prepare data summary for AI analysis
        data_summary = self._prepare_data_summary(df)

        # Use AI to analyze the data structure and content
        schema_analysis = await self._ai_analyze_schema(df, data_summary)

        # Use AI to detect data quality issues
        quality_analysis = await self._ai_analyze_quality(df, data_summary)

        # Use AI to generate initial insights
        initial_insights = await self._ai_generate_insights(df, data_summary, context)

        return {
            "status": "success",
            "schema": schema_analysis.get("schema", {}),
            "stats": data_summary,
            "quality_analysis": quality_analysis,
            "insights": initial_insights,
            "confidence": schema_analysis.get("confidence", 0.8),
            "output_data": df  # Pass data to next agent
        }

    def _convert_to_dataframe(self, data: Any) -> pd.DataFrame:
        """Convert various data formats to DataFrame"""
        if isinstance(data, dict):
            return pd.DataFrame(data)
        elif isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, str):
            try:
                json_data = json.loads(data)
                return pd.DataFrame(json_data)
            except:
                raise ValueError("Unable to parse string data")
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")

    def _prepare_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Prepare comprehensive data summary for AI analysis"""
        summary = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "sample_data": df.head(10).to_dict('records') if len(df) > 0 else [],
            "null_counts": df.isnull().sum().to_dict(),
            "unique_counts": {col: df[col].nunique() for col in df.columns},
        }

        # Add numeric statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            summary["numeric_stats"] = df[numeric_cols].describe().to_dict()

        # Add categorical statistics
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            summary["categorical_samples"] = {
                col: df[col].value_counts().head(5).to_dict()
                for col in categorical_cols[:10]  # Limit to first 10 categorical columns
            }

        return summary

    async def _ai_analyze_schema(self, df: pd.DataFrame, data_summary: Dict) -> Dict[str, Any]:
        """Use AI to intelligently detect CRM schema"""
        prompt = f"""
        Analyze this sales/CRM data and identify the schema mapping.

        Data Summary:
        - Columns: {data_summary['columns']}
        - Data Types: {data_summary['dtypes']}
        - Sample Row: {json.dumps(data_summary['sample_data'][0] if data_summary['sample_data'] else {}, indent=2)}
        - Unique Counts: {data_summary['unique_counts']}

        Identify which columns map to these common CRM fields:
        - deal_id: Unique identifier for deals/opportunities
        - deal_name: Name/title of the deal
        - amount: Deal value/revenue
        - stage: Sales stage/phase
        - close_date: Expected/actual close date
        - created_date: Deal creation date
        - owner: Sales rep/owner
        - account: Company/customer name
        - probability: Win probability
        - source: Lead/deal source

        Also identify any other important sales-related fields in the data.

        Return your analysis as a JSON object with:
        1. "schema": mapping of CRM fields to actual column names
        2. "confidence": your confidence level (0-1)
        3. "additional_fields": other important fields found
        4. "data_type": type of CRM data (e.g., "opportunities", "leads", "accounts")
        5. "recommendations": suggestions for data usage

        Be thorough and use context clues from column names and data values.
        """

        response = await self.think(prompt)

        try:
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        # Fallback structure if JSON parsing fails
        return {
            "schema": self._basic_schema_detection(df),
            "confidence": 0.7,
            "analysis": response[:500]
        }

    async def _ai_analyze_quality(self, df: pd.DataFrame, data_summary: Dict) -> Dict[str, Any]:
        """Use AI to analyze data quality issues"""
        prompt = f"""
        Analyze the quality of this sales/CRM data and identify issues.

        Data Statistics:
        - Total Rows: {data_summary['shape'][0]}
        - Total Columns: {data_summary['shape'][1]}
        - Null Values: {data_summary['null_counts']}
        - Data Types: {data_summary['dtypes']}

        Sample Data:
        {json.dumps(data_summary['sample_data'][:3], indent=2) if data_summary['sample_data'] else 'No data'}

        Identify and analyze:
        1. Data completeness issues
        2. Data consistency problems
        3. Potential duplicates or anomalies
        4. Missing critical fields for sales analysis
        5. Data quality score (0-100)
        6. Specific recommendations for data cleaning

        Consider sales best practices and what data is needed for:
        - Pipeline analysis
        - Forecasting
        - Performance tracking
        - Win/loss analysis

        Provide actionable insights about the data quality.
        """

        response = await self.think(prompt)

        return {
            "analysis": response,
            "quality_score": self._extract_quality_score(response)
        }

    async def _ai_generate_insights(self, df: pd.DataFrame, data_summary: Dict, context: Optional[Dict]) -> List[Dict[str, Any]]:
        """Use AI to generate initial insights from the data"""
        user_query = context.get("query", "") if context else ""

        prompt = f"""
        Analyze this sales/CRM data and generate actionable insights.

        Data Overview:
        - {data_summary['shape'][0]} total records
        - Key columns: {', '.join(data_summary['columns'][:15])}

        Numeric Statistics:
        {json.dumps(data_summary.get('numeric_stats', {}), indent=2) if 'numeric_stats' in data_summary else 'No numeric data'}

        Categorical Patterns:
        {json.dumps(data_summary.get('categorical_samples', {}), indent=2) if 'categorical_samples' in data_summary else 'No categorical data'}

        {"User Query: " + user_query if user_query else ""}

        Generate 5-7 specific, actionable insights about:
        1. Overall pipeline health
        2. Key trends or patterns in the data
        3. Potential risks or opportunities
        4. Performance indicators
        5. Data anomalies or interesting findings
        6. Recommendations for sales strategy

        For each insight, provide:
        - A clear, specific observation
        - The business impact
        - A recommended action
        - Confidence level (high/medium/low)

        Focus on insights that would help sales teams improve performance and close more deals.
        """

        response = await self.think(prompt)

        # Parse response into structured insights
        insights = self._parse_insights_response(response)

        return insights

    def _basic_schema_detection(self, df: pd.DataFrame) -> Dict[str, str]:
        """Basic fallback schema detection"""
        schema = {}
        columns = df.columns.str.lower().tolist()

        # Simple pattern matching as fallback
        patterns = {
            "deal_id": ["id", "deal_id", "opportunity_id"],
            "amount": ["amount", "value", "revenue"],
            "stage": ["stage", "status", "phase"],
            "owner": ["owner", "rep", "assigned"],
        }

        for field, keywords in patterns.items():
            for col in df.columns:
                if any(keyword in col.lower() for keyword in keywords):
                    schema[field] = col
                    break

        return schema

    def _extract_quality_score(self, response: str) -> float:
        """Extract quality score from AI response"""
        import re
        # Look for patterns like "score: 75" or "75/100" or "75%"
        patterns = [
            r'score[:\s]+(\d+)',
            r'(\d+)/100',
            r'(\d+)%',
            r'quality[:\s]+(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, response.lower())
            if match:
                score = float(match.group(1))
                return min(score / 100 if score > 1 else score, 1.0)

        return 0.7  # Default score if not found

    def _parse_insights_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured insights"""
        insights = []

        # Split response into sections (assuming bullet points or numbered list)
        import re
        sections = re.split(r'\n\d+\.|^\d+\.|\n-|^-', response)

        for i, section in enumerate(sections[:7]):  # Limit to 7 insights
            if len(section.strip()) > 20:  # Filter out empty sections
                insights.append({
                    "type": "data_ingestion",
                    "title": f"Data Insight {i+1}",
                    "description": section.strip()[:300],
                    "confidence": 0.8 - (i * 0.05),  # Slightly decrease confidence for later insights
                    "source": "DataIngestionAgent",
                    "data": {}
                })

        # If no insights were parsed, create one from the whole response
        if not insights and response:
            insights.append({
                "type": "data_ingestion",
                "title": "Initial Data Analysis",
                "description": response[:500],
                "confidence": 0.7,
                "source": "DataIngestionAgent",
                "data": {}
            })

        return insights