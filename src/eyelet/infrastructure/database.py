"""Database configuration and models"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from eyelet.utils.paths import get_eyelet_db_path, ensure_directory_exists, migrate_legacy_data

Base = declarative_base()


def get_db_path(custom_location: Optional[Path] = None) -> Path:
    """Get the database path using XDG-compliant central location.
    
    Args:
        custom_location: Optional custom database location
        
    Returns:
        Path to eyelet database file
    """
    # Get the new central database path
    db_path = get_eyelet_db_path(custom_location)
    
    # Ensure directory exists
    ensure_directory_exists(db_path.parent)
    
    # Check for legacy migration if no custom location specified
    if custom_location is None:
        legacy_path = Path.home() / ".eyelet" / "eyelet.db"
        if migrate_legacy_data(legacy_path, db_path):
            print(f"Migrated eyelet database from {legacy_path} to {db_path}")
    
    return db_path


class HookExecutionModel(Base):
    """SQLAlchemy model for hook executions"""

    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hook_id = Column(String, nullable=False)
    hook_type = Column(String, nullable=False)
    tool_name = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    input_data = Column(JSON)
    output_data = Column(JSON)
    duration_ms = Column(Integer)
    status = Column(String, default="pending")
    error_message = Column(String)


class WorkflowResultModel(Base):
    """SQLAlchemy model for workflow results"""

    __tablename__ = "workflow_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(Integer, nullable=False)
    step_name = Column(String, nullable=False)
    result = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)


class TemplateModel(Base):
    """SQLAlchemy model for templates"""

    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    template_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    content = Column(JSON, nullable=False)
    version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    installed = Column(Boolean, default=False)
    installed_at = Column(DateTime)


def init_db(engine=None, custom_db_path: Optional[Path] = None):
    """Initialize the database.
    
    Args:
        engine: Optional SQLAlchemy engine instance
        custom_db_path: Optional custom database path
        
    Returns:
        SQLAlchemy engine instance
    """
    if engine is None:
        db_path = get_db_path(custom_db_path)
        engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    return engine


def get_session(custom_db_path: Optional[Path] = None):
    """Get a database session.
    
    Args:
        custom_db_path: Optional custom database path
        
    Returns:
        SQLAlchemy session instance
    """
    engine = init_db(custom_db_path=custom_db_path)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
