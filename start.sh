#!/bin/bash
# MED-VISION Quick Start Script for macOS/Linux
# This script sets up and starts both backend and frontend servers

set -e

echo "================================================"
echo "  MED-VISION 2.0 - Quick Start Setup"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${YELLOW}⚠️  Please run this script from the project root directory${NC}"
    echo "Usage: bash start.sh"
    exit 1
fi

echo -e "${BLUE}Step 1: Setting up Backend${NC}"
echo "================================"

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
SECRET_KEY=your-super-secret-key-change-this-in-production-12345
DATABASE_URL=sqlite:///./medical_ai.db
EOF
    echo -e "${YELLOW}⚠️  Remember to change SECRET_KEY in production!${NC}"
fi

echo -e "${GREEN}✓ Backend setup complete${NC}"
echo ""

# Navigate back to root
cd ..

echo -e "${BLUE}Step 2: Setting up Frontend${NC}"
echo "================================"

cd frontend

# Install Node dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install -q
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"
echo ""

# Navigate back to root
cd ..

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}Setup Complete! ✓${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "🚀 Starting servers..."
echo ""
echo -e "${YELLOW}You have two options:${NC}"
echo ""
echo -e "${BLUE}Option 1: Run both servers in the background (Recommended)${NC}"
echo "============================================================"
echo "1. In a new terminal, run:"
echo "   cd backend && source venv/bin/activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. In another new terminal, run:"
echo "   cd frontend && npm run dev"
echo ""
echo "3. Open browser to: http://localhost:5173"
echo ""
echo -e "${BLUE}Option 2: Use the automatic launcher (requires 'tmux')${NC}"
echo "=========================================================="
echo "Run: bash start_servers.sh"
echo ""
echo -e "${YELLOW}Quick Troubleshooting:${NC}"
echo "- Port 8000 in use? Kill it with: lsof -i :8000 | grep LISTEN | awk '{print \$2}' | xargs kill -9"
echo "- Port 5173 in use? Kill it with: lsof -i :5173 | grep LISTEN | awk '{print \$2}' | xargs kill -9"
echo "- Database locked? Delete backend/medical_ai.db and restart"
echo ""
echo -e "${GREEN}Happy diagnosing! 🩺${NC}"
