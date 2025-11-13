#!/bin/bash

# Asset Sentinel - Startup Script
# This script starts both the backend API and serves the frontend

echo "========================================="
echo "   Asset Sentinel - Starting Application"
echo "========================================="
echo ""

# Check if Python dependencies are installed
echo "[1/3] Checking dependencies..."
cd backend

if ! python3 -c "import flask" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip3 install -q -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install Python dependencies"
        exit 1
    fi
fi

echo "✓ Dependencies installed"
echo ""

# Start the Flask backend which also serves the frontend
echo "[2/3] Starting Asset Sentinel server..."
echo ""
echo "Backend API: http://localhost:5000/api"
echo "Frontend UI: http://localhost:5000"
echo ""
echo "Default login credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "[3/3] Server starting..."
echo "========================================="
echo ""

# Run the Flask app
python3 app_integrated.py
