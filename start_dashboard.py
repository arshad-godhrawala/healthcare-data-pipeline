#!/usr/bin/env python3
"""
Simple dashboard server for Healthcare Data Pipeline
"""
import os
import sys
import webbrowser
import threading
import time
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

def start_dashboard():
    """Start the dashboard server"""
    # Get the frontend directory
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        return False
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Set up server
    PORT = 3000
    Handler = CORSRequestHandler
    
    try:
        # Create server
        with HTTPServer(("localhost", PORT), Handler) as httpd:
            print(f"✅ Dashboard server started on http://localhost:{PORT}")
            print(f"📁 Serving files from: {frontend_dir}")
            
            # Open browser after a short delay
            def open_browser():
                time.sleep(2)
                webbrowser.open(f'http://localhost:{PORT}')
            
            threading.Thread(target=open_browser, daemon=True).start()
            
            # Start serving
            print("🔄 Server is running... Press Ctrl+C to stop")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Dashboard server stopped.")
    except Exception as e:
        print(f"❌ Error starting dashboard server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Healthcare Data Pipeline Dashboard...")
    start_dashboard() 