from sqlalchemy.orm import Session
from backend.data_storage.database import ReceiptDB
from datetime import date
from typing import List

def sort_receipts(db: Session, sort_by: str, sort_order: str = "asc") -> List[ReceiptDB]:
    query = db.query(ReceiptDB)
    if sort_by == "vendor":
        if sort_order == "asc":
            query = query.order_by(ReceiptDB.vendor.asc())
        else:
            query = query.order_by(ReceiptDB.vendor.desc())
    elif sort_by == "date":
        if sort_order == "asc":
            query = query.order_by(ReceiptDB.transaction_date.asc())
        else:
            query = query.order_by(ReceiptDB.transaction_date.desc())
    elif sort_by == "amount":
        if sort_order == "asc":
            query = query.order_by(ReceiptDB.amount.asc())
        else:
            query = query.order_by(ReceiptDB.amount.desc())
    elif sort_by == "category":
        if sort_order == "asc":
            query = query.order_by(ReceiptDB.category.asc())
        else:
            query = query.order_by(ReceiptDB.category.desc())
    else:
        # Default to ID or raise error depending on desired behavior
        # For this context, let's raise an error for invalid sort_by
        raise ValueError(f"Invalid sort_by field: {sort_by}")
    return query.all()

# Example of in-memory sorting if you get all records first (less efficient for large datasets)
def sort_receipts_in_memory(receipt_list: List[ReceiptDB], sort_by: str, sort_order: str = "asc") -> List[ReceiptDB]:
    reverse = (sort_order == "desc")
    if sort_by == "vendor":
        return sorted(receipt_list, key=lambda x: x.vendor or "", reverse=reverse)
    elif sort_by == "date":
        # Use a default min date if transaction_date can be None
        return sorted(receipt_list, key=lambda x: x.transaction_date or date.min, reverse=reverse)
    elif sort_by == "amount":
        return sorted(receipt_list, key=lambda x: x.amount or 0.0, reverse=reverse)
    elif sort_by == "category":
        return sorted(receipt_list, key=lambda x: x.category or "", reverse=reverse)
    else:
        raise ValueError(f"Invalid sort_by field for in-memory sort: {sort_by}")