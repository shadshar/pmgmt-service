"""
Dashboard module for the Patch Management Service.
"""

import secrets
import uuid
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from ..db.models import Host, UpdateRun, PackageUpdate
from ..dependencies import get_db, get_current_user

# Create router
router = APIRouter(prefix="/dashboard")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Helper function to generate API keys
def generate_api_key() -> str:
    """Generate a random API key."""
    return secrets.token_hex(32)


@router.get("/", response_class=HTMLResponse)
async def dashboard_home(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """
    Dashboard home page showing an overview of all hosts.
    """
    # Get all hosts with their latest update run
    hosts_with_updates = []
    
    hosts = db.query(Host).all()
    for host in hosts:
        latest_run = (
            db.query(UpdateRun)
            .filter(UpdateRun.host_id == host.id)
            .order_by(desc(UpdateRun.timestamp))
            .first()
        )
        
        hosts_with_updates.append({
            "id": host.id,
            "hostname": host.hostname,
            "last_seen": host.last_seen,
            "latest_run": latest_run
        })
    
    return templates.TemplateResponse(
        "dashboard/home.html",
        {
            "request": request,
            "hosts": hosts_with_updates,
            "username": username
        }
    )


@router.get("/host/{host_id}", response_class=HTMLResponse)
async def host_details(
    host_id: str,
    request: Request,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """
    Host details page showing available updates for a specific host.
    """
    # Get host
    host = db.query(Host).filter(Host.id == host_id).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    
    # Get latest update run
    latest_run = (
        db.query(UpdateRun)
        .filter(UpdateRun.host_id == host.id)
        .order_by(desc(UpdateRun.timestamp))
        .first()
    )
    
    if not latest_run:
        return templates.TemplateResponse(
            "dashboard/host_details.html",
            {
                "request": request,
                "host": host,
                "latest_run": None,
                "packages": [],
                "username": username
            }
        )
    
    # Get package updates for the latest run
    packages = (
        db.query(PackageUpdate)
        .filter(PackageUpdate.update_run_id == latest_run.id)
        .all()
    )
    
    return templates.TemplateResponse(
        "dashboard/host_details.html",
        {
            "request": request,
            "host": host,
            "latest_run": latest_run,
            "packages": packages,
            "username": username
        }
    )


@router.get("/hosts", response_class=HTMLResponse)
async def manage_hosts(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """
    Host management page.
    """
    hosts = db.query(Host).all()
    
    return templates.TemplateResponse(
        "dashboard/manage_hosts.html",
        {
            "request": request,
            "hosts": hosts,
            "username": username
        }
    )


@router.post("/hosts/add")
async def add_host(
    hostname: str = Form(...),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """
    Add a new host.
    """
    # Check if hostname already exists
    existing_host = db.query(Host).filter(Host.hostname == hostname).first()
    if existing_host:
        raise HTTPException(status_code=400, detail="Hostname already exists")
    
    # Create new host
    api_key = generate_api_key()
    host = Host(
        id=str(uuid.uuid4()),
        hostname=hostname,
        api_key=api_key
    )
    
    db.add(host)
    db.commit()
    
    return RedirectResponse(
        url="/dashboard/hosts",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/hosts/{host_id}/regenerate-key")
async def regenerate_api_key(
    host_id: str,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """
    Regenerate API key for a host.
    """
    # Get host
    host = db.query(Host).filter(Host.id == host_id).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    
    # Generate new API key
    host.api_key = generate_api_key()
    
    db.commit()
    
    return RedirectResponse(
        url="/dashboard/hosts",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/hosts/{host_id}/delete")
async def delete_host(
    host_id: str,
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user)
):
    """
    Delete a host.
    """
    # Get host
    host = db.query(Host).filter(Host.id == host_id).first()
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    
    # Delete host (cascade will delete related update runs and package updates)
    db.delete(host)
    db.commit()
    
    return RedirectResponse(
        url="/dashboard/hosts",
        status_code=status.HTTP_303_SEE_OTHER
    )