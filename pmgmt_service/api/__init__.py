"""
API module for the Patch Management Service.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
import datetime
import uuid

from ..db.models import Host, UpdateRun, PackageUpdate
from ..dependencies import get_db

router = APIRouter(prefix="/api")

# API key authentication
API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)


async def get_host_from_api_key(
    api_key_header: str = Depends(API_KEY_HEADER),
    db: Session = Depends(get_db)
):
    """
    Validate API key and return the associated host.
    
    Args:
        api_key_header (str): API key from the Authorization header.
        db (Session): Database session.
        
    Returns:
        Host: Host associated with the API key.
        
    Raises:
        HTTPException: If the API key is invalid or missing.
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract the key from the header (format: "Bearer <api_key>")
    if api_key_header.startswith("Bearer "):
        api_key = api_key_header[7:]
    else:
        api_key = api_key_header
    
    host = db.query(Host).filter(Host.api_key == api_key).first()
    if not host:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return host


@router.post("/updates")
async def receive_updates(
    data: dict,
    host: Host = Depends(get_host_from_api_key),
    db: Session = Depends(get_db)
):
    """
    Receive update information from a host.
    
    Args:
        data (dict): Update data from the host.
        host (Host): Host associated with the API key.
        db (Session): Database session.
        
    Returns:
        dict: Response indicating success.
    """
    try:
        # Parse timestamp
        timestamp = datetime.datetime.fromisoformat(data.get("timestamp"))
        
        # Get distribution info
        distribution = data.get("distribution", {})
        
        # Create update run
        update_run = UpdateRun(
            id=str(uuid.uuid4()),
            host_id=host.id,
            timestamp=timestamp,
            distribution_id=distribution.get("id", "unknown"),
            distribution_version=distribution.get("version", "unknown"),
            distribution_name=distribution.get("name", "unknown"),
            package_manager=distribution.get("package_manager", "unknown"),
            total_updates=data.get("total_updates", 0),
            security_updates=data.get("security_updates", 0)
        )
        
        db.add(update_run)
        
        # Add package updates
        for update_data in data.get("updates", []):
            # Extract common fields
            package_update = PackageUpdate(
                id=str(uuid.uuid4()),
                update_run_id=update_run.id,
                name=update_data.get("name", ""),
                version=update_data.get("version", ""),
                current_version=update_data.get("current_version", ""),
                architecture=update_data.get("architecture", ""),
                is_security_update=update_data.get("is_security_update", False),
                website=update_data.get("website", None),
                description=update_data.get("description", None),
            )
            
            # Handle size field which might be in different formats
            if "size_bytes" in update_data:
                package_update.size = str(update_data["size_bytes"])
            elif "size" in update_data:
                package_update.size = update_data["size"]
            
            # Store any additional fields as JSON
            additional_info = {k: v for k, v in update_data.items() if k not in [
                "name", "version", "current_version", "architecture", 
                "is_security_update", "website", "description", "size", "size_bytes"
            ]}
            
            if additional_info:
                package_update.additional_info = additional_info
            
            db.add(package_update)
        
        # Update host last_seen timestamp
        host.last_seen = datetime.datetime.utcnow()
        
        # Commit changes
        db.commit()
        
        return {"status": "success", "message": "Update information received"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing update data: {str(e)}"
        )