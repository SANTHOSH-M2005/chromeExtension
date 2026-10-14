import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file BEFORE importing internal modules
load_dotenv()

from api.routes import router as api_router
from api.database import engine, Base
import api.models_db

# Ensure all database tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartConsent AI Backend",
    description="Backend for the SmartConsent AI browser extension",
    version="1.0.0"
)

# Configure CORS (Cross-Origin Resource Sharing)
# This is required so our Chrome Extension can communicate with this API
allowed_origins = os.getenv("ALLOWED_ORIGINS", "chrome-extension://*,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our API routes from api/routes.py
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "Backend is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "SmartConsent AI Backend"}

# If running directly (e.g. `python main.py`)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
