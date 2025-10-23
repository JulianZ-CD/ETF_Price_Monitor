from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import etf_router

### Create FastAPI instance with custom docs and openapi url
# API versioning included in router prefixes
app = FastAPI(
    title="ETF Price Monitor API",
    description="API for analyzing ETF constituents and calculating historical prices",
    version="1.0.0",
    docs_url="/api/py/docs",
    openapi_url="/api/py/openapi.json"
)

# Configure CORS to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins like ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(etf_router.router)

# Root endpoint - provides API information
@app.get("/api/py")
def api_root():
    """
    API root endpoint.
    Returns basic API information and available versions.
    """
    return {
        "name": "ETF Price Monitor API",
        "version": "1.0.0",
        "versions": {
            "v1": "/api/py/v1"
        },
        "documentation": "/docs"
    }