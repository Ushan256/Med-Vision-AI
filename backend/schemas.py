"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
from datetime import datetime


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    user_type: str  # student, researcher, doctor, nurse, other


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response (without password)"""
    id: int
    email: str
    first_name: str
    last_name: str
    user_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class PredictionResponse(BaseModel):
    """Prediction response"""
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    heatmap: Optional[str] = None
    original_image: Optional[str] = None
    disclaimer: str


class ScanHistoryItem(BaseModel):
    """Scan history item response"""
    id: int
    prediction: str
    confidence: float
    normal_prob: float
    pneumonia_prob: float
    heatmap_base64: Optional[str] = None
    original_image_base64: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class ScanHistoryList(BaseModel):
    """List of scan history items"""
    items: list[ScanHistoryItem]
    total: int
