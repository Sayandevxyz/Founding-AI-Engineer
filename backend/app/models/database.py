"""Database models and SQLite connection setup with SQLAlchemy."""
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Integer, Float, Text, Boolean, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()
DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./replicate_ai.db")

engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    original_url = Column(String(1024), nullable=False)
    status = Column(String(64), default="INITIALIZED")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    preview_port = Column(Integer, nullable=True)
    current_version = Column(Integer, default=1)
    
    generated_path = Column(String(512), nullable=True)
    website_spec_json = Column(Text, nullable=True)
    validation_result_json = Column(Text, nullable=True)
    stats_json = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    versions = relationship("ProjectVersionModel", back_populates="project", cascade="all, delete-orphan")


class ProjectVersionModel(Base):
    __tablename__ = "project_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String(64), ForeignKey("projects.id"), index=True)
    version = Column(Integer, nullable=False)
    prompt = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    changed_files_json = Column(Text, nullable=True)
    build_passed = Column(Boolean, default=True)
    snapshot_dir = Column(String(512), nullable=True)

    project = relationship("ProjectModel", back_populates="versions")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
