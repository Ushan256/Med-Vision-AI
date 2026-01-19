"""
Database setup and models for user authentication and scan history.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from pathlib import Path

# Database setup
DATABASE_URL = "sqlite:///./medical_ai.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """User account model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    user_type = Column(String, nullable=False)  # student, researcher, doctor, nurse, other
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to scan history
    scans = relationship("ScanHistory", back_populates="user", cascade="all, delete-orphan")


class ScanHistory(Base):
    """Scan history model"""
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prediction = Column(String, nullable=False)  # NORMAL or PNEUMONIA
    confidence = Column(Float, nullable=False)  # 0-100
    normal_prob = Column(Float, nullable=False)
    pneumonia_prob = Column(Float, nullable=False)
    heatmap_base64 = Column(Text, nullable=True)  # Base64 encoded heatmap
    original_image_base64 = Column(Text, nullable=True)  # Base64 encoded original image
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship to user
    user = relationship("User", back_populates="scans")


# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
