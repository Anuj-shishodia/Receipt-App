import pandas as pd
from collections import Counter
from sqlalchemy.orm import Session
from backend.data_storage.database import ReceiptDB
from typing import Dict, Any, List

def calculate_aggregates(db: Session) -> Dict[str, Any]:
    receipts = db.query(ReceiptDB).all()
    if not receipts:
        return {
            "total_spend": 0.0,
            "mean_spend": 0.0,
            "median_spend": 0.0,
            "mode_spend": [],
            "vendor_frequency": {},
            "monthly_spend_trend": {}
        }

    # Convert SQLAlchemy objects to dictionaries for DataFrame creation
    # Using a list comprehension to ensure all attributes are available.
    data_for_df = []
    for r in receipts:
        receipt_dict = {
            'id': r.id,
            'vendor': r.vendor,
            'transaction_date': r.transaction_date,
            'amount': r.amount,
            'category': r.category
        }
        data_for_df.append(receipt_dict)

    df = pd.DataFrame(data_for_df)
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])

    # Sum, Mean, Median
    total_spend = df['amount'].sum()
    mean_spend = df['amount'].mean()
    median_spend = df['amount'].median()

    # Mode (can be multiple)
    mode_spend = df['amount'].mode().tolist()

    # Frequency distributions of vendor occurrences
    vendor_frequency = df['vendor'].value_counts().to_dict()

    # Monthly spend trend
    df['month_year'] = df['transaction_date'].dt.to_period('M')
    monthly_spend_trend = df.groupby('month_year')['amount'].sum().to_dict()
    # Convert Period objects to strings for JSON serialization
    monthly_spend_trend = {str(k): v for k, v in monthly_spend_trend.items()}

    return {
        "total_spend": total_spend,
        "mean_spend": mean_spend,
        "median_spend": median_spend,
        "mode_spend": mode_spend,
        "vendor_frequency": vendor_frequency,
        "monthly_spend_trend": monthly_spend_trend
    }