"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from database import SessionLocal, check_db_connection
from routes import tweets, handles
from services.twitter_service import TwitterService
from services.scheduler_service import SchedulerService

# Load environment variables
load_dotenv()

# Global scheduler instance
scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print("Starting Twitter Feed Display System...")
    
    # Check database connection
    if not check_db_connection():
        print("WARNING: Database connection failed!")
    else:
        print("Database connection successful")
    
    # Initialize services
    twitter_service = TwitterService()
    
    # Start scheduler
    global scheduler
    scheduler = SchedulerService(twitter_service, SessionLocal)
    scheduler.start()
    
    yield
    
    # Shutdown
    print("Shutting down...")
    if scheduler:
        scheduler.stop()

# Create FastAPI app
app = FastAPI(
    title="Twitter Feed Display System",
    description="Production-grade Twitter feed display with persistent deduplication",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tweets.router)
app.include_router(handles.router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Twitter Feed Display System API",
        "version": "1.0.0",
        "endpoints": {
            "tweets": "/api/tweets",
            "handles": "/api/handles",
            "docs": "/docs"
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_status = check_db_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected"
    }

# Manual refresh endpoint (triggers scheduler)
@app.post("/api/manual-refresh")
async def manual_refresh():
    """Manually trigger tweet fetch."""
    if scheduler:
        scheduler.trigger_manual_fetch()
        return {"message": "Manual refresh triggered"}
    return {"message": "Scheduler not initialized"}

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )
