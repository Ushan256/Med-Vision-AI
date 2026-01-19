@echo off
REM MED-VISION Quick Start Script for Windows
REM This script sets up and starts both backend and frontend servers

setlocal enabledelayedexpansion

echo.
echo ================================================
echo   MED-VISION 2.0 - Quick Start Setup (Windows)
echo ================================================
echo.

REM Check if running from correct directory
if not exist "backend" (
    echo Error: backend folder not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

if not exist "frontend" (
    echo Error: frontend folder not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo [Step 1] Setting up Backend
echo ================================
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
pip install -q -r requirements.txt

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    (
        echo SECRET_KEY=your-super-secret-key-change-this-in-production-12345
        echo DATABASE_URL=sqlite:///./medical_ai.db
    ) > .env
    echo WARNING: Remember to change SECRET_KEY in production!
)

echo [OK] Backend setup complete
echo.

REM Navigate back to root
cd ..

echo [Step 2] Setting up Frontend
echo ================================
cd frontend

REM Install Node dependencies
if not exist "node_modules" (
    echo Installing Node dependencies...
    call npm install -q
)

echo [OK] Frontend setup complete
echo.

REM Navigate back to root
cd ..

echo.
echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo Next Steps:
echo.
echo 1. Open TWO command prompts in the project root folder
echo.
echo Terminal 1 - Run Backend:
echo    cd backend
echo    venv\Scripts\activate.bat
echo    python -m uvicorn main:app --reload
echo.
echo Terminal 2 - Run Frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 3. Open your browser to: http://localhost:5173
echo.
echo Quick Troubleshooting:
echo - If ports are in use, modify the port numbers:
echo   Backend: python -m uvicorn main:app --reload --port 8001
echo   Frontend: npm run dev -- --port 5174
echo.
echo - Delete backend\medical_ai.db if you need to reset the database
echo.
pause
