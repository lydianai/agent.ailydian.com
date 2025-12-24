# 🚀 LOCALHOST KULLANIM REHBERİ
## Healthcare-AI-Quantum-System

---

## ✅ SİSTEM AKTİF!

Sistem şu anda **http://localhost:8000** adresinde çalışıyor!

---

## 📋 HIZLI ERİŞİM

### Web Arayüzü (Tarayıcıdan)

1. **API Dokümantasyonu (Swagger UI):**
   ```
   http://localhost:8000/docs
   ```
   ↳ Interaktif API testi, tüm endpoint'leri dene

2. **Sistem Sağlık Kontrolü:**
   ```
   http://localhost:8000/health
   ```
   ↳ Sistemin durumunu kontrol et

3. **API Bilgisi:**
   ```
   http://localhost:8000/
   ```
   ↳ Mevcut endpoint'ler ve versiyon bilgisi

---

## 🧪 TEST SENARYOLARI

### Senaryo 1: Göğüs Ağrısı Tanısı

**Tarayıcıda:** http://localhost:8000/docs açın ve `/api/v1/clinical-decision/diagnose` endpoint'ini deneyin

**Terminal'de:**
```bash
curl -X POST http://localhost:8000/api/v1/clinical-decision/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P-12345",
    "chief_complaint": "chest pain and shortness of breath",
    "symptoms": ["diaphoresis", "nausea", "arm pain"],
    "vitals": {
      "heart_rate": 105,
      "blood_pressure_systolic": 145,
      "blood_pressure_diastolic": 92,
      "oxygen_saturation": 94.0,
      "temperature": 37.1,
      "respiratory_rate": 20
    },
    "medical_history": ["hypertension", "diabetes"],
    "current_medications": ["metformin", "lisinopril"]
  }'
```

**Beklenen Sonuç:**
- Primary Diagnosis: Acute Coronary Syndrome
- Differential Diagnosis: AMI, Unstable Angina, GERD
- Recommended Tests: Troponin, ECG, Chest X-ray
- Treatment: Aspirin STAT, Nitroglycerin, Cardiac monitoring

---

### Senaryo 2: Yoğun Bakım Hasta İzleme

**Terminal'de:**
```bash
curl -X POST http://localhost:8000/api/v1/patient-monitoring/assess \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "ICU-001",
    "vital_signs": {
      "heart_rate": 125,
      "blood_pressure_systolic": 85,
      "blood_pressure_diastolic": 55,
      "oxygen_saturation": 88.0,
      "temperature": 38.9,
      "respiratory_rate": 26
    }
  }'
```

**Beklenen Sonuç:**
- NEWS2 Score: 12 (HIGH RISK)
- Sepsis Risk: HIGH (qSOFA 2/3)
- Alerts: Hypoxemia, Hypotension, Sepsis risk
- Recommendations: Urgent ICU transfer, increase monitoring

---

### Senaryo 3: Ateş Şikayeti

```bash
curl -X POST http://localhost:8000/api/v1/clinical-decision/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P-67890",
    "chief_complaint": "fever and chills",
    "symptoms": ["fatigue", "body aches", "headache"],
    "vitals": {
      "heart_rate": 98,
      "blood_pressure_systolic": 120,
      "blood_pressure_diastolic": 78,
      "oxygen_saturation": 97.0,
      "temperature": 39.2,
      "respiratory_rate": 18
    }
  }'
```

**Beklenen Sonuç:**
- Primary Diagnosis: Fever of Unknown Origin
- Tests: CBC, Blood cultures, Urinalysis
- Treatment: Acetaminophen, fluids, monitoring

---

### Senaryo 4: Baş Ağrısı

```bash
curl -X POST http://localhost:8000/api/v1/clinical-decision/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P-11111",
    "chief_complaint": "severe headache",
    "symptoms": ["photophobia", "nausea"],
    "vitals": {
      "heart_rate": 88,
      "blood_pressure_systolic": 125,
      "blood_pressure_diastolic": 80,
      "temperature": 37.0
    }
  }'
```

---

## 🎯 HAZIR TEST SCRİPTİ

Tüm testleri otomatik çalıştır:

```bash
./test_system.sh
```

Bu script:
✅ Health check
✅ API info
✅ Clinical diagnosis (chest pain)
✅ Patient monitoring (ICU case)
✅ Agent metrics

---

## 🔧 SİSTEM YÖNETİMİ

### Sistemin Çalışıp Çalışmadığını Kontrol Et

```bash
curl http://localhost:8000/health
```

Yanıt:
```json
{
  "status": "healthy",
  "service": "Healthcare-AI-Quantum-System",
  "version": "1.0.0",
  "mode": "demo"
}
```

### Server Loglarını Görüntüle

```bash
tail -f server.log
```

### Sistemi Durdur

```bash
kill $(cat server.pid)
```

veya:

```bash
pkill -f "python quickstart.py"
```

### Sistemi Yeniden Başlat

```bash
# Önce durdur
kill $(cat server.pid)

# Sonra başlat
source venv/bin/activate
python quickstart.py > server.log 2>&1 &
echo $! > server.pid
```

### Port Kullanımını Kontrol Et

```bash
lsof -i :8000
```

---

## 📊 AGENT'LAR VE YETENEKLERİ

### 1. Clinical Decision Agent (Klinik Karar)
**Endpoint:** `POST /api/v1/clinical-decision/diagnose`

**Yetenekler:**
- ✅ Diferansiyel tanı (5 olası tanı)
- ✅ Olasılık skorları (%0-100)
- ✅ ICD-10 kodları
- ✅ Önerilen testler (LOINC uyumlu)
- ✅ Tedavi önerileri (kanıta dayalı)
- ✅ Acil bulgular tespiti
- ✅ İlaç etkileşimi uyarıları

**Örnek Giriş:**
```json
{
  "patient_id": "P-001",
  "chief_complaint": "chest pain",
  "symptoms": ["shortness of breath", "nausea"],
  "vitals": {
    "heart_rate": 105,
    "blood_pressure_systolic": 145
  }
}
```

### 2. Patient Monitoring Agent (Hasta İzleme)
**Endpoint:** `POST /api/v1/patient-monitoring/assess`

**Yetenekler:**
- ✅ NEWS2 skorlama (0-20)
- ✅ Sepsis risk değerlendirmesi (qSOFA)
- ✅ Risk seviyesi (LOW/MEDIUM/HIGH)
- ✅ Otomatik alert üretimi
- ✅ Vital signs analizi
- ✅ Klinik öneriler

**Örnek Giriş:**
```json
{
  "patient_id": "ICU-001",
  "vital_signs": {
    "heart_rate": 110,
    "blood_pressure_systolic": 90,
    "oxygen_saturation": 92.0,
    "temperature": 38.5,
    "respiratory_rate": 24
  }
}
```

### 3. Resource Optimization Agent (Kaynak Optimizasyonu)
**Durum:** Offline (IBM Quantum credentials gerektirir)

Tam sistem için:
- Quantum QAOA optimizasyonu
- Ameliyathane çizelgeleme
- Kaynak dağılımı

---

## ⚙️ SİSTEM MODLARı

### Demo Mode (Şu Anda Aktif)
- ✅ API key'siz çalışır
- ✅ Database'siz çalışır
- ✅ Rule-based logic kullanır
- ✅ Gerçekçi sonuçlar üretir
- ⚠️ LLM yok (GPT-4/Claude)
- ⚠️ Quantum optimization yok

### Full Mode (Production)
Gereksinimler:
- OpenAI API Key (GPT-4o)
- Anthropic API Key (Claude Opus)
- IBM Quantum Token
- PostgreSQL database
- MongoDB database
- Redis cache
- Apache Kafka

Full mode için: `main.py` kullanın (quickstart.py yerine)

---

## 🌐 SWAGGER UI KULLANIMI

1. **Tarayıcıda aç:** http://localhost:8000/docs

2. **Endpoint seç:** Örn. `/api/v1/clinical-decision/diagnose`

3. **"Try it out" tıkla**

4. **Request body düzenle:**
```json
{
  "patient_id": "TEST-001",
  "chief_complaint": "chest pain",
  "symptoms": ["nausea"]
}
```

5. **"Execute" tıkla**

6. **Sonucu görüntüle:** Response body'de JSON sonuç

---

## 📱 MOBIL/UZAK ERİŞİM

### Aynı ağdaki cihazlardan erişim

1. IP adresinizi öğrenin:
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

2. Diğer cihazlardan erişin:
```
http://YOUR_IP:8000
```

Örnek:
```
http://192.168.1.100:8000/docs
```

### Güvenlik Duvarı

Port 8000'i açmanız gerekebilir:
```bash
# macOS
sudo pfctl -e
sudo pfctl -f /etc/pf.conf
```

---

## 🐛 SORUN GİDERME

### Problem: "Connection refused"

**Çözüm:**
```bash
# Server çalışıyor mu?
curl http://localhost:8000/health

# Çalışmıyorsa, yeniden başlat
source venv/bin/activate
python quickstart.py &
```

### Problem: "Port already in use"

**Çözüm:**
```bash
# Port kullanan process'i bul
lsof -i :8000

# Process'i sonlandır
kill -9 <PID>

# Veya farklı port kullan
# quickstart.py'de PORT değiştir
```

### Problem: "Module not found"

**Çözüm:**
```bash
# Virtual environment aktif mi?
source venv/bin/activate

# Paketler yüklü mü?
pip list | grep fastapi

# Yoksa yükle
pip install fastapi uvicorn pydantic
```

### Problem: "Slow response"

**Neden:** Demo mode rule-based, hızlı olmalı.

**Kontrol:**
```bash
# CPU kullanımı
top | grep python

# Memory kullanımı
ps aux | grep python

# Restart
kill $(cat server.pid)
python quickstart.py &
```

---

## 📈 PERFORFans BEKLENTİLERİ

### Demo Mode (Aktif)
- Health check: <10ms
- Clinical diagnosis: ~50ms (rule-based)
- Patient monitoring: ~20ms (calculation)
- Memory: ~50MB

### Full Mode (Production)
- Health check: <10ms
- Clinical diagnosis: ~2-3 seconds (GPT-4 call)
- Patient monitoring: ~100-200ms (Kafka + ML)
- Resource optimization: ~8-10 minutes (Quantum QAOA)
- Memory: ~2GB (all agents)

---

## 🔐 GÜVENLİK NOTLARI

### Demo Mode Güvenlik

⚠️ **UYARI:** Bu demo version production kullanıma uygun DEĞİLDİR!

Eksikler:
- ❌ Authentication yok
- ❌ Rate limiting yok
- ❌ Input validation minimal
- ❌ PHI encryption yok
- ❌ Audit logging yok
- ❌ HTTPS yok

### Production Güvenlik

Full system (`main.py`) içerir:
- ✅ JWT authentication
- ✅ Role-based access control (RBAC)
- ✅ HIPAA-compliant logging
- ✅ PHI encryption
- ✅ Rate limiting
- ✅ TLS/HTTPS
- ✅ Audit trails

---

## 📞 DESTEK

### Logları İncele
```bash
# Son 50 satır
tail -50 server.log

# Canlı izle
tail -f server.log

# Hata ara
grep ERROR server.log
```

### Sistem Bilgisi
```bash
# Python versiyonu
python --version

# Yüklü paketler
pip list

# Disk kullanımı
df -h

# Memory kullanımı
free -m  # Linux
vm_stat  # macOS
```

---

## 🎓 ÖRNEK KULLANIM SENARYOSU

### Acil Servis Workflow

```bash
# 1. Hasta geldi - vital signs kaydedildi
curl -X POST http://localhost:8000/api/v1/patient-monitoring/assess \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "ER-20251223-001",
    "vital_signs": {
      "heart_rate": 110,
      "blood_pressure_systolic": 95,
      "oxygen_saturation": 93.0,
      "temperature": 38.2,
      "respiratory_rate": 22
    }
  }'

# Sonuç: NEWS2=7 (MEDIUM), Sepsis risk ELEVATED

# 2. Doktor muayene etti - tanı desteği iste
curl -X POST http://localhost:8000/api/v1/clinical-decision/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "ER-20251223-001",
    "chief_complaint": "fever and confusion",
    "symptoms": ["chills", "decreased urine output"],
    "vitals": {
      "heart_rate": 110,
      "blood_pressure_systolic": 95,
      "temperature": 38.2,
      "respiratory_rate": 22
    },
    "medical_history": ["chronic UTI", "diabetes"]
  }'

# Sonuç: Possible sepsis, immediate antibiotics, ICU consult

# 3. Tedavi başladı - vital signs yeniden kontrol
curl -X POST http://localhost:8000/api/v1/patient-monitoring/assess \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "ER-20251223-001",
    "vital_signs": {
      "heart_rate": 95,
      "blood_pressure_systolic": 110,
      "oxygen_saturation": 96.0,
      "temperature": 37.8,
      "respiratory_rate": 18
    }
  }'

# Sonuç: NEWS2=3 (LOW), improving trend
```

---

## 🚀 SONRAKI ADIMLAR

### Demo'dan Full System'e Geçiş

1. **API Keys Edinin:**
   ```bash
   # OpenAI
   https://platform.openai.com/api-keys

   # Anthropic
   https://console.anthropic.com/

   # IBM Quantum
   https://quantum-computing.ibm.com/
   ```

2. **Database'leri Kurun:**
   ```bash
   docker-compose up -d postgres mongodb redis kafka
   ```

3. **Environment Ayarlayın:**
   ```bash
   cp .env.example .env
   # .env dosyasını düzenleyin, API key'leri ekleyin
   ```

4. **Migration Çalıştırın:**
   ```bash
   alembic upgrade head
   ```

5. **Full System Başlatın:**
   ```bash
   python main.py
   ```

### Ek Özellikler Ekleyin

- [ ] Radiology AI agent
- [ ] Pharmacy management
- [ ] Mobile app (React Native)
- [ ] Telegram bot notifications
- [ ] Voice interface (Siri/Alexa)

---

## ✅ ÖZET

**Sistem Durumu:** ✅ Aktif ve çalışıyor
**Port:** 8000
**Mode:** Demo (API key'siz)
**Erişim:** http://localhost:8000

**Hızlı Test:**
```bash
curl http://localhost:8000/health
```

**İnteraktif Dokümantasyon:**
```
http://localhost:8000/docs
```

**Sistem Durdur:**
```bash
kill $(cat server.pid)
```

---

**🎉 BAŞARILAR! SİSTEM HAZIR KULLANIMA.**

_Healthcare-AI-Quantum-System v1.0.0_
