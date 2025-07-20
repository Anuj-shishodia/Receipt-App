import base64
from io import BytesIO
from PIL import Image # For images
import PyPDF2 # For PDFs (can also use pdfminer.six or fitz/PyMuPDF)
import fitz # PyMuPDF for more robust PDF text extraction

def decode_base64_file(base64_string: str) -> bytes:
    return base64.b64decode(base64_string)

def extract_text_from_file(file_content: bytes, file_type: str) -> str:
    text = ""
    if "image" in file_type:
        try:
            # Requires Tesseract OCR installed on the system
            # and pytesseract Python package
            from pytesseract import image_to_string
            img = Image.open(BytesIO(file_content))
            text = image_to_string(img)
        except ImportError:
            print("Pytesseract not installed or Tesseract not found. Skipping OCR.")
            text = "Pytesseract not configured or Tesseract not found on system path."
        except Exception as e:
            print(f"Error processing image with OCR: {e}")
            text = f"Error during OCR: {e}"
    elif "pdf" in file_type:
        try:
            doc = fitz.open(stream=file_content, filetype="pdf")
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"Error processing PDF: {e}")
            text = f"Error during PDF text extraction: {e}"
    elif "text" in file_type:
        text = file_content.decode('utf-8')
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    return text