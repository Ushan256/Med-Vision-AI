"""
FastAPI server for Medical AI model inference and Grad-CAM visualization.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status, Header
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import io
import numpy as np
from pathlib import Path
import tempfile
import os
import base64
from typing import Optional, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from gradcam import generate_gradcam, get_resnet18_target_layer
from database import get_db, User, ScanHistory, engine, Base
from auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from schemas import (
    UserRegister, UserLogin, UserResponse, TokenResponse, 
    RefreshTokenRequest, PredictionResponse, ScanHistoryList, ScanHistoryItem
)

# Create tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Provides better control and error handling than deprecated @app.on_event.
    """
    # Startup
    try:
        load_model()
        print("Application startup complete.")
    except Exception as e:
        print(f"Warning: Could not load model on startup: {e}")
        print("Model will be loaded on first prediction request.")
    
    yield
    
    # Shutdown (cleanup if needed)
    print("Application shutdown complete.")


app = FastAPI(
    title="Medical AI Imaging API",
    description="API for chest X-ray pneumonia classification with Explainable AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - explicitly allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"  # Fallback for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    """Dependency to get current authenticated user from JWT token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = verify_token(token)
    
    if token_data is None or token_data.email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Global variables
MODEL_PATH = Path(__file__).parent / "models" / "medical_model.pth"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = None
class_names = ["NORMAL", "PNEUMONIA"]
image_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def load_model():
    """Load the trained model."""
    global model
    
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. Please train the model first using train.py"
        )
    
    # Create model architecture
    model = models.resnet18(weights=None)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 2)
    
    # Load weights
    checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(DEVICE)
    model.eval()
    
    # Update class names if available in checkpoint
    if 'classes' in checkpoint:
        global class_names
        class_names = checkpoint['classes']
    
    print(f"Model loaded successfully from {MODEL_PATH}")
    print(f"Using device: {DEVICE}")


def preprocess_image(image_bytes: bytes) -> Tuple[torch.Tensor, np.ndarray]:
    """
    Preprocess image for model inference.
    
    Args:
        image_bytes: Image file bytes
        
    Returns:
        Tuple of (preprocessed image tensor, original image as numpy array)
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        # Save original image as numpy array for Grad-CAM overlay
        original_image = np.array(image)
        image_tensor = image_transform(image).unsqueeze(0)
        return image_tensor.to(DEVICE), original_image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")


def image_to_base64(image_array: np.ndarray) -> str:
    """
    Convert numpy image array to Base64 string.
    
    Args:
        image_array: Image as numpy array (H, W, 3) in range [0, 255]
        
    Returns:
        Base64 encoded string with data URI prefix
    """
    # Ensure image is uint8
    if image_array.dtype != np.uint8:
        image_array = np.clip(image_array, 0, 255).astype(np.uint8)
    
    # Convert to PIL Image and then to bytes
    pil_image = Image.fromarray(image_array)
    buffer = io.BytesIO()
    pil_image.save(buffer, format='PNG')
    image_bytes = buffer.getvalue()
    
    # Encode to Base64
    base64_string = base64.b64encode(image_bytes).decode('utf-8')
    
    # Return with data URI prefix for easy use in frontend
    return f"data:image/png;base64,{base64_string}"


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Medical AI Imaging API",
        "version": "1.0.0",
        "endpoints": {
            "/predict": "POST - Upload image for pneumonia classification",
            "/auth/register": "POST - Register new user",
            "/auth/login": "POST - Login user",
            "/auth/refresh": "POST - Refresh access token",
            "/auth/me": "GET - Get current user info",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    model_loaded = model is not None
    return {
        "status": "healthy" if model_loaded else "model_not_loaded",
        "device": str(DEVICE),
        "model_loaded": model_loaded
    }


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Token response with user info
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        user_type=user_data.user_type
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate tokens
    access_token = create_access_token(data={"sub": new_user.email})
    refresh_token = create_refresh_token(data={"sub": new_user.email})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=60 * 60 * 24,  # 24 hours in seconds
        user=UserResponse.from_orm(new_user)
    )


@app.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login a user and return access token.
    
    Args:
        credentials: Login credentials
        db: Database session
        
    Returns:
        Token response with user info
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate tokens
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=60 * 60 * 24,  # 24 hours in seconds
        user=UserResponse.from_orm(user)
    )


@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token request
        db: Database session
        
    Returns:
        New token response
    """
    token_data = verify_token(request.refresh_token)
    if token_data is None or token_data.email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user = db.query(User).filter(User.email == token_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Generate new access token
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=60 * 60 * 24,
        user=UserResponse.from_orm(user)
    )


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get information about the current authenticated user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse.from_orm(current_user)


@app.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout endpoint. Clears tokens client-side.
    Note: JWT tokens cannot be invalidated server-side without a token blacklist.
    Tokens are cleared from localStorage on the client side.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    # In a production environment, you might want to implement token blacklisting
    # For now, tokens are cleared on the client side via localStorage
    return {"message": "Logged out successfully", "detail": "Please clear tokens from client storage"}


# ==================== PREDICTION ENDPOINTS ====================


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Predict pneumonia from chest X-ray image with Grad-CAM heatmap.
    Requires authentication. Saves scan to user history.
    
    Args:
        file: Uploaded image file
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        JSON response with prediction results and Base64-encoded heatmap image
    """
    # Load model if not already loaded
    if model is None:
        try:
            load_model()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Model loading error: {str(e)}")
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read and preprocess image
    image_bytes = await file.read()
    image_tensor, original_image = preprocess_image(image_bytes)
    
    # Store original image as base64
    original_image_base64 = image_to_base64(original_image)
    
    # Make prediction
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
        predicted_class = outputs.argmax(dim=1).item()
        confidence = probabilities[predicted_class].item()
    
    # Generate Grad-CAM heatmap
    heatmap_base64 = None
    try:
        # Ensure input tensor has gradients enabled for Grad-CAM
        image_tensor_grad = image_tensor.clone().detach().requires_grad_(True)
        target_layer = get_resnet18_target_layer(model)
        heatmap_image = generate_gradcam(
            model=model,
            input_tensor=image_tensor_grad,
            target_layer=target_layer,
            class_idx=predicted_class,
            original_image=original_image
        )
        
        # Convert heatmap to Base64
        heatmap_base64 = image_to_base64(heatmap_image)
    except Exception as e:
        # If Grad-CAM fails, still return prediction but log the error
        print(f"Warning: Grad-CAM generation failed: {str(e)}")
    
    confidence_percentage = round(confidence * 100, 2)
    normal_prob = round(probabilities[0].item() * 100, 2)
    pneumonia_prob = round(probabilities[1].item() * 100, 2)
    
    # Save scan to history
    scan_history = ScanHistory(
        user_id=current_user.id,
        prediction=class_names[predicted_class],
        confidence=confidence_percentage,
        normal_prob=normal_prob,
        pneumonia_prob=pneumonia_prob,
        heatmap_base64=heatmap_base64,
        original_image_base64=original_image_base64,
        timestamp=datetime.now(timezone.utc)
    )
    db.add(scan_history)
    db.commit()
    db.refresh(scan_history)
    
    return JSONResponse({
        "scan_id": scan_history.id,
        "prediction": class_names[predicted_class],
        "confidence": confidence_percentage,
        "probabilities": {
            class_names[0]: normal_prob,
            class_names[1]: pneumonia_prob
        },
        "heatmap": heatmap_base64,
        "original_image": original_image_base64,
        "disclaimer": "This is an AI prototype for research purposes and should not be used for clinical diagnosis."
    })


@app.get("/history")
async def get_user_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get scan history for the current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of user's scans in reverse chronological order
    """
    scans = db.query(ScanHistory).filter(
        ScanHistory.user_id == current_user.id
    ).order_by(ScanHistory.timestamp.desc()).all()
    
    scan_items = [ScanHistoryItem.from_orm(scan) for scan in scans]
    return ScanHistoryList(items=scan_items, total=len(scan_items))


@app.get("/history/{scan_id}")
async def get_scan_detail(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific scan.
    
    Args:
        scan_id: ID of the scan
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Scan details
    """
    scan = db.query(ScanHistory).filter(
        ScanHistory.id == scan_id,
        ScanHistory.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    return ScanHistoryItem.from_orm(scan)


@app.post("/predict_with_gradcam")
async def predict_with_gradcam(file: UploadFile = File(...)):

    """
    Predict pneumonia with Grad-CAM heatmap visualization (legacy endpoint).
    This endpoint is kept for backward compatibility. Use /predict instead.
    
    Args:
        file: Uploaded image file
        
    Returns:
        JSON response with prediction and Base64-encoded heatmap
    """
    # Simply redirect to the main predict endpoint
    return await predict(file)


@app.get("/gradcam_image/{file_path:path}")
async def get_gradcam_image(file_path: str):
    """
    Retrieve Grad-CAM visualization image.
    
    Args:
        file_path: Path to the heatmap image
        
    Returns:
        Image file
    """
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Heatmap image not found")
    
    return FileResponse(file_path, media_type="image/png")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
