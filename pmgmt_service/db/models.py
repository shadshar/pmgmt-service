"""
Database models for the Patch Management Service.
"""

import datetime
import uuid
from typing import List

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, 
    ForeignKey, Text, JSON, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Host(Base):
    """
    Model representing a host system.
    """
    __tablename__ = "hosts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hostname = Column(String(255), nullable=False, unique=True)
    api_key = Column(String(64), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime, nullable=True)
    
    # Relationships
    updates = relationship("UpdateRun", back_populates="host", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Host(hostname='{self.hostname}')>"


class UpdateRun(Base):
    """
    Model representing a single run of the update check.
    """
    __tablename__ = "update_runs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    host_id = Column(String(36), ForeignKey("hosts.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    distribution_id = Column(String(255), nullable=False)
    distribution_version = Column(String(255), nullable=False)
    distribution_name = Column(String(255), nullable=False)
    package_manager = Column(String(255), nullable=False)
    total_updates = Column(Integer, default=0)
    security_updates = Column(Integer, default=0)
    
    # Relationships
    host = relationship("Host", back_populates="updates")
    packages = relationship("PackageUpdate", back_populates="update_run", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UpdateRun(host='{self.host.hostname}', timestamp='{self.timestamp}')>"


class PackageUpdate(Base):
    """
    Model representing a single package update.
    """
    __tablename__ = "package_updates"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    update_run_id = Column(String(36), ForeignKey("update_runs.id"), nullable=False)
    name = Column(String(255), nullable=False)
    version = Column(String(255), nullable=False)
    current_version = Column(String(255), nullable=True)
    architecture = Column(String(255), nullable=True)
    is_security_update = Column(Boolean, default=False)
    size = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    additional_info = Column(JSON, nullable=True)
    
    # Relationships
    update_run = relationship("UpdateRun", back_populates="packages")
    
    def __repr__(self):
        return f"<PackageUpdate(name='{self.name}', version='{self.version}')>"


def get_engine(db_path="pmgmt.db"):
    """
    Create a SQLAlchemy engine.
    
    Args:
        db_path (str): Path to the SQLite database file.
        
    Returns:
        Engine: SQLAlchemy engine.
    """
    return create_engine(f"sqlite:///{db_path}")


def get_session_factory(engine):
    """
    Create a SQLAlchemy session factory.
    
    Args:
        engine: SQLAlchemy engine.
        
    Returns:
        sessionmaker: SQLAlchemy session factory.
    """
    return sessionmaker(bind=engine)


def init_db(db_path="pmgmt.db"):
    """
    Initialize the database.
    
    Args:
        db_path (str): Path to the SQLite database file.
    """
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)
    return engine