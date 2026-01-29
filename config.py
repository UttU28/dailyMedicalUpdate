"""
Configuration utility for loading environment variables.
Handles both regular script execution and PyInstaller bundled executables.
"""
import os
import sys
from dotenv import load_dotenv

def load_env_file():
    """Load .env file from current directory or bundled location (PyInstaller)"""
    # Check if running from PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running from PyInstaller bundle
        base_path = sys._MEIPASS
        env_path = os.path.join(base_path, '.env')
    else:
        # Running as script
        env_path = '.env'
    
    # Load .env file if it exists
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        # Fallback to default load_dotenv behavior
        load_dotenv()
