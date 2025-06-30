#!/usr/bin/env python3
"""
Phase 4 Launch Script
====================

Launch script to start both the Streamlit dashboard and FastAPI server
for the Multi-Market Correlation Engine Phase 4.

Author: Multi-Market Correlation Engine Team
Version: 4.0.0
"""

import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path

def start_api_server():
    """Start the FastAPI server."""
    print("🚀 Starting FastAPI server...")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Start FastAPI with uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "src.api.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
        "--log-level", "info"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("🛑 FastAPI server stopped")
    except Exception as e:
        print(f"❌ Error starting FastAPI server: {e}")

def start_dashboard():
    """Start the Streamlit dashboard."""
    print("🚀 Starting Streamlit dashboard...")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Start Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        "src/dashboard/main_dashboard.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("🛑 Streamlit dashboard stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit dashboard: {e}")

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "streamlit",
        "fastapi",
        "uvicorn",
        "plotly",
        "pandas",
        "numpy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("📦 Install missing packages with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def main():
    """Main launch function."""
    print("🚀 Multi-Market Correlation Engine - Phase 4 Launcher")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\n🎯 Starting Phase 4 services...")
    print("  - FastAPI server: http://localhost:8000")
    print("  - Streamlit dashboard: http://localhost:8501")
    print("  - API documentation: http://localhost:8000/docs")
    
    # Start services in separate threads
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
    
    try:
        # Start API server
        api_thread.start()
        print("⏳ Waiting for API server to start...")
        time.sleep(3)
        
        # Start dashboard
        dashboard_thread.start()
        print("⏳ Waiting for dashboard to start...")
        time.sleep(3)
        
        print("\n🎉 Phase 4 services are starting up!")
        print("\n📋 Available endpoints:")
        print("  🌐 Main Dashboard: http://localhost:8501")
        print("  🔌 API Server: http://localhost:8000")
        print("  📚 API Documentation: http://localhost:8000/docs")
        print("  🔍 API Health Check: http://localhost:8000/health")
        
        # Open browser to dashboard
        print("\n🌐 Opening dashboard in browser...")
        time.sleep(2)
        webbrowser.open("http://localhost:8501")
        
        print("\n✋ Press Ctrl+C to stop all services")
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Phase 4 services...")
            
    except Exception as e:
        print(f"❌ Error launching services: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 