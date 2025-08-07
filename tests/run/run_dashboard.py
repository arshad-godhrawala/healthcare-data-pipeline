"""
Simple HTTP server to serve the Healthcare Dashboard.
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Configuration
PORT = 3000  # Changed from 8080 to 3000
DIRECTORY = "frontend"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Get the absolute path to the frontend directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up two levels to get to project root, then to frontend
        project_root = os.path.dirname(os.path.dirname(current_dir))
        frontend_dir = os.path.join(project_root, DIRECTORY)
        super().__init__(*args, directory=frontend_dir, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for API access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def run_dashboard():
    """Run the dashboard server."""
    # Check if frontend directory exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up two levels to get to project root, then to frontend
    project_root = os.path.dirname(os.path.dirname(current_dir))
    frontend_dir = os.path.join(project_root, DIRECTORY)
    
    if not os.path.exists(frontend_dir):
        print(f"❌ Frontend directory not found: {frontend_dir}")
        return
    
    print(f"📁 Serving from: {frontend_dir}")
    
    # Create server
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"🚀 Healthcare Dashboard Server Starting...")
        print(f"📊 Dashboard URL: http://localhost:{PORT}")
        print(f"🔗 API URL: http://localhost:8002")
        print(f"📖 API Docs: http://localhost:8002/docs")
        print("=" * 60)
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Open dashboard in browser
        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except:
            print(f"Please open your browser and go to: http://localhost:{PORT}")
        
        # Start server
        httpd.serve_forever()

if __name__ == "__main__":
    try:
        run_dashboard()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard server stopped.")
    except Exception as e:
        print(f"❌ Error starting dashboard server: {e}") 