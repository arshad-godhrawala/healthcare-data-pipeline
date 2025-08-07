#!/usr/bin/env python3
"""
Script to run the dashboard server for the Healthcare Data Pipeline
"""
import http.server
import socketserver
import webbrowser
import threading
import time
import os
from pathlib import Path

# Set up the server
PORT = 3000
DIRECTORY = Path(__file__).parent / "frontend"

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    # Change to the frontend directory
    os.chdir(DIRECTORY)
    
    print(f"Starting Dashboard Server...")
    print(f"Serving files from: {DIRECTORY}")
    print(f"Dashboard will be available at: http://localhost:{PORT}")
    
    # Create the server
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"Dashboard server started on port {PORT}")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open(f'http://localhost:{PORT}')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDashboard server stopped.") 