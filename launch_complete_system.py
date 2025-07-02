#!/usr/bin/env python3
"""
Complete System Launcher for Multi-Market Correlation Engine
===========================================================

Launches all system components in the proper sequence:
1. Enhanced API Server with Workflow Management
2. Frontend Development Server
3. System Health Monitoring

Author: Multi-Market Correlation Engine Team
Version: 1.0.0
"""

import os
import sys
import time
import subprocess
import signal
import threading
import requests
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemLauncher:
"""Complete system launcher with health monitoring."""

def __init__(self):
self.processes = {}
self.running = True

def start_api_server(self):
"""Start the enhanced API server."""
try:
logger.info(" Starting Enhanced API Server...")

# Activate virtual environment and start API
api_cmd = [
'python', '-m', 'uvicorn',
'src.api.main_enhanced:app',
'--host', '127.0.0.1',
'--port', '8000',
'--reload'
]

api_process = subprocess.Popen(
api_cmd,
stdout=subprocess.PIPE,
stderr=subprocess.PIPE,
text=True
)

self.processes['api'] = api_process
logger.info(" API Server started on http://localhost:8000")

# Wait for API to be ready
self.wait_for_api()

return api_process

except Exception as e:
logger.error(f" Failed to start API server: {e}")
return None

def start_frontend(self):
"""Start the frontend development server."""
try:
logger.info(" Starting Frontend Development Server...")

# Change to frontend directory and start dev server
frontend_cmd = ['npm', 'run', 'dev']

frontend_process = subprocess.Popen(
frontend_cmd,
cwd='frontend',
stdout=subprocess.PIPE,
stderr=subprocess.PIPE,
text=True
)

self.processes['frontend'] = frontend_process
logger.info(" Frontend Server starting on http://localhost:3001")

return frontend_process

except Exception as e:
logger.error(f" Failed to start frontend server: {e}")
return None

def wait_for_api(self, max_attempts=30):
"""Wait for API server to be ready."""
for attempt in range(max_attempts):
try:
response = requests.get('http://localhost:8000/health', timeout=5)
if response.status_code == 200:
logger.info(" API Server is ready!")
return True
except requests.exceptions.RequestException:
pass

logger.info(f"⏳ Waiting for API server... ({attempt + 1}/{max_attempts})")
time.sleep(2)

logger.error(" API server failed to start within timeout period")
return False

def check_system_health(self):
"""Check system health and display status."""
try:
# Check API health
api_response = requests.get('http://localhost:8000/health', timeout=5)
api_healthy = api_response.status_code == 200
api_data = api_response.json() if api_healthy else {}

# Check frontend (simple port check)
try:
frontend_response = requests.get('http://localhost:3001', timeout=5)
frontend_healthy = frontend_response.status_code == 200
except:
frontend_healthy = False

logger.info(f"🏥 System Health Check:")
logger.info(f" API Server: {' Healthy' if api_healthy else ' Unhealthy'}")
logger.info(f" Frontend: {' Healthy' if frontend_healthy else ' Unhealthy'}")

if api_healthy and 'components' in api_data:
components = api_data['components']
logger.info(f" Database: {'' if components.get('database') else ''}")
logger.info(f" ML Models: {'' if components.get('ml_predictor') else ''}")
logger.info(f" Agents: {'' if components.get('agent_coordinator') else ''}")
logger.info(f" Vector DB: {'' if components.get('vector_database') else ''}")

return api_healthy and frontend_healthy

except Exception as e:
logger.error(f" Health check failed: {e}")
return False

def run_demo_workflow(self):
"""Run a demo workflow to test the system."""
try:
logger.info(" Starting Demo Workflow...")

response = requests.post('http://localhost:8000/demo/full-workflow', timeout=10)

if response.status_code == 200:
data = response.json()
workflow_id = data['workflow_id']
logger.info(f" Demo workflow started: {workflow_id}")
logger.info(f" Features: {', '.join(data['features'])}")
logger.info(f" Estimated Duration: {data['estimated_duration']}")
logger.info(f" Status URL: http://localhost:8000{data['status_url']}")

return workflow_id
else:
logger.error(f" Failed to start demo workflow: {response.status_code}")
return None

except Exception as e:
logger.error(f" Demo workflow failed: {e}")
return None

def monitor_workflow(self, workflow_id):
"""Monitor workflow progress."""
try:
while self.running:
response = requests.get(f'http://localhost:8000/workflow/{workflow_id}/status', timeout=5)

if response.status_code == 200:
data = response.json()
status = data['status']
current_stage = data['current_stage']
completed_stages = len(data['stages_completed'])
total_stages = 12 # Total workflow stages

progress = (completed_stages / total_stages) * 100

logger.info(f" Workflow Progress: {progress:.1f}% ({completed_stages}/{total_stages})")
logger.info(f" Status: {status} | Current Stage: {current_stage}")

if status in ['completed', 'failed']:
logger.info(f"🏁 Workflow {status.upper()}!")
if data.get('duration'):
logger.info(f" Duration: {data['duration']:.2f}s")
if data.get('errors'):
logger.error(f" Errors: {data['errors']}")
break

time.sleep(5) # Check every 5 seconds

except Exception as e:
logger.error(f" Workflow monitoring failed: {e}")

def display_system_info(self):
"""Display comprehensive system information."""
logger.info("="*80)
logger.info(" MULTI-MARKET CORRELATION ENGINE - COMPLETE SYSTEM")
logger.info("="*80)
logger.info("")
logger.info(" SYSTEM COMPONENTS:")
logger.info(" • Enhanced API Server (FastAPI)")
logger.info(" • Workflow Orchestration Manager")
logger.info(" • ML/AI Analysis Engine")
logger.info(" • Vector Database (FAISS)")
logger.info(" • Agent-based Automation")
logger.info(" • React TypeScript Frontend")
logger.info("")
logger.info(" ACCESS POINTS:")
logger.info(" • Frontend UI: http://localhost:3001")
logger.info(" • API Server: http://localhost:8000")
logger.info(" • API Documentation: http://localhost:8000/docs")
logger.info(" • Workflow Dashboard: http://localhost:3001/workflow")
logger.info("")
logger.info(" CAPABILITIES:")
logger.info(" • Real-time Market Data Collection")
logger.info(" • Advanced Correlation Analysis")
logger.info(" • Machine Learning Predictions")
logger.info(" • LLM-powered Insights")
logger.info(" • Vector Pattern Matching")
logger.info(" • Automated Recommendations")
logger.info(" • Comprehensive Reporting")
logger.info("")
logger.info("="*80)

def setup_signal_handlers(self):
"""Setup signal handlers for graceful shutdown."""
def signal_handler(signum, frame):
logger.info("\n🛑 Shutdown signal received...")
self.shutdown()
sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def shutdown(self):
"""Graceful shutdown of all components."""
logger.info(" Shutting down system components...")
self.running = False

for name, process in self.processes.items():
if process and process.poll() is None:
logger.info(f" Stopping {name}...")
process.terminate()
try:
process.wait(timeout=5)
except subprocess.TimeoutExpired:
logger.warning(f" Force killing {name}...")
process.kill()

logger.info(" System shutdown complete")

def run(self):
"""Main execution loop."""
try:
self.setup_signal_handlers()
self.display_system_info()

# Start components
api_process = self.start_api_server()
if not api_process:
logger.error(" Failed to start API server. Exiting.")
return

frontend_process = self.start_frontend()
if not frontend_process:
logger.error(" Failed to start frontend. Continuing with API only.")

# Wait a bit for services to start
time.sleep(5)

# Health check
if self.check_system_health():
logger.info(" All systems operational!")

# Run demo workflow
workflow_id = self.run_demo_workflow()

if workflow_id:
# Monitor workflow in background
monitor_thread = threading.Thread(
target=self.monitor_workflow,
args=(workflow_id,)
)
monitor_thread.daemon = True
monitor_thread.start()

logger.info("")
logger.info(" SYSTEM READY FOR USE!")
logger.info(" Open http://localhost:3001 in your browser")
logger.info(" Navigate to the Workflow Dashboard to see the demo")
logger.info(" Press Ctrl+C to shutdown")
logger.info("")

# Keep running
try:
while self.running:
time.sleep(60) # Health check every minute
if not self.check_system_health():
logger.warning(" System health degraded")
except KeyboardInterrupt:
pass
else:
logger.error(" System health check failed")

except Exception as e:
logger.error(f" System launcher failed: {e}")
finally:
self.shutdown()

if __name__ == "__main__":
launcher = SystemLauncher()
launcher.run()
