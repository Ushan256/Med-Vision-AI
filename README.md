# MED-VISION: AI-Powered Medical Imaging Platform
**Live Demo:** https://med-vision-ai.vercel.app/

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-orange.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![React](https://img.shields.io/badge/React-18.2+-61dafb.svg)
![SQLite](https://img.shields.io/badge/SQLite-3.0+-yellow.svg)

**Professional AI-powered medical imaging solution for pneumonia detection with user authentication, scan history, and explainable AI**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Tech Stack](#tech-stack) • [Architecture](#architecture)

</div>

---

## Overview

**MED-VISION** is a comprehensive AI-powered medical imaging platform designed for chest X-ray pneumonia detection. Built for researchers, medical students, doctors, and healthcare professionals, the platform combines state-of-the-art deep learning with explainable AI (XAI) to provide accurate, transparent, and trusted medical image analysis.

### Key Highlights

- 🏥 **Professional Medical Imaging Platform** - Enterprise-grade system with user authentication and history management
- 🔐 **Secure User Management** - Role-based access (Students, Researchers, Doctors, Nurses, Others) with JWT token authentication
- 📊 **Personal Scan History** - Private, user-specific history with detailed analysis records
- 🔍 **Explainable AI** - Grad-CAM heatmaps visualize AI decision-making regions
- 🎨 **Modern Dark Mode UI** - High-contrast dark mode optimized for medical imaging
- ⚡ **RESTful API** - FastAPI backend with SQLite database for reliable data storage
- 📱 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile devices

---

## Features

### 🔐 User Authentication & Management

- **Secure Registration**: Email-based account creation with password hashing (bcrypt)
- **Role Selection**: Choose your role (Student, Researcher, Doctor, Nurse, Other) during signup
- **JWT Token Authentication**: Secure token-based authentication with automatic refresh
- **Token Expiration**: Tokens automatically expire on logout for enhanced security
- **Personal Profiles**: First name, last name, and role displayed in user profile

### 📸 Image Analysis

- **Drag & Drop Upload**: Intuitive file upload interface
- **Real-time Preview**: Preview images before analysis
- **Instant Analysis**: Fast inference (~100-200ms per image)
- **Confidence Metrics**: Detailed probability breakdowns for all classes
- **Grad-CAM Heatmaps**: Visual explanations showing AI focus regions

### 📊 Scan History Management

- **Personal History**: Each user has their own private scan history
- **Secure Isolation**: User data is completely isolated - no cross-user access
- **Detailed Records**: Every scan includes:
  - Prediction result (NORMAL/PNEUMONIA)
  - Confidence percentage
  - Class probabilities
  - Original image and heatmap
  - Timestamp
- **Quick Access**: Sidebar navigation for easy history browsing
- **Interactive Review**: Click any historical scan to view full details

### 🎨 User Interface

- **Side-by-Side Grid Layout**: Immediate comparison of image and results
- **High-Contrast Dark Mode**: Optimized for medical imaging workflows
- **Interactive Heatmap Toggle**: Show/hide overlay with adjustable opacity
- **Responsive Design**: Adapts to all screen sizes
- **Smooth Animations**: Professional transitions and loading states
- **Medical Disclaimer**: Prominent warnings about research-only usage

### 🧠 AI Capabilities

- **ResNet18 Architecture**: Pre-trained on ImageNet, fine-tuned for medical imaging
- **Transfer Learning**: Leverages learned features for better accuracy
- **Grad-CAM Visualization**: Explainable AI showing model attention
- **Confidence Scoring**: Detailed probability distributions
- **Fast Inference**: Optimized for real-time analysis

---

## Tech Stack

### Backend

- **Python 3.8+**: Core programming language
- **FastAPI**: Modern, fast web framework for building APIs
- **PyTorch 2.0+**: Deep learning framework for model inference
- **ResNet18**: Pre-trained CNN architecture for image classification
- **SQLAlchemy**: ORM for database management
- **SQLite**: Lightweight, file-based database (local storage)
- **Uvicorn**: ASGI server for running FastAPI
- **JWT**: JSON Web Tokens for authentication
- **bcrypt**: Password hashing for security

### Frontend

- **React 18.2+**: Modern UI library for building interactive interfaces
- **Vite**: Next-generation frontend build tool
- **Axios**: HTTP client for API communication
- **CSS3**: Custom styling with CSS variables and animations
- **Context API**: State management for authentication

### Database

- **SQLite**: Local file-based database (`medical_ai.db`)
- **Tables**:
  - `users`: User accounts with email, hashed passwords, names, roles
  - `scan_history`: Individual scan records linked to users

---

## Installation

### Prerequisites

- **Python 3.8+** (recommended: 3.9+)
- **Node.js 16+** and npm
- **CUDA-capable GPU** (optional, for faster training/inference)
- **Git** (for cloning the repository)

### Backend Setup

1. **Clone the repository**:
```bash
git clone https://github.com/Ushan256/Med-Vision-AI.git
cd "AI Medical Imaging Project"
```

2. **Navigate to backend directory**:
```bash
cd backend
```

3. **Create virtual environment**:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

5. **Initialize database** (automatically created on first run):
```bash
python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"
```

6. **Train model** (optional - if `models/medical_model.pth` doesn't exist):
```bash
# Download dataset first
python prepare_data.py

# Train the model
python train.py
```

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd ../frontend
```

2. **Install dependencies**:
```bash
npm install
```

---

## Usage

### Starting the Application

#### Start Backend Server

```bash
cd backend
python -m uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`
- API Documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative Docs (ReDoc): `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

#### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173` (Vite default port)

### Quick Start Guide

1. **Start the backend server** (see above)
2. **Start the frontend server** (see above)
3. **Open browser** to `http://localhost:5173`
4. **Create an account**:
   - Click "Sign Up" (top right if modal appears)
   - Enter first name, last name
   - Select your role (Student, Researcher, Doctor, Nurse, or Other)
   - Enter email and password (minimum 6 characters)
   - Click "Create Account"
5. **Upload an X-ray image**:
   - Click "Click to upload or drag and drop"
   - Select a chest X-ray image (JPG, PNG, etc.)
   - Click "🔍 Analyze Image"
6. **View results**:
   - See prediction, confidence, and probabilities
   - Toggle heatmap overlay on/off
   - Adjust heatmap opacity with slider
7. **Review history**:
   - Check left sidebar for all previous scans
   - Click any scan to view full details

---

## API Endpoints

### Authentication

#### `POST /auth/register`
Register a new user account.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "user_type": "doctor"
}
```

**Response**: TokenResponse with access_token, refresh_token, and user info

#### `POST /auth/login`
Login with email and password.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response**: TokenResponse with access_token, refresh_token, and user info

#### `POST /auth/logout`
Logout current user (clears tokens client-side).

**Headers**: `Authorization: Bearer <access_token>`

#### `POST /auth/refresh`
Refresh access token using refresh token.

#### `GET /auth/me`
Get current authenticated user information.

**Headers**: `Authorization: Bearer <access_token>`

### Prediction

#### `POST /predict`
Analyze a chest X-ray image for pneumonia detection.

**Headers**: `Authorization: Bearer <access_token>`

**Request**: `multipart/form-data` with image file

**Response**:
```json
{
  "scan_id": 123,
  "prediction": "PNEUMONIA",
  "confidence": 95.23,
  "probabilities": {
    "NORMAL": 4.77,
    "PNEUMONIA": 95.23
  },
  "heatmap": "data:image/png;base64,...",
  "original_image": "data:image/png;base64,...",
  "disclaimer": "This is an AI prototype for research purposes..."
}
```

### History

#### `GET /history`
Get all scan history for the authenticated user.

**Headers**: `Authorization: Bearer <access_token>`

**Response**:
```json
{
  "items": [
    {
      "id": 123,
      "prediction": "PNEUMONIA",
      "confidence": 95.23,
      "normal_prob": 4.77,
      "pneumonia_prob": 95.23,
      "heatmap_base64": "data:image/png;base64,...",
      "original_image_base64": "data:image/png;base64,...",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1
}
```

#### `GET /history/{scan_id}`
Get details of a specific scan.

**Headers**: `Authorization: Bearer <access_token>`

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend                           │
│  • AuthContext (JWT token management)                       │
│  • User Authentication (Login/Signup)                       │
│  • Image Upload & Preview                                   │
│  • Results Display (Grid Layout)                            │
│  • History Sidebar (User-specific)                          │
│  • Interactive Heatmap (Toggle & Opacity)                   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/HTTPS
                         │ (REST API)
┌────────────────────────▼────────────────────────────────────┐
│                  FastAPI Backend                            │
│  • Authentication Endpoints (/auth/*)                       │
│  • Prediction Endpoint (/predict)                           │
│  • History Endpoints (/history)                             │
│  • JWT Token Validation                                     │
│  • Model Inference (ResNet18)                               │
│  • Grad-CAM Generation                                      │
└────────────────────────┬────────────────────────────────────┘
                         │ SQLAlchemy ORM
┌────────────────────────▼────────────────────────────────────┐
│              SQLite Database (medical_ai.db)                │
│  • users table (email, password_hash, names, role)          │
│  • scan_history table (user_id, predictions, images)        │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

**Users Table**:
- `id` (Primary Key)
- `email` (Unique, Indexed)
- `hashed_password`
- `first_name`
- `last_name`
- `user_type` (student, researcher, doctor, nurse, other)
- `created_at`

**Scan History Table**:
- `id` (Primary Key)
- `user_id` (Foreign Key → users.id)
- `prediction` (NORMAL/PNEUMONIA)
- `confidence` (0-100)
- `normal_prob` (0-100)
- `pneumonia_prob` (0-100)
- `heatmap_base64` (Text, Base64 encoded)
- `original_image_base64` (Text, Base64 encoded)
- `timestamp` (Indexed)

### Security Features

- **Password Hashing**: bcrypt with salt for secure password storage
- **JWT Tokens**: Stateless authentication with expiration
- **Token Refresh**: Automatic token refresh mechanism
- **User Isolation**: Database queries filtered by user_id
- **CORS Protection**: Configurable CORS middleware
- **Input Validation**: Pydantic models for request validation

---

## Project Structure

```
AI Medical Imaging Project/
│
├── backend/
│   ├── models/
│   │   └── medical_model.pth          # Trained model weights
│   ├── utils/
│   │   ├── __init__.py
│   │   └── gradcam.py                 # Grad-CAM utilities
│   ├── auth.py                         # Authentication utilities (JWT, hashing)
│   ├── database.py                     # Database models and setup
│   ├── gradcam.py                      # Grad-CAM implementation
│   ├── main.py                         # FastAPI server & endpoints
│   ├── schemas.py                      # Pydantic models
│   ├── train.py                        # Model training script
│   ├── prepare_data.py                 # Dataset preparation
│   ├── requirements.txt                # Python dependencies
│   └── medical_ai.db                   # SQLite database (auto-generated)
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AuthModal.jsx          # Login/Signup modal
│   │   │   ├── AuthModal.css
│   │   │   ├── HistorySidebar.jsx     # Scan history sidebar
│   │   │   ├── HistorySidebar.css
│   │   │   ├── InteractiveHeatmap.jsx # Heatmap toggle component
│   │   │   ├── InteractiveHeatmap.css
│   │   │   ├── ConfidenceMeter.jsx    # Confidence display
│   │   │   ├── ConfidenceMeter.css
│   │   │   ├── MedicalDisclaimer.jsx  # Disclaimer footer
│   │   │   └── MedicalDisclaimer.css
│   │   ├── context/
│   │   │   └── AuthContext.jsx        # Authentication context
│   │   ├── App.jsx                     # Main application
│   │   ├── App.css                     # Main styles
│   │   ├── main.jsx                    # React entry point
│   │   └── index.css                   # Global styles
│   ├── index.html                      # HTML template
│   ├── package.json                    # Node.js dependencies
│   └── vite.config.js                  # Vite configuration
│
└── README.md                           # This file
```

---

## Development

### Training a New Model

1. **Prepare the dataset**:
```bash
cd backend
python prepare_data.py
```

2. **Train the model**:
```bash
python train.py
```

3. **Model will be saved to**: `backend/models/medical_model.pth`

### Customizing the Application

#### Backend Customization

- **Modify endpoints**: Edit `backend/main.py`
- **Add database models**: Edit `backend/database.py`
- **Change authentication**: Edit `backend/auth.py`
- **Update schemas**: Edit `backend/schemas.py`

#### Frontend Customization

- **Modify components**: Edit files in `frontend/src/components/`
- **Update styles**: Edit CSS files or `frontend/src/App.css`
- **Change authentication flow**: Edit `frontend/src/context/AuthContext.jsx`

### Troubleshooting

#### "Failed to fetch" Error

This error typically means the backend server is not running:

1. **Check backend status**: Ensure `uvicorn main:app --reload` is running
2. **Verify port**: Backend should be on `http://localhost:8000`
3. **Check CORS**: Ensure CORS is enabled in `backend/main.py`
4. **Network issues**: Check firewall settings

#### Database Issues

- **Database locked**: Close any other processes using `medical_ai.db`
- **Migration needed**: Delete `medical_ai.db` and restart (tables auto-create)
- **Permission errors**: Ensure write permissions in `backend/` directory

#### Model Loading Issues

- **Model not found**: Train the model first (see Training section)
- **CUDA errors**: Ensure PyTorch is installed with correct CUDA version
- **Memory errors**: Use CPU mode or reduce batch size

---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit your changes**: `git commit -m 'Add some AmazingFeature'`
4. **Push to the branch**: `git push origin feature/AmazingFeature`
5. **Open a Pull Request**

### Guidelines

- Follow **PEP 8** for Python code
- Use **ESLint/Prettier** for JavaScript/React code
- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Ensure backward compatibility

---

## Limitations & Future Work

### Current Limitations

- **Research Prototype**: Not validated for clinical use
- **Binary Classification**: Only distinguishes Normal vs. Pneumonia
- **Single Dataset**: Trained on specific dataset, may not generalize
- **No Patient Data**: Does not consider patient history or symptoms
- **Local Database**: SQLite suitable for development, not production scale

### Future Enhancements

- [ ] Multi-class classification (various pneumonia types)
- [ ] Integration with DICOM format
- [ ] Patient history integration
- [ ] Model ensemble for improved accuracy
- [ ] PostgreSQL/MongoDB for production database
- [ ] Real-time video analysis
- [ ] Mobile app development (React Native)
- [ ] Cloud deployment (Docker, AWS, Azure)
- [ ] Advanced analytics and reporting
- [ ] Multi-language support
- [ ] Admin dashboard for user management

---

## Medical Disclaimer

⚠️ **IMPORTANT: This is a research prototype and should NOT be used for clinical diagnosis without proper validation and regulatory approval.**

The system is designed to:
- Assist, not replace, medical professionals
- Provide second opinions, not primary diagnoses
- Support decision-making, not make autonomous decisions
- Be used in conjunction with clinical expertise

Always consult qualified healthcare professionals for medical diagnoses.

---

## Acknowledgments

- **Dataset**: [Chest X-Ray Pneumonia Dataset](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia) by Paul Mooney
- **PyTorch Team**: For the excellent deep learning framework
- **FastAPI**: For the modern Python web framework
- **React Team**: For the powerful UI library

---

## Contact & Support

For questions, issues, or contributions:

- **Issues**: Open an issue on GitHub
- **Documentation**: Check this README for detailed information
- **API Docs**: Visit `http://localhost:8000/docs` when backend is running

---

<div align="center">

**⚠️ Medical Disclaimer**: This is an AI prototype for research purposes and should not be used for clinical diagnosis.

Made with ❤️ for advancing medical AI research

</div>
