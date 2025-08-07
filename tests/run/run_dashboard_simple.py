"""
Simple and fast HTTP server for the Healthcare Dashboard.
"""

import http.server
import socketserver
import os
import webbrowser
import threading
import time

# Configuration
PORT = 3000
DIRECTORY = "frontend"

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Get the absolute path to the frontend directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        frontend_dir = os.path.join(current_dir, DIRECTORY)
        super().__init__(*args, directory=frontend_dir, **kwargs)
    
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def start_server():
    """Start the dashboard server."""
    try:
        # Check if frontend directory exists
        current_dir = os.path.dirname(os.path.abspath(__file__))
        frontend_dir = os.path.join(current_dir, DIRECTORY)
        
        if not os.path.exists(frontend_dir):
            print(f"❌ Frontend directory not found: {frontend_dir}")
            return False
        
        print(f"📁 Serving from: {frontend_dir}")
        
        # Create server with shorter timeout
        with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
            httpd.timeout = 1  # Short timeout
            print(f"🚀 Healthcare Dashboard Server Starting...")
            print(f"📊 Dashboard URL: http://localhost:{PORT}")
            print(f"🔗 API URL: http://localhost:8002")
            print("=" * 50)
            
            # Start server
            httpd.serve_forever()
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def open_browser():
    """Open browser after a short delay."""
    time.sleep(2)  # Wait for server to start
    try:
        webbrowser.open(f'http://localhost:{PORT}')
        print(f"🌐 Browser opened: http://localhost:{PORT}")
    except:
        print(f"📋 Please open your browser and go to: http://localhost:{PORT}")

if __name__ == "__main__":
    print("🚀 Starting Healthcare Dashboard...")
    
    # Start browser in separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start server
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard server stopped.")
    except Exception as e:
        print(f"❌ Error: {e}") 