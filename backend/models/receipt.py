from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class ReceiptData(BaseModel):
    vendor: str = Field(..., description="Name of the vendor or biller")
    transaction_date: date = Field(..., description="Date of the transaction or billing period")
    amount: float = Field(..., gt=0, description="Total amount of the transaction")
    category: Optional[str] = Field(None, description="Category of expenditure (e.g., Groceries, Electricity)")

class ReceiptInput(BaseModel):
    file_name: str
    file_content_base64: str # Base64 encoded file content
    file_type: str # e.g., 'image/jpeg', 'application/pdf', 'text/plain'