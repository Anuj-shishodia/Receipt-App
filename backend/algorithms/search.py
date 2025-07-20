from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from backend.data_storage.database import ReceiptDB
from datetime import date
from typing import List, Optional

def search_receipts(db: Session, query: Optional[str] = None, start_date: Optional[date] = None,
                    end_date: Optional[date] = None, min_amount: Optional[float] = None,
                    max_amount: Optional[float] = None, category: Optional[str] = None) -> List[ReceiptDB]:
    query_obj = db.query(ReceiptDB)

    if query:
        query_obj = query_obj.filter(
            (func.lower(ReceiptDB.vendor).contains(func.lower(query))) |
            (func.lower(ReceiptDB.category).contains(func.lower(query)))
        )
    if start_date:
        query_obj = query_obj.filter(ReceiptDB.transaction_date >= start_date)
    if end_date:
        query_obj = query_obj.filter(ReceiptDB.transaction_date <= end_date)
    if min_amount:
        query_obj = query_obj.filter(ReceiptDB.amount >= min_amount)
    if max_amount:
        query_obj = query_obj.filter(ReceiptDB.amount <= max_amount)
    if category:
        query_obj = query_obj.filter(func.lower(ReceiptDB.category) == func.lower(category))

    return query_obj.all()