"""
Dependency injection for the Patch Management Service.
"""

import os
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from .db.models import get_engine, get_session_factory

# Create database engine and session factory
DB_PATH = os.environ.get("PMGMT_DB_PATH", "pmgmt.db")
engine = get_engine(DB_PATH)
SessionLocal = get_session_factory(engine)

# HTTP Basic authentication for the dashboard
security = HTTPBasic()


def get_db() -> Generator[Session, None, None]:
    """
    Get a database session.
    
    Yields:
        Session: Database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Validate user credentials for dashboard access.
    
    Args:
        credentials (HTTPBasicCredentials): User credentials.
        
    Returns:
        str: Username if credentials are valid.
        
    Raises:
        HTTPException: If credentials are invalid.
    """
    # Get username and password from environment variables
    username = os.environ.get("PMGMT_USERNAME")
    password = os.environ.get("PMGMT_PASSWORD")
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication not configured. Set PMGMT_USERNAME and PMGMT_PASSWORD environment variables."
        )
    
    if credentials.username != username or credentials.password != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username