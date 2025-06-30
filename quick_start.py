#!/usr/bin/env python3
"""
Quick Start Script for Multi-Market Correlation Engine
======================================================

This script helps you set up and verify your development environment
for the Multi-Market Correlation Engine project.

Usage:
    python quick_start.py
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Print welcome header."""
    print("=" * 60)
    print("🚀 Multi-Market Correlation Engine - Quick Start")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is 3.9+."""
    print("📍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need Python 3.9+")
        return False

def check_pip():
    """Check if pip is available."""
    print("\n📍 Checking pip installation...")
    try:
        import pip
        print("✅ pip is available")
        return True
    except ImportError:
        print("❌ pip not found")
        return False

def create_virtual_environment():
    """Create virtual environment."""
    print("\n📍 Creating virtual environment...")
    
    venv_path = Path("correlation_env")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "correlation_env"], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("\n📍 Installing dependencies...")
    
    # Determine the activation script path
    system = platform.system()
    if system == "Windows":
        pip_path = Path("correlation_env/Scripts/pip")
    else:
        pip_path = Path("correlation_env/bin/pip")
    
    if not pip_path.exists():
        print("❌ Virtual environment pip not found")
        return False
    
    try:
        subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_directories():
    """Create necessary directories."""
    print("\n📍 Creating project directories...")
    
    directories = [
        "data/raw",
        "data/processed", 
        "data/models",
        "logs",
        "tests",
        "notebooks"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Project directories created")
    return True

def create_env_file():
    """Create .env file from template."""
    print("\n📍 Setting up environment file...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example.exists():
        # Create a basic .env.example
        env_content = """# Environment Variables for Multi-Market Correlation Engine
# Get your free API keys:

# FRED API (Federal Reserve Economic Data) - FREE
# Get at: https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY=your_fred_api_key_here

# Alpha Vantage API (Backup data source) - FREE
# Get at: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here

# Database Configuration
DATABASE_URL=sqlite:///data/market_data.db

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/correlation_engine.log
"""
        with open(".env.example", "w") as f:
            f.write(env_content)
    
    # Copy to .env
    with open(".env.example", "r") as f:
        content = f.read()
    
    with open(".env", "w") as f:
        f.write(content)
    
    print("✅ .env file created from template")
    print("⚠️  Remember to add your actual API keys to the .env file")
    return True

def test_imports():
    """Test basic imports."""
    print("\n📍 Testing core imports...")
    
    # Determine python path in virtual environment
    system = platform.system()
    if system == "Windows":
        python_path = Path("correlation_env/Scripts/python")
    else:
        python_path = Path("correlation_env/bin/python")
    
    test_script = """
import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
print("✅ All core packages imported successfully!")
"""
    
    try:
        result = subprocess.run(
            [str(python_path), "-c", test_script], 
            capture_output=True, 
            text=True, 
            check=True
        )
        print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Import test failed: {e.stderr}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 Quick Start Complete!")
    print("=" * 60)
    
    system = platform.system()
    if system == "Windows":
        activate_cmd = "correlation_env\\Scripts\\activate"
    else:
        activate_cmd = "source correlation_env/bin/activate"
    
    print(f"""
📋 Next Steps:

1. Activate your virtual environment:
   {activate_cmd}

2. Get your free API keys:
   - FRED API: https://fred.stlouisfed.org/docs/api/api_key.html
   - Alpha Vantage: https://www.alphavantage.co/support/#api-key

3. Add your API keys to the .env file

4. Start building! Follow the BUILD_GUIDE.md for detailed steps

5. Test the basic setup:
   python -c "from src.collectors.market_data_collector import MarketDataCollector; print('Ready to build!')"

🚀 You're ready to start building the Multi-Market Correlation Engine!
""")

def main():
    """Main setup function."""
    print_header()
    
    # Run all setup steps
    steps = [
        ("Python Version", check_python_version),
        ("Pip Installation", check_pip),
        ("Virtual Environment", create_virtual_environment),
        ("Dependencies", install_dependencies),
        ("Project Directories", create_directories),
        ("Environment File", create_env_file),
        ("Import Test", test_imports),
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        try:
            if not step_function():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} failed with error: {e}")
            failed_steps.append(step_name)
    
    if failed_steps:
        print(f"\n⚠️  Some steps failed: {', '.join(failed_steps)}")
        print("Please check the errors above and try again.")
        return False
    
    print_next_steps()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 