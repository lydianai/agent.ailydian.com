#!/bin/bash

echo "🏥 Healthcare-AI-Quantum-System - Test Suite"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check${NC}"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

# Test 2: API Info
echo -e "${BLUE}Test 2: API Information${NC}"
curl -s http://localhost:8000/ | python3 -m json.tool
echo ""

# Test 3: Clinical Diagnosis - Chest Pain
echo -e "${BLUE}Test 3: Clinical Diagnosis - Chest Pain${NC}"
curl -s -X POST http://localhost:8000/api/v1/clinical-decision/diagnose \
  -H "Content-Type: application/json" \
  -d @- << 'EOF' | python3 -m json.tool
{
  "patient_id": "P-12345",
  "chief_complaint": "chest pain and shortness of breath",
  "symptoms": ["diaphoresis", "nausea"],
  "vitals": {
    "heart_rate": 105,
    "blood_pressure_systolic": 145,
    "blood_pressure_diastolic": 92,
    "oxygen_saturation": 94.0,
    "temperature": 37.1
  }
}
EOF
echo ""

# Test 4: Patient Monitoring
echo -e "${BLUE}Test 4: Patient Monitoring - High Risk${NC}"
curl -s -X POST http://localhost:8000/api/v1/patient-monitoring/assess \
  -H "Content-Type: application/json" \
  -d @- << 'EOF' | python3 -m json.tool
{
  "patient_id": "ICU-001",
  "vital_signs": {
    "heart_rate": 125,
    "blood_pressure_systolic": 85,
    "blood_pressure_diastolic": 55,
    "oxygen_saturation": 88.0,
    "temperature": 38.9,
    "respiratory_rate": 26
  }
}
EOF
echo ""

# Test 5: Agent Metrics
echo -e "${BLUE}Test 5: Agent Metrics${NC}"
curl -s http://localhost:8000/api/v1/metrics/agents | python3 -m json.tool
echo ""

echo -e "${GREEN}✅ All tests completed!${NC}"
echo ""
echo "📚 Open browser to:"
echo "  • http://localhost:8000/docs - Interactive API documentation"
echo ""
