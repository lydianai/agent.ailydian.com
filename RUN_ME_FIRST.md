# 🚀 ÇAL IŞTIRMA REHBERİ

## İlk Kurulum (5 dakika)

### 1. Ortam Değişkenlerini Ayarla

```bash
# .env dosyasını oluştur
cp .env.example .env

# .env dosyasını bir text editörde aç ve şunları düzenle:
# - OPENAI_API_KEY=sk-your-actual-key-here
# - ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
# (En az birini doldur)
```

### 2. Servisleri Başlat

```bash
# Docker servislerini başlat (PostgreSQL, MongoDB, Redis, Kafka)
./scripts/start_local.sh

# VEYA manuel olarak:
docker-compose up -d
```

### 3. Python Dependencies Yükle

```bash
# Virtual environment oluştur (opsiyonel ama önerilen)
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows

# Dependencies yükle
pip install -r requirements.txt
```

### 4. API'yi Başlat

```bash
# Development modunda başlat
python main.py
```

API şu adreste çalışacak: **http://localhost:8080**

### 5. Test Et!

```bash
# Yeni bir terminal aç ve test script'ini çalıştır:
python scripts/test_api.py
```

---

## 📊 Neler Çalışıyor?

Sistem başarıyla başlatıldıktan sonra:

✅ **API Server**: http://localhost:8080
- Interactive docs: http://localhost:8080/docs
- Health check: http://localhost:8080/health

✅ **Clinical Decision Agent**: Aktif ve hazır
- GPT-4/Claude ile tanı desteği
- İlaç etkileşim kontrolü
- Acil durum tespiti

✅ **Databases**:
- PostgreSQL (port 5432)
- MongoDB (port 27017)
- Redis (port 6379)
- Kafka (port 9092)

---

## 🧪 API'yi Test Etme

### Postman / cURL ile:

```bash
curl -X POST "http://localhost:8080/api/v1/clinical-decision/diagnose" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "550e8400-e29b-41d4-a716-446655440000",
    "chief_complaint": "chest pain and shortness of breath",
    "symptoms": ["chest pain", "shortness of breath", "diaphoresis"],
    "vitals": {
      "heart_rate": 105,
      "blood_pressure_systolic": 145,
      "blood_pressure_diastolic": 92,
      "temperature": 37.2,
      "oxygen_saturation": 94.0
    },
    "medical_history": ["hypertension", "diabetes"],
    "current_medications": ["metformin", "lisinopril"],
    "labs": {
      "troponin": 0.8,
      "BNP": 450
    }
  }'
```

### Python Script ile:

```python
import requests

response = requests.post(
    "http://localhost:8080/api/v1/clinical-decision/diagnose",
    json={
        "patient_id": "550e8400-e29b-41d4-a716-446655440000",
        "chief_complaint": "chest pain",
        "symptoms": ["chest pain"],
        "vitals": {"heart_rate": 105}
    }
)

print(response.json())
```

---

## 🎯 Örnek Çıktı

```json
{
  "decision_id": "...",
  "primary_diagnosis": {
    "diagnosis": "Acute Coronary Syndrome - NSTEMI",
    "probability": 0.85,
    "severity": "critical"
  },
  "differential_diagnoses": [
    {
      "diagnosis": "Acute Coronary Syndrome",
      "probability": 0.85
    },
    {
      "diagnosis": "Pulmonary Embolism",
      "probability": 0.10
    }
  ],
  "confidence": 0.85,
  "recommended_tests": [
    {
      "test": "ECG",
      "urgency": "immediate",
      "reason": "Rule out STEMI"
    },
    {
      "test": "Troponin serial",
      "urgency": "within 1 hour"
    }
  ],
  "treatment_suggestions": [
    {
      "treatment": "Aspirin 325mg",
      "urgency": "immediate"
    },
    {
      "treatment": "Cardiology consult",
      "urgency": "within 1 hour"
    }
  ],
  "drug_warnings": [],
  "requires_human_review": false,
  "urgent_flags": [
    "HIGH PROBABILITY CRITICAL CONDITION: Acute Coronary Syndrome (85%)",
    "IMMEDIATE TEST REQUIRED: ECG"
  ]
}
```

---

## 🔧 Sorun Giderme

### Problem: "Docker is not running"
**Çözüm**: Docker Desktop'ı başlat

### Problem: "Module not found"
**Çözüm**: `pip install -r requirements.txt`

### Problem: "Database connection failed"
**Çözüm**: `docker-compose restart postgres`

### Problem: "OpenAI API error"
**Çözüm**: `.env` dosyasında `OPENAI_API_KEY` değerini kontrol et

---

## 📚 Daha Fazla Bilgi

- **Dokümantasyon**: `docs/turkish/` klasörüne bak
- **API Docs**: http://localhost:8080/docs
- **Test Suite**: `pytest tests/ -v`

---

## 🎉 Hazırsın!

Sistem şimdi çalışıyor ve gerçek hasta verileri ile tanı yapabiliyor!

**Önemli**: Bu sistem development modunda. Production'a geçmeden önce:
1. Tüm güvenlik ayarlarını yap
2. HIPAA compliance kontrolleri tamamla
3. Load testing yap
4. Monitoring kur

**İyi kodlamalar! 🚀**
