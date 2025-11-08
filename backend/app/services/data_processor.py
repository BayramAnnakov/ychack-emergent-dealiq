"""
Data processing service for CRM data
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

from app.core.config import settings


class DataProcessor:
    """Service for processing and analyzing CRM data"""

    @staticmethod
    def get_basic_stats(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get basic statistics from a dataframe
        """
        stats = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "null_counts": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict(),
        }

        # Add numeric column statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            stats["numeric_summary"] = df[numeric_cols].describe().to_dict()

        # Add date column info if any
        date_cols = df.select_dtypes(include=["datetime64"]).columns
        if len(date_cols) > 0:
            date_stats = {}
            for col in date_cols:
                date_stats[col] = {
                    "min": str(df[col].min()),
                    "max": str(df[col].max()),
                    "unique": df[col].nunique()
                }
            stats["date_columns"] = date_stats

        return stats

    @staticmethod
    def detect_crm_schema(df: pd.DataFrame) -> Dict[str, str]:
        """
        Detect common CRM fields in the dataframe
        """
        columns = df.columns.str.lower().tolist()
        schema = {}

        # Common CRM field patterns
        patterns = {
            "deal_id": ["deal_id", "opportunity_id", "opp_id", "deal", "id"],
            "deal_name": ["deal_name", "opportunity_name", "opp_name", "name", "title"],
            "amount": ["amount", "value", "deal_value", "revenue", "price", "arr", "mrr"],
            "stage": ["stage", "deal_stage", "status", "pipeline_stage", "phase"],
            "close_date": ["close_date", "closed_date", "expected_close", "closing_date"],
            "created_date": ["created_date", "created_at", "creation_date", "opened_date"],
            "owner": ["owner", "sales_rep", "assigned_to", "account_executive", "ae"],
            "account": ["account", "company", "customer", "client", "organization"],
            "probability": ["probability", "win_probability", "likelihood", "confidence"],
            "source": ["source", "lead_source", "origin", "channel"],
        }

        for field, keywords in patterns.items():
            for col in columns:
                if any(keyword in col for keyword in keywords):
                    schema[field] = df.columns[columns.index(col)]
                    break

        return schema

    @staticmethod
    def clean_data(df: pd.DataFrame, schema: Dict[str, str]) -> pd.DataFrame:
        """
        Clean and standardize CRM data
        """
        df_clean = df.copy()

        # Clean amount fields
        if "amount" in schema:
            amount_col = schema["amount"]
            if amount_col in df_clean.columns:
                # Remove currency symbols and convert to float
                df_clean[amount_col] = df_clean[amount_col].replace(
                    r'[\$,£,€,¥,]', '', regex=True
                ).astype(float, errors="ignore")

        # Parse dates
        date_fields = ["close_date", "created_date"]
        for field in date_fields:
            if field in schema and schema[field] in df_clean.columns:
                df_clean[schema[field]] = pd.to_datetime(
                    df_clean[schema[field]],
                    errors="coerce"
                )

        # Standardize stage names
        if "stage" in schema and schema["stage"] in df_clean.columns:
            df_clean[schema["stage"]] = df_clean[schema["stage"]].str.strip().str.title()

        # Remove complete duplicates
        df_clean = df_clean.drop_duplicates()

        return df_clean

    @staticmethod
    def calculate_pipeline_metrics(df: pd.DataFrame, schema: Dict[str, str]) -> Dict[str, Any]:
        """
        Calculate key pipeline metrics
        """
        metrics = {}

        # Total pipeline value
        if "amount" in schema:
            amount_col = schema["amount"]
            metrics["total_pipeline_value"] = float(df[amount_col].sum())
            metrics["average_deal_size"] = float(df[amount_col].mean())
            metrics["median_deal_size"] = float(df[amount_col].median())

        # Deal count by stage
        if "stage" in schema:
            stage_col = schema["stage"]
            metrics["deals_by_stage"] = df[stage_col].value_counts().to_dict()

        # Win rate (if we have closed deals)
        if "stage" in schema:
            stage_col = schema["stage"]
            closed_won_keywords = ["closed won", "won", "closed-won", "success"]
            closed_lost_keywords = ["closed lost", "lost", "closed-lost", "failed"]

            stage_lower = df[stage_col].str.lower()
            won_deals = stage_lower.isin(closed_won_keywords).sum()
            lost_deals = stage_lower.isin(closed_lost_keywords).sum()

            if (won_deals + lost_deals) > 0:
                metrics["win_rate"] = won_deals / (won_deals + lost_deals)

        # Sales velocity metrics
        if "created_date" in schema and "close_date" in schema:
            created_col = schema["created_date"]
            close_col = schema["close_date"]

            # Only for closed deals
            closed_deals = df[df[close_col].notna()]
            if len(closed_deals) > 0:
                closed_deals["cycle_length"] = (
                    pd.to_datetime(closed_deals[close_col]) -
                    pd.to_datetime(closed_deals[created_col])
                ).dt.days

                metrics["average_sales_cycle"] = float(closed_deals["cycle_length"].mean())
                metrics["median_sales_cycle"] = float(closed_deals["cycle_length"].median())

        return metrics

    @staticmethod
    def load_file(file_id: str) -> pd.DataFrame:
        """
        Load a file by ID from the uploads directory
        """
        # Find the file
        file_patterns = [f"{file_id}{ext}" for ext in settings.ALLOWED_EXTENSIONS]
        file_path = None

        for pattern in file_patterns:
            potential_path = os.path.join(settings.UPLOAD_DIR, pattern)
            if os.path.exists(potential_path):
                file_path = potential_path
                break

        if not file_path:
            raise FileNotFoundError(f"File with ID {file_id} not found")

        # Load based on extension
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".csv":
            return pd.read_csv(file_path)
        elif ext in [".xlsx", ".xls"]:
            return pd.read_excel(file_path)
        elif ext == ".json":
            return pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")