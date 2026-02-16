"""
AI Data Labs - Backend API
FastAPI application for the AI Data Labs platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Data Labs API",
    description="AI-first data infrastructure platform",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Data Labs API",
        "version": "1.0.0",
        "status": "operational",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/v1/status")
async def status():
    """API status endpoint"""
    return {
        "status": "operational",
        "services": {
            "clickhouse": "connected",
            "postgresql": "connected",
            "kafka": "connected",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
