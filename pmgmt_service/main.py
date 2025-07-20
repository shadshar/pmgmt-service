"""
Main module for the Patch Management Service.
"""

import os
import logging
import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from .api import router as api_router
from .dashboard import router as dashboard_router
from .db.models import init_db
from .dependencies import get_current_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Patch Management Service",
    description="A service for collecting and displaying package update information",
    version="0.1.0"
)

# Include routers
app.include_router(api_router)
app.include_router(dashboard_router)

# Redirect root to dashboard
@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")


def main():
    """Main entry point for the service."""
    # Get port from environment variable
    port = int(os.environ.get("PMGMT_PORT", "3716"))
    
    # Initialize database
    db_path = os.environ.get("PMGMT_DB_PATH", "pmgmt.db")
    init_db(db_path)
    logger.info(f"Initialized database at {db_path}")
    
    # Check if authentication is configured
    username = os.environ.get("PMGMT_USERNAME")
    password = os.environ.get("PMGMT_PASSWORD")
    
    if not username or not password:
        logger.warning(
            "Authentication not configured. Set PMGMT_USERNAME and PMGMT_PASSWORD environment variables."
        )
    
    # Start the server
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()