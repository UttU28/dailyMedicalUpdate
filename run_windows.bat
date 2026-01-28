@echo off
REM Windows batch script to setup and run the Medical Claim Processor
echo ========================================
echo Medical Claim Processor - Setup & Run
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [INFO] Python found
python --version
echo.

REM Check if virtual environment exists
if not exist "env\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found. Creating one...
    python -m venv env
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [INFO] Virtual environment created successfully
) else (
    echo [INFO] Virtual environment already exists
)

echo.
echo [INFO] Activating virtual environment...
call env\Scripts\activate.bat

echo.
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [INFO] Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install requirements
    pause
    exit /b 1
)

echo.
echo [INFO] All dependencies installed successfully
echo.
echo ========================================
echo Starting Medical Claim Processor...
echo ========================================
echo.

REM Run the application
python app.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo [ERROR] Application exited with an error
    pause
)
