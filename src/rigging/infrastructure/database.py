"""Database configuration and models"""

from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


def get_db_path() -> Path:
    """Get the database path"""
    db_dir = Path.home() / ".rigging"
    db_dir.mkdir(exist_ok=True)
    return db_dir / "rigging.db"


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


def init_db(engine=None):
    """Initialize the database"""
    if engine is None:
        engine = create_engine(f"sqlite:///{get_db_path()}")
    Base.metadata.create_all(bind=engine)
    return engine


def get_session():
    """Get a database session"""
    engine = init_db()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()