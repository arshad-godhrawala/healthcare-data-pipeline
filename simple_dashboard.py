#!/usr/bin/env python3
"""
Simple dashboard for Healthcare Data Pipeline
"""
import os
import sys
import webbrowser
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

def main():
    """Start the dashboard server"""
    print("🚀 Starting Healthcare Data Pipeline Dashboard...")
    
    # Get the frontend directory
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        return
    
    # Check if index.html exists
    index_file = frontend_dir / "index.html"
    if not index_file.exists():
        print(f"❌ index.html not found in {frontend_dir}")
        return
    
    print(f"✅ Found frontend files in: {frontend_dir}")
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    # Try different ports
    ports = [3000, 3001, 3002, 8080, 8001]
    
    for port in ports:
        try:
            # Create server
            server = HTTPServer(("localhost", port), CORSRequestHandler)
            print(f"✅ Dashboard server started on http://localhost:{port}")
            print(f"📁 Serving files from: {frontend_dir}")
            
            # Open browser after a short delay
            def open_browser():
                time.sleep(2)
                webbrowser.open(f'http://localhost:{port}')
            
            import threading
            threading.Thread(target=open_browser, daemon=True).start()
            
            # Start serving
            print("🔄 Server is running... Press Ctrl+C to stop")
            server.serve_forever()
            break
            
        except OSError as e:
            print(f"⚠️  Port {port} is busy, trying next port...")
            continue
        except KeyboardInterrupt:
            print("\n🛑 Dashboard server stopped.")
            break
        except Exception as e:
            print(f"❌ Error starting dashboard server: {e}")
            continue

if __name__ == "__main__":
    main() 