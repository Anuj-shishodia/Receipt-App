from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.data_storage.database import init_db
from backend.api.routes import router as receipt_router

app = FastAPI(
    title="Receipt Processing API",
    description="API for uploading, parsing, storing, searching, sorting, and aggregating receipt data."
)

# Define the list of allowed origins
# IMPORTANT: These should match the exact URLs where your frontend will be running.
origins = [
    "http://localhost",         # Base localhost (sometimes used by dev servers)
    "http://localhost:3000",    # Common for React/Vue/Angular dev servers
    "http://localhost:8501",    # Default port for Streamlit applications
    # If your frontend is deployed elsewhere, add its production URL here too:
    # "https://your-frontend-domain.com",
    # "http://127.0.0.1:8501", # Sometimes 127.0.0.1 instead of localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # List of origins that are allowed to make requests
    allow_credentials=True,         # Allow cookies to be included in cross-origin requests
    allow_methods=["*"],            # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],            # Allow all HTTP headers in the request
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(receipt_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
