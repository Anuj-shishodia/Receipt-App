import re
from datetime import datetime

def parse_receipt_data(text: str) -> dict:
    vendor = "Unknown Vendor"
    transaction_date = None
    amount = 0.0
    category = None

    # Example: Simple regex for vendor (very basic, needs refinement)
    vendor_patterns = [
        r"(?:Vendor|Store|Shop):\s*([A-Za-z0-9\s]+)",
        r"([A-Za-z\s]+)(?:\s+Supermarket|\s+Groceries|\s+Store)",
        r"Invoice from\s*([A-Za-z0-9\s]+)"
    ]
    for pattern in vendor_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            vendor = match.group(1).strip()
            break

    # Example: Date parsing (flexible patterns)
    date_patterns = [
        r"\d{1,2}/\d{1,2}/\d{2,4}",  # DD/MM/YYYY or DD/MM/YY
        r"\d{1,2}-\d{1,2}-\d{2,4}",  # DD-MM-YYYY or DD-MM-YY
        r"\d{4}-\d{2}-\d{2}",        # YYYY-MM-DD
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}" # Month Day, Year
    ]
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                date_str = match.group(0)
                if '/' in date_str:
                    transaction_date = datetime.strptime(date_str, '%d/%m/%Y').date()
                elif re.match(r"\d{4}-\d{2}-\d{2}", date_str):
                    transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                elif re.match(r"\d{1,2}-\d{1,2}-\d{2,4}", date_str):
                    # Try a few common formats for DD-MM-YY/YYYY
                    try:
                        transaction_date = datetime.strptime(date_str, '%d-%m-%Y').date()
                    except ValueError:
                        transaction_date = datetime.strptime(date_str, '%d-%m-%y').date()
                elif re.match(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", date_str, re.IGNORECASE):
                    # Attempt different year formats for "Month Day, Year"
                    try:
                        transaction_date = datetime.strptime(date_str, '%b %d, %Y').date()
                    except ValueError:
                        transaction_date = datetime.strptime(date_str, '%B %d, %Y').date()
                break
            except ValueError:
                continue

    # Example: Amount parsing (look for "Total", "Amount Due", etc.)
    amount_patterns = [
        r"(?:Total|Amount Due|Balance|Sum):\s*[$€£]?\s*(\d+(?:[.,]\d{2})?)",
        r"[$€£]?\s*(\d+(?:[.,]\d{2}?))\s*(?:Total|Amount Due|Balance|Sum)",
        r"(\d+(?:[.,]\d{2}?))\s*(?:USD|EUR|GBP)"
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                amount = float(match.group(1).replace(',', '.')) # Handle comma as decimal
                break
            except ValueError:
                continue

    # Optional: Basic category mapping
    if "grocery" in text.lower() or "supermarket" in text.lower() or "food" in text.lower():
        category = "Groceries"
    elif "electricity" in text.lower() or "power bill" in text.lower():
        category = "Utilities (Electricity)"
    elif "internet" in text.lower() or "broadband" in text.lower():
        category = "Utilities (Internet)"
    elif "water" in text.lower() or "utility" in text.lower():
        category = "Utilities (Water)"
    elif "restaurant" in text.lower() or "cafe" in text.lower():
        category = "Dining"
    elif "transport" in text.lower() or "fuel" in text.lower() or "petrol" in text.lower():
        category = "Transportation"


    return {
        "vendor": vendor,
        "transaction_date": transaction_date,
        "amount": amount,
        "category": category
    }