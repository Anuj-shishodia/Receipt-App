from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from backend.models.receipt import ReceiptData, ReceiptInput
from backend.data_storage.database import get_db, ReceiptDB
from backend.data_ingestion.file_handler import extract_text_from_file, decode_base64_file
from backend.data_parsing.rule_parser import parse_receipt_data
from backend.algorithms.search import search_receipts
from backend.algorithms.sort import sort_receipts
from backend.algorithms.aggregate import calculate_aggregates
from datetime import date
import base64
import io
import csv
import json
from fastapi.responses import StreamingResponse
from typing import Optional, List

router = APIRouter()

@router.post("/upload_receipt/")
async def upload_receipt(receipt_input: ReceiptInput, db: Session = Depends(get_db)):
    try:
        file_content_bytes = decode_base64_file(receipt_input.file_content_base64)
        extracted_text = extract_text_from_file(file_content_bytes, receipt_input.file_type)
        parsed_data = parse_receipt_data(extracted_text)

        # Ensure all required fields for ReceiptData are present, even if None
        # Pydantic will validate based on its schema
        receipt_data_dict = {
            "vendor": parsed_data.get("vendor"),
            "transaction_date": parsed_data.get("transaction_date"),
            "amount": parsed_data.get("amount"),
            "category": parsed_data.get("category")
        }

        # Validate with Pydantic model
        validated_data = ReceiptData(**receipt_data_dict)

        db_receipt = ReceiptDB(
            vendor=validated_data.vendor,
            transaction_date=validated_data.transaction_date,
            amount=validated_data.amount,
            category=validated_data.category
        )
        db.add(db_receipt)
        db.commit()
        db.refresh(db_receipt)
        return {"message": "Receipt uploaded and processed successfully!", "data": validated_data.dict()}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to process receipt: {e}")

@router.get("/receipts/", response_model=List[ReceiptData])
def get_receipts(
    db: Session = Depends(get_db),
    query: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    category: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
):
    receipts = search_receipts(db, query, start_date, end_date, min_amount, max_amount, category)

    if sort_by:
        try:
            # Re-query with sort for efficiency, rather than sorting in-memory if possible
            # If search_receipts already returned a filtered list, you might sort that in-memory
            # For simplicity here, we re-apply sort directly on the DB query for `search_receipts`
            # or you can load all and then sort in memory if the dataset is small.
            # For this example, search_receipts fetches all matching, so sorting in-memory is fine.
            receipts = sort_receipts(db, sort_by, sort_order) # This will re-query and sort everything if no filters
            # A more correct approach would be to apply sorting on the result of search_receipts:
            # receipts_filtered = search_receipts(...)
            # receipts = sort_receipts_in_memory(receipts_filtered, sort_by, sort_order)
            # But for API, it's better to build the query chain directly for performance.
            # Let's adjust search_receipts/sort_receipts to work with query objects.
            # For now, `sort_receipts` as provided operates on the whole table.
            # To combine:
            base_query = db.query(ReceiptDB)
            if query:
                base_query = base_query.filter(
                    (func.lower(ReceiptDB.vendor).contains(func.lower(query))) |
                    (func.lower(ReceiptDB.category).contains(func.lower(query)))
                )
            if start_date:
                base_query = base_query.filter(ReceiptDB.transaction_date >= start_date)
            if end_date:
                base_query = base_query.filter(ReceiptDB.transaction_date <= end_date)
            if min_amount:
                base_query = base_query.filter(ReceiptDB.amount >= min_amount)
            if max_amount:
                base_query = base_query.filter(ReceiptDB.amount <= max_amount)
            if category:
                base_query = base_query.filter(func.lower(ReceiptDB.category) == func.lower(category))

            if sort_by == "vendor":
                if sort_order == "asc": base_query = base_query.order_by(ReceiptDB.vendor.asc())
                else: base_query = base_query.order_by(ReceiptDB.vendor.desc())
            elif sort_by == "date":
                if sort_order == "asc": base_query = base_query.order_by(ReceiptDB.transaction_date.asc())
                else: base_query = base_query.order_by(ReceiptDB.transaction_date.desc())
            elif sort_by == "amount":
                if sort_order == "asc": base_query = base_query.order_by(ReceiptDB.amount.asc())
                else: base_query = base_query.order_by(ReceiptDB.amount.desc())
            elif sort_by == "category":
                if sort_order == "asc": base_query = base_query.order_by(ReceiptDB.category.asc())
                else: base_query = base_query.order_by(ReceiptDB.category.desc())
            else:
                raise ValueError("Invalid sort_by field") # Should be caught by the outer try-except

            receipts = base_query.all()

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


    # Convert SQLAlchemy models to Pydantic models for response
    return [ReceiptData.from_orm(r) for r in receipts]

@router.get("/receipts/aggregates/")
def get_receipt_aggregates(db: Session = Depends(get_db)):
    aggregates = calculate_aggregates(db)
    return aggregates

@router.put("/receipts/{receipt_id}/", response_model=ReceiptData)
def update_receipt(receipt_id: int, receipt_data: ReceiptData, db: Session = Depends(get_db)):
    db_receipt = db.query(ReceiptDB).filter(ReceiptDB.id == receipt_id).first()
    if not db_receipt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")

    # Update fields from the incoming Pydantic model
    for key, value in receipt_data.dict(exclude_unset=True).items():
        setattr(db_receipt, key, value)

    db.commit()
    db.refresh(db_receipt)
    return db_receipt

@router.get("/export_receipts/", response_class=StreamingResponse)
def export_receipts(db: Session = Depends(get_db), format: str = "csv"):
    receipts = db.query(ReceiptDB).all()
    # Convert SQLAlchemy objects to dicts, handling date types for JSON serialization
    data = []
    for r in receipts:
        r_dict = r.__dict__.copy()
        r_dict.pop('_sa_instance_state', None) # Remove SQLAlchemy internal state
        if 'transaction_date' in r_dict and isinstance(r_dict['transaction_date'], date):
            r_dict['transaction_date'] = r_dict['transaction_date'].isoformat()
        data.append(r_dict)

    if format == "csv":
        output = io.StringIO()
        # Ensure fieldnames match dictionary keys for CSV writing
        fieldnames = ["id", "vendor", "transaction_date", "amount", "category"] # Explicit order
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        output.seek(0)
        return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=receipts.csv"})
    elif format == "json":
        return StreamingResponse(io.BytesIO(json.dumps(data, indent=2, default=str).encode('utf-8')), media_type="application/json", headers={"Content-Disposition": "attachment; filename=receipts.json"})
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Choose 'csv' or 'json'.")