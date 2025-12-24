#!/usr/bin/env python3
"""
Simple HTTP Server for Healthcare-AI-Quantum-System Landing Page
No dependencies required - uses only Python standard library
"""

import http.server
import socketserver
from pathlib import Path
import json

PORT = 3000
frontend_dir = Path(__file__).parent / "frontend"

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(frontend_dir), **kwargs)

    def end_headers(self):
        # CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def translate_path(self, path):
        """Translate URL path to file system path"""
        # Health check endpoint
        if path == '/health':
            return None  # Will be handled in do_GET

        # Root or index.html -> templates/index.html
        if path == '/' or path == '/index.html':
            path = '/templates/index.html'
        # All .html files -> templates/{file}.html
        elif path.endswith('.html') and not path.startswith('/templates/'):
            path = '/templates' + path
        # Static files (css, js, images)
        elif not path.startswith('/templates/') and not path.startswith('/static/'):
            # If it's not already in templates or static, assume templates
            if not any(path.endswith(ext) for ext in ['.css', '.js', '.png', '.jpg', '.svg', '.ico']):
                path = '/templates' + path

        # Use parent class to do actual path translation
        return super().translate_path(path)

    def do_GET(self):
        # Check health endpoint FIRST
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({
                "status": "healthy",
                "service": "Healthcare-AI-Quantum-System Landing Page",
                "version": "1.0.0"
            })
            self.wfile.write(response.encode())
            return

        super().do_GET()

if __name__ == "__main__":
    print("=" * 70)
    print("🏥 Healthcare-AI-Quantum-System - Premium Landing Page")
    print("=" * 70)
    print("")
    print("✨ Features:")
    print("  • Bilingual (Turkish/English)")
    print("  • Animated particle background")
    print("  • Live API demonstrations")
    print("  • Quantum visualization")
    print("  • Premium UI/UX")
    print("")
    print("🌐 Server starting...")
    print(f"  • Landing Page: http://localhost:{PORT}")
    print("  • API Backend:  http://localhost:8000 (start separately with quickstart.py)")
    print("")
    print("📚 Quick Links:")
    print(f"  • Documentation: http://localhost:{PORT}/#features")
    print(f"  • Live Demo:     http://localhost:{PORT}/#demo")
    print(f"  • Tech Stack:    http://localhost:{PORT}/#tech")
    print("")
    print("=" * 70)
    print("")
    print(f"Server running on http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    print("")

    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped.")
