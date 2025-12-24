#!/bin/bash

# HIZLI BAŞLATMA SCRIPTI - Basit Frontend Server

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          🏥 LYD IAN HEALTHCARE AI SYSTEM 🏥                  ║"
echo "║              Hızlı Başlatma (Frontend Modlu)                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Python frontend sunucusunu çalıştır
python3.12 << 'PYEOF'
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

os.chdir('frontend')

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        # Route mapping
        if self.path == '/' or self.path == '/dashboard':
            self.path = '/pages/dashboard.html'
        elif self.path == '/emergency':
            self.path = '/pages/emergency.html'
        elif self.path == '/diagnosis':
            self.path = '/pages/diagnosis.html'
        elif self.path.startswith('/static/'):
            pass  # Keep static files as is
        elif not '.' in os.path.basename(self.path):
            # No extension, might be a page route
            if os.path.exists(f'pages{self.path}.html'):
                self.path = f'/pages{self.path}.html'

        return SimpleHTTPRequestHandler.do_GET(self)

print("=" * 70)
print("🚀 Frontend sunucusu başlatılıyor...")
print("")
print("📍 Erişim Adresleri:")
print("   Dashboard:  http://localhost:3500/")
print("   Emergency:  http://localhost:3500/emergency")
print("   Diagnosis:  http://localhost:3500/diagnosis")
print("")
print("⚡ Durdurmak için CTRL+C")
print("=" * 70)
print("")

server = HTTPServer(('', 3500), MyHandler)
server.serve_forever()
PYEOF
