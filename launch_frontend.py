#!/usr/bin/env python3
"""
Frontend Launcher for Multi-Market Correlation Engine
=====================================================

Convenient script to launch the TypeScript React frontend with proper checks.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_backend_api():
"""Check if the backend API is running."""
try:
response = requests.get("http://127.0.0.1:8000/health", timeout=5)
if response.status_code == 200:
print(" Backend API is running and healthy")
return True
else:
print(f" Backend API returned status code: {response.status_code}")
return False
except requests.exceptions.RequestException as e:
print(f" Backend API is not accessible: {e}")
return False

def install_dependencies():
"""Install frontend dependencies if needed."""
frontend_dir = Path("frontend")
node_modules = frontend_dir / "node_modules"

if not node_modules.exists():
print(" Installing frontend dependencies...")
try:
subprocess.run(
["npm", "install"],
cwd=frontend_dir,
check=True,
capture_output=True,
text=True
)
print(" Dependencies installed successfully")
return True
except subprocess.CalledProcessError as e:
print(f" Failed to install dependencies: {e}")
print(f"Error output: {e.stderr}")
return False
else:
print(" Dependencies already installed")
return True

def check_node_version():
"""Check if Node.js is installed and meets requirements."""
try:
result = subprocess.run(
["node", "--version"],
capture_output=True,
text=True,
check=True
)
version = result.stdout.strip()
print(f" Node.js version: {version}")

# Extract major version number
major_version = int(version.lstrip('v').split('.')[0])
if major_version >= 18:
return True
else:
print(f" Node.js version {version} is below recommended version 18+")
return False

except (subprocess.CalledProcessError, FileNotFoundError):
print(" Node.js not found. Please install Node.js 18+ from https://nodejs.org/")
return False

def start_frontend():
"""Start the frontend development server."""
frontend_dir = Path("frontend")

if not frontend_dir.exists():
print(" Frontend directory not found")
return False

print(" Starting frontend development server...")
print("📍 Frontend will be available at: http://localhost:3000")
print("🔗 API proxy configured for: http://127.0.0.1:8000")
print("\n" + "="*60)
print(" Multi-Market Correlation Engine - TypeScript Frontend")
print("="*60)

try:
# Start the development server
subprocess.run(
["npm", "run", "dev"],
cwd=frontend_dir,
check=True
)
except subprocess.CalledProcessError as e:
print(f" Failed to start frontend server: {e}")
return False
except KeyboardInterrupt:
print("\n🛑 Frontend server stopped by user")
return True

def main():
"""Main launcher function."""
print(" Multi-Market Correlation Engine - Frontend Launcher")
print("=" * 60)

# Check prerequisites
if not check_node_version():
sys.exit(1)

# Check if backend is running
backend_running = check_backend_api()
if not backend_running:
print("\n To start the backend API:")
print(" cd /Users/aditya/Desktop/multi_market_correlation_engine")
print(" source correlation_env/bin/activate")
print(" python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000")
print("\n Some features may not work without the backend API")

response = input("\nContinue anyway? (y/N): ").strip().lower()
if response != 'y':
print("Exiting...")
sys.exit(0)

# Install dependencies
if not install_dependencies():
sys.exit(1)

# Start frontend
print("\n Starting TypeScript React Frontend...")
start_frontend()

if __name__ == "__main__":
main()