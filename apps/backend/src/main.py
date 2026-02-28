"""
AI Data Labs - Backend API
FastAPI application for the AI Data Labs platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from api.v1 import auth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Data Labs API",
    description="AI-first data infrastructure platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)
app.include_router(auth.router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting AI Data Labs API...")
    # Initialize default admin user
    from auth.service import AuthService
    await AuthService.create_default_admin()
    logger.info("API ready to serve requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down AI Data Labs API...")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Data Labs API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/api/docs",
        "health": "/health"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            "auth": "operational"
        }
    }


@app.get("/api/v1/status")
async def status():
    """API status endpoint"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "services": {
            "clickhouse": "not configured",
            "postgresql": "not configured",
            "kafka": "not configured",
        },
    }




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
