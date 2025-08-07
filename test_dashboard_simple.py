#!/usr/bin/env python3
"""
Simple dashboard test script
"""
import requests
import time
import subprocess
import sys
import threading
from pathlib import Path

def test_dashboard():
    """Test if dashboard is working"""
    print("🔍 Testing Dashboard...")
    
    # Check if frontend files exist
    frontend_dir = Path(__file__).parent / "frontend"
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    index_file = frontend_dir / "index.html"
    if not index_file.exists():
        print("❌ index.html not found")
        return False
    
    print("✅ Frontend files found")
    
    # Start dashboard server in background
    def start_server():
        subprocess.run([sys.executable, "start_dashboard.py"], 
                      capture_output=True, timeout=10)
    
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    print("⏳ Starting dashboard server...")
    time.sleep(5)  # Wait for server to start
    
    try:
        # Test dashboard endpoint
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard server working")
            return True
        else:
            print(f"❌ Dashboard server returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Dashboard test failed: {e}")
        return False

if __name__ == "__main__":
    test_dashboard() 