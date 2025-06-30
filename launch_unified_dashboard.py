#!/usr/bin/env python3
"""
Launch script for the Unified Multi-Market Correlation Engine Dashboard
Starts both API server and dashboard in one command
"""

import subprocess
import time
import sys
import os
import signal
import requests
from threading import Thread

def check_port(port):
    """Check if a port is already in use"""
    try:
        response = requests.get(f"http://127.0.0.1:{port}", timeout=2)
        return True
    except:
        return False

def wait_for_service(port, service_name, max_wait=30):
    """Wait for a service to become available"""
    print(f"⏳ Waiting for {service_name} on port {port}...")
    for i in range(max_wait):
        if check_port(port):
            print(f"✅ {service_name} is ready!")
            return True
        time.sleep(1)
        if i % 5 == 0:
            print(f"   Still waiting... ({i}/{max_wait}s)")
    return False

def cleanup_processes():
    """Clean up any existing processes"""
    print("🧹 Cleaning up existing processes...")
    try:
        # Kill existing streamlit and uvicorn processes
        subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
        subprocess.run(["pkill", "-f", "uvicorn"], capture_output=True)
        time.sleep(2)
    except:
        pass

def start_api_server():
    """Start the API server"""
    print("🚀 Starting API server...")
    api_cmd = [
        sys.executable, "-m", "uvicorn", 
        "src.api.main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--log-level", "info",
        "--timeout-keep-alive", "5"
    ]
    
    return subprocess.Popen(
        api_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid if hasattr(os, 'setsid') else None
    )

def start_dashboard():
    """Start the unified dashboard"""
    print("📊 Starting unified dashboard...")
    dashboard_cmd = [
        sys.executable, "-m", "streamlit", "run",
        "src/dashboard/unified_dashboard.py",
        "--server.port", "8500",
        "--server.address", "127.0.0.1",
        "--browser.gatherUsageStats", "false",
        "--server.headless", "true"
    ]
    
    return subprocess.Popen(
        dashboard_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid if hasattr(os, 'setsid') else None
    )

def main():
    print("🚀 Multi-Market Correlation Engine - Unified Dashboard Launcher")
    print("=" * 60)
    
    # Store process references
    processes = []
    
    def signal_handler(signum, frame):
        print("\n\n🛑 Shutting down services...")
        for proc in processes:
            try:
                if hasattr(os, 'killpg'):
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                else:
                    proc.terminate()
            except:
                pass
        cleanup_processes()
        print("✅ Shutdown complete!")
        sys.exit(0)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Clean up any existing processes
        cleanup_processes()
        
        # Start API server
        api_process = start_api_server()
        processes.append(api_process)
        
        # Wait for API to be ready
        if not wait_for_service(8000, "API Server"):
            print("❌ API Server failed to start!")
            return 1
        
        # Start dashboard
        dashboard_process = start_dashboard()
        processes.append(dashboard_process)
        
        # Wait for dashboard to be ready
        if not wait_for_service(8500, "Unified Dashboard"):
            print("❌ Dashboard failed to start!")
            return 1
        
        print("\n" + "=" * 60)
        print("🎉 UNIFIED DASHBOARD IS READY!")
        print("=" * 60)
        print(f"🌐 Dashboard URL: http://127.0.0.1:8500")
        print(f"🔧 API Server:    http://127.0.0.1:8000")
        print(f"📚 API Docs:      http://127.0.0.1:8000/docs")
        print("=" * 60)
        print("\n✨ Features Available:")
        print("   📈 Market Overview - Real-time price charts & data")
        print("   🔗 Correlations - Interactive correlation analysis")
        print("   🤖 AI Insights - GARCH, VAR, ML predictions")
        print("   🌐 Network Analysis - Correlation networks")
        print("   ⚙️ System Monitor - Real-time system status")
        print("\n💡 Press Ctrl+C to stop all services")
        print("=" * 60)
        
        # Keep the launcher running
        try:
            while True:
                # Check if processes are still running
                for proc in processes[:]:  # Copy list to avoid modification during iteration
                    if proc.poll() is not None:
                        print(f"⚠️ Process {proc.pid} has stopped")
                        processes.remove(proc)
                
                if not processes:
                    print("❌ All processes have stopped")
                    break
                    
                time.sleep(5)
        except KeyboardInterrupt:
            pass
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        signal_handler(None, None)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 