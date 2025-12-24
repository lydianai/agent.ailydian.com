#!/bin/bash

# Healthcare AI System - Localhost Başlatma Scripti
# Bu script tüm sistemi localhost'ta çalıştırır

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║          🏥 LYDIAN HEALTHCARE AI SYSTEM 🏥                  ║"
echo "║                                                              ║"
echo "║  AI-Powered Healthcare Management Platform                   ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Renk kodları
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Proje dizinine git
cd "$(dirname "$0")"

echo -e "${BLUE}📂 Proje Dizini:${NC} $(pwd)"
echo ""

# Python versiyonunu kontrol et
echo -e "${YELLOW}🔍 Python versiyonu kontrol ediliyor...${NC}"
python3 --version
echo ""

# Gerekli paketleri kontrol et
echo -e "${YELLOW}📦 Gerekli paketler kontrol ediliyor...${NC}"
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${RED}❌ FastAPI yüklü değil!${NC}"
    echo -e "${YELLOW}Yükleniyor...${NC}"
    pip3 install fastapi uvicorn python-multipart websockets
fi

if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo -e "${RED}❌ Uvicorn yüklü değil!${NC}"
    echo -e "${YELLOW}Yükleniyor...${NC}"
    pip3 install uvicorn
fi

echo -e "${GREEN}✓ Tüm paketler hazır${NC}"
echo ""

# Frontend dosyalarını kontrol et
echo -e "${YELLOW}🎨 Frontend dosyaları kontrol ediliyor...${NC}"
if [ -d "frontend/pages" ]; then
    echo -e "${GREEN}✓ Dashboard:${NC} $([ -f "frontend/pages/dashboard.html" ] && echo "✓" || echo "❌")"
    echo -e "${GREEN}✓ Emergency:${NC} $([ -f "frontend/pages/emergency.html" ] && echo "✓" || echo "❌")"
    echo -e "${GREEN}✓ Diagnosis:${NC} $([ -f "frontend/pages/diagnosis.html" ] && echo "✓" || echo "❌")"
else
    echo -e "${RED}❌ Frontend klasörü bulunamadı!${NC}"
fi
echo ""

# API routes kontrolü
echo -e "${YELLOW}🔌 API routes kontrol ediliyor...${NC}"
if [ -d "api/routes" ]; then
    echo -e "${GREEN}✓ Emergency API:${NC} $([ -f "api/routes/emergency.py" ] && echo "✓" || echo "❌")"
    echo -e "${GREEN}✓ Diagnosis API:${NC} $([ -f "api/routes/diagnosis.py" ] && echo "✓" || echo "❌")"
    echo -e "${GREEN}✓ Treatment API:${NC} $([ -f "api/routes/treatment.py" ] && echo "✓" || echo "❌")"
    echo -e "${GREEN}✓ Pharmacy API:${NC} $([ -f "api/routes/pharmacy.py" ] && echo "✓" || echo "❌")"
else
    echo -e "${RED}❌ API routes klasörü bulunamadı!${NC}"
fi
echo ""

# Agents kontrolü
echo -e "${YELLOW}🤖 AI Agents kontrol ediliyor...${NC}"
if [ -d "agents" ]; then
    echo -e "${GREEN}✓ Emergency Agent:${NC} $([ -f "agents/emergency/agent.py" ] && echo "✓" || echo "❌")"
    echo -e "${GREEN}✓ Diagnosis Agent:${NC} $([ -f "agents/diagnosis/agent.py" ] && echo "✓" || echo "❌")"
    echo -e "${GREEN}✓ Treatment Agent:${NC} $([ -f "agents/treatment/agent.py" ] && echo "✓" || echo "❌")"
    echo -e "${GREEN}✓ Pharmacy Agent:${NC} $([ -f "agents/pharmacy/agent.py" ] && echo "✓" || echo "❌")"
else
    echo -e "${RED}❌ Agents klasörü bulunamadı!${NC}"
fi
echo ""

# Port kontrolü
echo -e "${YELLOW}🔍 Port 8000 kontrol ediliyor...${NC}"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}⚠ Port 8000 zaten kullanımda!${NC}"
    echo -e "${YELLOW}Mevcut process sonlandırılıyor...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 2
fi
echo -e "${GREEN}✓ Port 8000 hazır${NC}"
echo ""

# Sunucuyu başlat
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🚀 SUNUCU BAŞLATILIYOR                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}📍 Erişim Adresleri:${NC}"
echo ""
echo -e "   ${BLUE}Dashboard:${NC}     http://localhost:8000/"
echo -e "   ${BLUE}Emergency:${NC}     http://localhost:8000/emergency"
echo -e "   ${BLUE}Diagnosis:${NC}     http://localhost:8000/diagnosis"
echo -e "   ${BLUE}Treatment:${NC}     http://localhost:8000/treatment"
echo -e "   ${BLUE}Pharmacy:${NC}      http://localhost:8000/pharmacy"
echo -e "   ${BLUE}Patients:${NC}      http://localhost:8000/patients"
echo ""
echo -e "   ${BLUE}API Docs:${NC}      http://localhost:8000/api/docs"
echo -e "   ${BLUE}Health:${NC}        http://localhost:8000/health"
echo ""
echo -e "${YELLOW}⚡ Sunucuyu durdurmak için CTRL+C tuşlarına basın${NC}"
echo ""
echo "================================================================"
echo ""

# Sunucuyu başlat
python3 main.py
