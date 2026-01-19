#!/usr/bin/env python3
"""
Check if backend is running, if not, start it.
This script checks port 8000 and starts the backend server if needed.
"""

import subprocess
import socket
import sys
import time
import os

def is_port_open(host='localhost', port=8000):
    """Check if port 8000 is accessible"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    try:
        result = sock.connect_ex((host, port))
        return result == 0
    finally:
        sock.close()

def main():
    print("=" * 60)
    print("MED-VISION Backend Status Check")
    print("=" * 60)
    
    # Check if backend is already running
    if is_port_open():
        print("✅ Backend is RUNNING on http://localhost:8000")
        print("\nYou can now:")
        print("  1. Open http://localhost:5173 in your browser")
        print("  2. Try signing up again")
        return 0
    
    print("❌ Backend is NOT running on port 8000")
    print("\nAttempting to start backend...")
    
    # Get the backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    
    if not os.path.exists(backend_dir):
        print(f"❌ Error: backend directory not found at {backend_dir}")
        return 1
    
    os.chdir(backend_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found in backend folder")
        print("Please create backend/.env with SECRET_KEY and DATABASE_URL")
        return 1
    
    print("✅ .env file found")
    
    # Try to start the backend
    try:
        print("\n📡 Starting FastAPI server...")
        print("=" * 60)
        
        # Use python -m uvicorn to ensure it uses the right Python
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'main:app', 
            '--reload', 
            '--host', '127.0.0.1',
            '--port', '8000'
        ], check=False)
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
