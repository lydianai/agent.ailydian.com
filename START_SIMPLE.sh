#!/bin/bash

echo "🏥 LYDIAN HEALTHCARE AI SYSTEM 🏥"
echo "=================================="
echo ""

# Virtual environment'i aktive et
if [ -d "venv" ]; then
    echo "✓ Virtual environment bulundu, aktive ediliyor..."
    source venv/bin/activate
else
    echo "⚠ Virtual environment bulunamadı, oluşturuluyor..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Paketler yükleniyor..."
    pip install fastapi uvicorn python-multipart websockets pydantic --quiet
fi

echo ""
echo "🚀 Sunucu başlatılıyor..."
echo ""
echo "📍 Erişim Adresleri:"
echo "   Dashboard:  http://localhost:8000/"
echo "   Emergency:  http://localhost:8000/emergency"
echo "   Diagnosis:  http://localhost:8000/diagnosis"
echo "   API Docs:   http://localhost:8000/api/docs"
echo ""
echo "⚡ Durdurmak için CTRL+C"
echo ""

# Sunucuyu başlat
python3 main.py
