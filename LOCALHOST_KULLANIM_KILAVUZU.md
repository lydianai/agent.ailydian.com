# 🏥 Lydian Healthcare AI System - Localhost Kullanım Kılavuzu

## 🚀 Hızlı Başlangıç (3 Adımda Çalıştır!)

### 1️⃣ Terminal'i Aç
```bash
cd /Users/sardag/Desktop/HealthCare-AI-Quantum-System
```

### 2️⃣ Başlatma Scriptini Çalıştır
```bash
./START_LOCALHOST.sh
```

### 3️⃣ Tarayıcıda Aç
```
http://localhost:8000
```

**🎉 Hazır! Sistem çalışıyor!**

---

## 📍 Tüm Sayfalar

| Sayfa | URL | Durum |
|-------|-----|-------|
| 🏠 **Dashboard** | http://localhost:8000/ | ✅ Tam Fonksiyonel |
| 🚑 **Emergency** | http://localhost:8000/emergency | ✅ Tam Fonksiyonel |
| 🧠 **AI Diagnosis** | http://localhost:8000/diagnosis | ✅ Tam Fonksiyonel |
| 💊 **Treatment** | http://localhost:8000/treatment | 🔄 Geliştirme Aşamasında |
| 💉 **Pharmacy** | http://localhost:8000/pharmacy | 🔄 Geliştirme Aşamasında |
| 👥 **Patients** | http://localhost:8000/patients | 🔄 Geliştirme Aşamasında |

---

## 📚 API Documentation

**Swagger UI:** http://localhost:8000/api/docs
**ReDoc:** http://localhost:8000/api/redoc

---

## 🔧 Manuel Başlatma (Alternatif)

Eğer script çalışmazsa, manuel olarak başlatabilirsiniz:

```bash
# 1. Gerekli paketleri yükleyin
pip3 install fastapi uvicorn python-multipart websockets pydantic

# 2. Sunucuyu başlatın
python3 main.py
```

---

## 🎯 Özellik Testleri

### Dashboard Testi
1. http://localhost:8000/ adresini açın
2. **4 istatistik kartını** görmelisiniz (Active Patients, Emergency Cases, AI Diagnoses, Prescriptions)
3. **2 grafik** görmelisiniz (Patient Flow, Triage Distribution)
4. **Recent Activity** ve **Active Alerts** panellerini kontrol edin
5. **Quick Actions** butonlarını test edin

### Emergency Triage Testi
1. http://localhost:8000/emergency adresini açın
2. **Triage Form**'u doldurun:
   - Patient ID: `P-TEST001`
   - Arrival Time: Şu anki zaman
   - Chief Complaint: `"Severe chest pain radiating to left arm"`
   - Vital Signs:
     - BP: 180/110
     - Heart Rate: 120
     - Respiratory Rate: 24
     - Temperature: 37.2
     - O2 Saturation: 94
     - GCS: 15
     - Pain Scale: 9
   - Symptoms: ✓ Chest Pain, ✓ Difficulty Breathing
3. **"Perform Triage Assessment"** butonuna tıklayın
4. **AI Triage Sonucunu** görmelisiniz:
   - ESI Level (muhtemelen Level 2 - EMERGENT)
   - ABCDE Assessment
   - Immediate Actions
   - Activated Protocols (STEMI Protocol)

### AI Diagnosis Testi
1. http://localhost:8000/diagnosis adresini açın
2. **Diagnosis Form**'u doldurun:
   - Patient ID: `P-TEST002`
   - Age: 55
   - Gender: Male
   - Presenting Symptoms: `"Persistent cough, fever, difficulty breathing for 3 days"`
   - Medical History: `"Diabetes, Hypertension"`
3. **(Opsiyonel)** Medikal görüntü yükleyin (drag & drop)
4. **Laboratory Results** (opsiyonel):
   - WBC: 15.5 (yüksek)
   - Hemoglobin: 13.2
   - Temperature: 38.5°C
5. **"Analyze with AI"** butonuna tıklayın
6. **AI Diagnosis Sonucunu** görmelisiniz:
   - Confidence Score (%)
   - Primary Diagnosis (ICD-10 koduyla)
   - Differential Diagnosis (top 5)
   - Imaging Findings (eğer yüklediyseniz)
   - Clinical Reasoning
   - Recommendations (Tests, Specialists, Follow-up)
   - Risk Stratification

---

## 🔌 API Endpoint Testleri

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Beklenen Sonuç:**
```json
{
  "status": "healthy",
  "service": "Healthcare AI System",
  "version": "1.0.0"
}
```

### 2. System Info
```bash
curl http://localhost:8000/api/system/info
```

### 3. Emergency Triage API
```bash
curl -X POST "http://localhost:8000/api/v1/emergency/triage" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P-TEST001",
    "chief_complaint": "Chest pain",
    "vital_signs": {
      "heart_rate": 120,
      "blood_pressure_systolic": 180,
      "blood_pressure_diastolic": 110,
      "respiratory_rate": 24,
      "temperature": 37.2,
      "oxygen_saturation": 94,
      "glasgow_coma_scale": 15
    },
    "symptoms": ["chest_pain", "difficulty_breathing"]
  }'
```

### 4. AI Diagnosis API
```bash
curl -X POST "http://localhost:8000/api/v1/diagnosis/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P-TEST002",
    "imaging_data": {
      "modality": "x_ray",
      "body_region": "chest"
    },
    "clinical_data": {
      "age": 55,
      "gender": "male",
      "presenting_symptoms": "Persistent cough, fever"
    }
  }'
```

---

## 🐛 Sorun Giderme

### Problem: "Port 8000 already in use"
**Çözüm:**
```bash
# Port'u kullanan process'i bul ve sonlandır
lsof -ti:8000 | xargs kill -9

# Sonra tekrar başlat
./START_LOCALHOST.sh
```

### Problem: "Module not found: fastapi"
**Çözüm:**
```bash
pip3 install fastapi uvicorn python-multipart websockets pydantic
```

### Problem: Frontend sayfaları görünmüyor
**Çözüm:**
```bash
# Frontend klasörünün varlığını kontrol edin
ls -la frontend/pages/

# Şu dosyalar olmalı:
# - dashboard.html
# - emergency.html
# - diagnosis.html
```

### Problem: API routes çalışmıyor
**Çözüm:**
```bash
# API routes klasörünü kontrol edin
ls -la api/routes/

# Şu dosyalar olmalı:
# - emergency.py
# - diagnosis.py
# - treatment.py
# - pharmacy.py
# - __init__.py
```

---

## 📂 Proje Yapısı

```
HealthCare-AI-Quantum-System/
├── main.py                          # Ana FastAPI uygulaması
├── START_LOCALHOST.sh               # Hızlı başlatma scripti
│
├── frontend/                        # Frontend dosyaları
│   ├── pages/
│   │   ├── dashboard.html          ✅ Tamamlandı
│   │   ├── emergency.html          ✅ Tamamlandı
│   │   └── diagnosis.html          ✅ Tamamlandı
│   │
│   └── static/
│       ├── css/
│       │   ├── dashboard.css
│       │   ├── emergency.css
│       │   ├── diagnosis.css
│       │   └── treatment-pharmacy-patients.css
│       │
│       └── js/
│           ├── dashboard.js
│           ├── emergency.js
│           └── diagnosis.js
│
├── api/                            # Backend API
│   ├── routes/
│   │   ├── emergency.py           ✅ Emergency triage API
│   │   ├── diagnosis.py           ✅ AI diagnosis API
│   │   ├── treatment.py           ✅ Treatment planning API
│   │   └── pharmacy.py            ✅ Pharmacy management API
│   │
│   └── websocket/
│       ├── manager.py             ✅ WebSocket connection manager
│       └── routes.py              ✅ WebSocket endpoints
│
├── agents/                         # AI Agents
│   ├── emergency/
│   │   └── agent.py               ✅ Emergency triage agent (ESI)
│   ├── diagnosis/
│   │   └── agent.py               ✅ AI diagnosis agent
│   ├── treatment/
│   │   └── agent.py               ✅ Treatment planning agent
│   └── pharmacy/
│       └── agent.py               ✅ Pharmacy management agent
│
└── integrations/                   # Entegrasyonlar
    └── fhir/
        └── models.py              ✅ FHIR R4 modelleri
```

---

## 🎨 Kullanıcı Arayüzü Özellikleri

### ✅ Dashboard
- Real-time istatistikler
- Chart.js grafikleri
- Activity feed
- Alert paneli
- Quick actions

### ✅ Emergency
- ESI Level 1-5 triage
- Vital signs monitoring
- ABCDE assessment
- Protocol activation
- Active cases grid

### ✅ Diagnosis
- Medical imaging upload (drag & drop)
- AI-powered diagnosis
- Confidence scoring
- Differential diagnosis
- Risk stratification
- Clinical reasoning

### 🔄 Treatment (Yakında)
- Evidence-based treatment planning
- Drug interaction checking
- Medication orders

### 🔄 Pharmacy (Yakında)
- Prescription verification
- Dosage calculation
- ADR monitoring

### 🔄 Patients (Yakında)
- Patient records
- Medical history
- Document management

---

## 🚦 Sistem Durumu

| Bileşen | Durum | Açıklama |
|---------|-------|----------|
| Backend API | ✅ Çalışıyor | FastAPI + Uvicorn |
| Frontend Pages | ✅ Çalışıyor | 3/6 sayfa tamamlandı |
| AI Agents | ✅ Çalışıyor | 4 agent aktif |
| WebSocket | ✅ Hazır | Real-time updates için hazır |
| Database | ⚠️ Opsiyonel | SQLite/PostgreSQL bağlanabilir |
| FHIR Integration | ✅ Hazır | FHIR R4 modelleri hazır |

---

## 📞 Destek

Herhangi bir sorun yaşarsanız:

1. **Logları kontrol edin:**
   ```bash
   tail -f backend.log
   ```

2. **Health check yapın:**
   ```bash
   curl http://localhost:8000/health
   ```

3. **API docs'u inceleyin:**
   http://localhost:8000/api/docs

---

## 🎯 Sonraki Adımlar

1. ✅ Dashboard, Emergency, Diagnosis sayfaları çalışıyor
2. 🔄 Treatment, Pharmacy, Patients sayfalarını tamamlayın
3. 🔄 Veritabanı bağlantısı ekleyin (PostgreSQL)
4. 🔄 Kullanıcı authentication ekleyin
5. 🔄 Production deployment yapın (Vercel/AWS)

---

**🏥 Lydian Healthcare AI System - v1.0.0**
**📅 Son Güncelleme: 2024-01-15**
