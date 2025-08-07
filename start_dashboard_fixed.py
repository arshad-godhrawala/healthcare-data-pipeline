#!/usr/bin/env python3
"""
Fixed dashboard server for Healthcare Data Pipeline
"""
import os
import sys
import webbrowser
import threading
import time
import socket
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def find_free_port(start_port=3000):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def start_dashboard():
    """Start the dashboard server"""
    # Get the frontend directory
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        return False
    
    # Check if index.html exists
    index_file = frontend_dir / "index.html"
    if not index_file.exists():
        print(f"❌ index.html not found in {frontend_dir}")
        return False
    
    print(f"✅ Found frontend files in: {frontend_dir}")
    
    # Find a free port
    port = find_free_port(3000)
    if port is None:
        print("❌ No free ports found")
        return False
    
    print(f"🔍 Using port: {port}")
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    try:
        # Create server
        server = HTTPServer(("localhost", port), CORSRequestHandler)
        print(f"✅ Dashboard server started on http://localhost:{port}")
        print(f"📁 Serving files from: {frontend_dir}")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open(f'http://localhost:{port}')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Start serving
        print("🔄 Server is running... Press Ctrl+C to stop")
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard server stopped.")
    except Exception as e:
        print(f"❌ Error starting dashboard server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Healthcare Data Pipeline Dashboard...")
    start_dashboard() 