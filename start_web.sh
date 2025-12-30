#!/bin/bash

echo "========================================"
echo "  RPA Bot - Web Interface Launcher"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

echo "[1/3] Checking Python installation..."
python3 --version

echo ""
echo "[2/3] Installing/Updating dependencies..."
pip3 install -r requirements_web.txt

echo ""
echo "[3/3] Starting Flask server..."
echo ""
echo "========================================"
echo "  Web interface will open at:"
echo "  http://localhost:5000"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Flask app
python3 app.py

