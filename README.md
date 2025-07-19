# Full-Stack Receipt Processor

This project develops a full-stack mini-application for uploading receipts and bills, extracting structured data using rule-based logic and OCR, and presenting summarized insights through an interactive dashboard. The backend is built with FastAPI, using SQLite for data storage, and the frontend dashboard is powered by Streamlit.

## Project Architecture

The application follows a modular architecture to handle various stages of receipt processing. The core components include a backend for data handling and processing, an OCR pipeline for text extraction, a database for persistent storage, and a Streamlit dashboard for user interaction and visualization.

![Full-Stack Receipt Processor Architecture]
<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/f5aa7f7a-fed8-4a76-954b-b424f54cacbd" />


[cite_start]*Figure: High-level architecture diagram of the Full-Stack Receipt Processor.* [cite: 1]

### Key Modules:

* [cite_start]**Backend Modules**: Handles the core API logic, authentication (conceptual), and data validation. [cite: 1]
    * [cite_start]**Receipt API**: Manages endpoints for uploading, retrieving, searching, sorting, and aggregating receipt data. [cite: 1]
    * [cite_start]**Auth Service**: (Conceptual/Placeholder) For user authentication. [cite: 1]
    * [cite_start]**Validation Service**: Ensures data integrity using formal type-checking (e.g., Pydantic models). [cite: 1]
* [cite_start]**OCR Pipeline**: Processes image and PDF files to extract raw text. [cite: 1]
    * [cite_start]**Image Preprocessing**: Prepares images for optimal text extraction. [cite: 1]
    * [cite_start]**Text Extraction**: Utilizes OCR (e.g., Tesseract) to convert images/PDFs into text. [cite: 1]
    * [cite_start]**Postprocessing**: Cleans and refines the extracted text. [cite: 1]
* [cite_start]**Database**: Stores extracted structured data in a normalized relational form. [cite: 1]
    * **PostgreSQL**: (As per diagram, but SQLite is used in the provided code examples for simplicity and lightweight setup). [cite_start]Ensures ACID compliance and indexing for optimized search performance. [cite: 1]
* [cite_start]**Streamlit Dashboard**: Provides an interactive user interface for managing and visualizing receipt data. [cite: 1]
    * [cite_start]Displays uploaded receipts with extracted fields. [cite: 1]
    * [cite_start]Presents statistical visualizations like categorical distributions and time-series expenditure graphs. [cite: 1]

## Features

### Backend / Processing Layer
* [cite_start]**Data Ingestion**: Handles heterogeneous file formats (`.jpg`, `.png`, `.pdf`, `.txt`). [cite: 1]
* [cite_start]**Data Parsing**: Extracts structured data fields: Vendor/Biller, Date of Transaction/Billing Period, Amount, and Category. [cite: 1]
* [cite_start]**Data Storage**: Stores extracted data in a lightweight relational database (SQLite in current implementation, easily convertible to PostgreSQL if desired) with ACID compliance and indexing. [cite: 1]

### Algorithmic Implementation
* **Search Algorithms**: Keyword-, range-, and pattern-based search mechanisms using string matching and comparison operators. [cite_start]Implements linear search and, where appropriate, hashed indexing for optimization. [cite: 1]
* [cite_start]**Sorting Algorithms**: Enables sorting based on numerical (Amount) and categorical (Vendor, Category) fields. [cite: 1]
* [cite_start]**Aggregation Functions**: Computes statistical aggregates such as sum, mean, median, mode of expenditure, frequency distributions of vendor occurrences, and time-series aggregations (e.g., monthly spend trend). [cite: 1]

### Dashboard / UI (Streamlit)
* [cite_start]**Tabular View**: Displays individual records with parsed fields. [cite: 1]
* [cite_start]**Statistical Visualizations**: Categorical distributions via bar/pie charts and time-series expenditure graphs using line charts. [cite: 1]
* **File Upload Interface**: Intuitive interface for uploading receipt and bill files.

### Validation & Error Handling
* [cite_start]Applies formal validation rules on file types, parsing logic, and data schemas (using Pydantic models). [cite: 1]
* [cite_start]Uses exception handling to provide informative feedback without halting system operations. [cite: 1]

### Bonus Features (Implemented)
* [cite_start]**Manual Correction**: Allows users to manually correct parsed fields via the UI. [cite: 1]
* [cite_start]**Data Export**: Enables exporting summaries as `.csv` or `.json` files. [cite: 1]

## Setup and Installation Guide

Follow these steps to set up and run the Full-Stack Receipt Processor on your local machine.

### Prerequisites

* **Python 3.9+**: Download from [python.org](https://www.python.org/).
* **Tesseract OCR**: Essential for image and PDF text extraction.
    * **Windows**: Download installer from [Tesseract-OCR GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki). Make sure to add it to your system's PATH during installation.
    * **macOS**: `brew install tesseract`
    * **Linux (Debian/Ubuntu)**: `sudo apt-get install tesseract-ocr`
* **Node.js & npm / yarn** (Only if you opt for a React frontend, not needed for Streamlit).

### 1. Clone the Repository (or create project structure)

If you haven't already, create the project directories and files as outlined in the project setup guide. Assume your project root is `receipt_app`.

```bash
# Example for creating directories (for Windows, use `mkdir` and create `__init__.py` files with New-Item)
mkdir receipt_app
cd receipt_app

# Create backend directories
mkdir -p backend/data_ingestion
mkdir -p backend/data_parsing
mkdir -p backend/data_storage
mkdir -p backend/algorithms
mkdir -p backend/models
mkdir -p backend/api

# Create frontend directory for Streamlit
mkdir -p frontend

# Create __init__.py files (for Windows PowerShell: New-Item -Path "path/to/file/__init__.py" -ItemType File)
touch backend/__init__.py
touch backend/data_ingestion/__init__.py
touch backend/data_parsing/__init__.py
touch backend/data_storage/__init__.py
touch backend/algorithms/__init__.py
touch backend/models/__init__.py
touch backend/api/__init__.py

# Create requirements.txt and Streamlit app file
touch requirements.txt
touch frontend/app.py
touch backend/main.py
