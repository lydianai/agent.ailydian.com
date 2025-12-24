# ⚡ HIZLI BAŞLANGIÇ REHBERİ

Bu doküman, projeyi **ilk kez** çalıştıracak geliştiriciler için hızlı kurulum rehberidir.

---

## 📋 Önkoşullar

Aşağıdaki yazılımların yüklü olduğundan emin olun:

### Zorunlu
- [x] **Python 3.11+** ([İndir](https://www.python.org/downloads/))
- [x] **Docker Desktop** ([İndir](https://www.docker.com/products/docker-desktop/))
- [x] **Git** ([İndir](https://git-scm.com/downloads))

### Opsiyonel (Production için)
- [ ] **Kubernetes** (minikube, kind, veya cloud K8s)
- [ ] **IBM Quantum Account** (quantum features için)
- [ ] **AWS/Azure Account** (cloud deployment için)

---

## 🚀 5 Dakikada Kurulum

### 1. Repository'yi İndir

```bash
# Terminal'i aç ve şu komutları çalıştır:
git clone https://github.com/your-org/HealthCare-AI-Quantum-System.git
cd HealthCare-AI-Quantum-System
```

### 2. Docker ile Tüm Sistemi Başlat

```bash
# Tüm servisleri başlat (PostgreSQL, MongoDB, Redis, Kafka, vb.)
docker-compose up -d

# Servislerin başladığını kontrol et
docker-compose ps
```

Beklenen çıktı:
```
NAME                          STATUS
healthcare-ai-postgres        Up 30 seconds
healthcare-ai-mongodb         Up 30 seconds
healthcare-ai-redis           Up 30 seconds
healthcare-ai-kafka           Up 30 seconds
```

### 3. Python Environment Hazırla

```bash
# Virtual environment oluştur
python3 -m venv venv

# Activate et
source venv/bin/activate  # Mac/Linux
# VEYA
venv\Scripts\activate     # Windows

# Dependencies yükle
pip install -r requirements.txt
```

### 4. Environment Variables Ayarla

```bash
# .env.example dosyasını kopyala
cp .env.example .env

# .env dosyasını bir text editör ile aç ve düzenle
# Örnek:
# OPENAI_API_KEY=sk-your-key-here
# POSTGRES_PASSWORD=your-secure-password
```

**ÖNEMLİ**: `.env` dosyasını **ASLA** git'e commit etme!

### 5. Database'leri Initialize Et

```bash
# Database migration'ları çalıştır
python scripts/init_databases.py

# Seed data ekle (test için)
python scripts/seed_test_data.py
```

### 6. İlk Agent'ı Çalıştır

```bash
# Clinical Decision Agent'ı başlat
cd agents/clinical-decision
python src/main.py
```

Başarılı olursa göreceksiniz:
```
🚀 Clinical Decision Agent started successfully!
📊 Listening on port 8080
🔗 Connected to database
✅ Ready to accept requests
```

### 7. Dashboard'u Aç (Opsiyonel)

```bash
# Yeni bir terminal aç
cd dashboard
npm install
npm run dev
```

Dashboard: http://localhost:3000

---

## ✅ Test Et

### API Testi

```bash
# Başka bir terminal'de:
curl -X POST http://localhost:8080/api/v1/health
```

Beklenen cevap:
```json
{
  "status": "healthy",
  "agent": "clinical-decision",
  "version": "1.0.0"
}
```

### Basit Tanı Testi

```bash
curl -X POST http://localhost:8080/api/v1/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "test-001",
    "symptoms": ["chest pain", "shortness of breath"],
    "vitals": {
      "heart_rate": 105,
      "blood_pressure": "145/92",
      "temperature": 37.2
    }
  }'
```

---

## 🛑 Durdurma

```bash
# Agent'ı durdur: Ctrl+C

# Docker servislerini durdur
docker-compose down

# Virtual environment'tan çık
deactivate
```

---

## 🐛 Sorun Giderme

### Problem: Docker başlamıyor

**Çözüm:**
```bash
# Docker Desktop'ın çalıştığından emin ol
docker --version

# Docker servisini restart et
# Mac: Docker Desktop'ı kapat/aç
# Linux: sudo systemctl restart docker
```

### Problem: Port already in use (8080)

**Çözüm:**
```bash
# Hangi process 8080'i kullanıyor bul
lsof -i :8080  # Mac/Linux
netstat -ano | findstr :8080  # Windows

# Process'i durdur veya başka port kullan
export AGENT_PORT=8081
python src/main.py
```

### Problem: Database connection error

**Çözüm:**
```bash
# PostgreSQL'in çalıştığını kontrol et
docker-compose ps | grep postgres

# Log'lara bak
docker-compose logs postgres

# Restart et
docker-compose restart postgres
```

### Problem: Python ModuleNotFoundError

**Çözüm:**
```bash
# Virtual environment'ın active olduğundan emin ol
which python  # /path/to/venv/bin/python görmeli

# Dependencies'i yeniden yükle
pip install -r requirements.txt --upgrade
```

---

## 📚 Sonraki Adımlar

Artık sistem çalışıyor! Şimdi:

1. **Dokümantasyonu Oku**:
   - [Proje Brief](docs/turkish/PROJE_BRIEF.md) - Genel bakış
   - [Teknik Yol Haritası](docs/turkish/TEKNIK_YOL_HARITASI.md) - Detaylı mimari

2. **Agent'ları Keşfet**:
   - `agents/clinical-decision/README.md`
   - `agents/resource-optimization/README.md`
   - (diğer agent'lar)

3. **Geliştirme Başlat**:
   - Test yaz: `tests/` klasörüne bak
   - Yeni feature ekle: Branch oluştur
   - Pull request gönder

---

## 🆘 Yardım

Sorun yaşıyorsan:

1. **Dokümantasyon**: `docs/` klasöründe ara
2. **Issues**: GitHub Issues'a bak
3. **Slack**: #healthcare-ai-dev kanalına sor
4. **Email**: dev-team@healthcare-ai-quantum.com

---

## ⚡ Hızlı Komutlar Özeti

```bash
# Başlat
docker-compose up -d
source venv/bin/activate
cd agents/clinical-decision && python src/main.py

# Test
curl http://localhost:8080/api/v1/health

# Durdur
docker-compose down
deactivate
```

---

**Happy Coding! 🚀**
