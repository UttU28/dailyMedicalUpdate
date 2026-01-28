#!/bin/bash

# Ubuntu/Linux shell script to setup and run the Medical Claim Processor

echo "========================================"
echo "Medical Claim Processor - Setup & Run"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.8+ using: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

echo "[INFO] Python found"
python3 --version
echo ""

# Check if virtual environment exists
if [ ! -d "env" ] || [ ! -f "env/bin/activate" ]; then
    echo "[INFO] Virtual environment not found. Creating one..."
    python3 -m venv env
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        exit 1
    fi
    echo "[INFO] Virtual environment created successfully"
else
    echo "[INFO] Virtual environment already exists"
fi

echo ""
echo "[INFO] Activating virtual environment..."
source env/bin/activate

echo ""
echo "[INFO] Upgrading pip..."
python -m pip install --upgrade pip

echo ""
echo "[INFO] Installing requirements..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install requirements"
    exit 1
fi

echo ""
echo "[INFO] All dependencies installed successfully"
echo ""
echo "========================================"
echo "Starting Medical Claim Processor..."
echo "========================================"
echo ""

# Run the application
python app.py

# Check exit status
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Application exited with an error"
    exit 1
fi
