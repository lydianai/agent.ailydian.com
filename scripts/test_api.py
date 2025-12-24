#!/usr/bin/env python3
"""
API Test Script

Tests the Clinical Decision Agent via REST API.

Usage:
    python scripts/test_api.py
"""

import asyncio
import httpx
from uuid import uuid4

API_BASE_URL = "http://localhost:8080"


async def test_health_check():
    """Test health check endpoint"""
    print("🏥 Testing health check...")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/health")

        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False

    return True


async def test_clinical_diagnosis():
    """Test clinical diagnosis endpoint"""
    print("\n🧠 Testing clinical diagnosis...")

    # Sample patient data
    request_data = {
        "patient_id": str(uuid4()),
        "chief_complaint": "chest pain and shortness of breath",
        "symptoms": [
            "chest pain",
            "shortness of breath",
            "diaphoresis",
            "nausea"
        ],
        "vitals": {
            "heart_rate": 105,
            "blood_pressure_systolic": 145,
            "blood_pressure_diastolic": 92,
            "temperature": 37.2,
            "oxygen_saturation": 94.0,
            "respiratory_rate": 22
        },
        "medical_history": [
            "hypertension",
            "type 2 diabetes",
            "hyperlipidemia",
            "family history of CAD"
        ],
        "current_medications": [
            "metformin 1000mg BID",
            "lisinopril 10mg daily",
            "atorvastatin 40mg daily"
        ],
        "labs": {
            "troponin": 0.8,
            "BNP": 450,
            "creatinine": 1.1,
            "glucose": 145,
            "WBC": 11.2
        }
    }

    print(f"   Patient ID: {request_data['patient_id']}")
    print(f"   Chief Complaint: {request_data['chief_complaint']}")

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/api/v1/clinical-decision/diagnose",
            json=request_data
        )

        if response.status_code == 200:
            result = response.json()

            print("\n✅ Diagnosis successful!")
            print(f"\n📊 Results:")
            print(f"   Decision ID: {result['decision_id']}")
            print(f"   Confidence: {result['confidence']*100:.1f}%")

            if result['primary_diagnosis']:
                print(f"\n🎯 Primary Diagnosis:")
                print(f"   {result['primary_diagnosis'].get('diagnosis')}")
                print(f"   Probability: {result['primary_diagnosis'].get('probability', 0)*100:.1f}%")

            if result['differential_diagnoses']:
                print(f"\n🔍 Differential Diagnoses:")
                for idx, dx in enumerate(result['differential_diagnoses'][:5], 1):
                    print(f"   {idx}. {dx.get('diagnosis')} ({dx.get('probability', 0)*100:.0f}%)")

            if result['recommended_tests']:
                print(f"\n🧪 Recommended Tests:")
                for test in result['recommended_tests'][:5]:
                    urgency = test.get('urgency', 'routine')
                    print(f"   - {test.get('test')} [{urgency}]")

            if result['treatment_suggestions']:
                print(f"\n💊 Treatment Suggestions:")
                for tx in result['treatment_suggestions'][:5]:
                    print(f"   - {tx.get('treatment')}")

            if result['drug_warnings']:
                print(f"\n⚠️  Drug Warnings:")
                for warning in result['drug_warnings']:
                    print(f"   - {warning.get('description')}")

            if result['urgent_flags']:
                print(f"\n🚨 URGENT FLAGS:")
                for flag in result['urgent_flags']:
                    print(f"   ⚡ {flag}")

            if result['requires_human_review']:
                print(f"\n👨‍⚕️ REQUIRES HUMAN REVIEW")

            print(f"\n📝 Explanation:")
            if result['explanation']:
                print(f"   {result['explanation'][:200]}...")

        else:
            print(f"❌ Diagnosis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False

    return True


async def test_metrics():
    """Test metrics endpoint"""
    print("\n📊 Testing metrics...")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/v1/clinical-decision/metrics")

        if response.status_code == 200:
            metrics = response.json()
            print("✅ Metrics retrieved")
            print(f"   Total Decisions: {metrics.get('total_decisions', 0)}")
            print(f"   Successful: {metrics.get('successful_decisions', 0)}")
            print(f"   Failed: {metrics.get('failed_decisions', 0)}")
            print(f"   Avg Confidence: {metrics.get('avg_confidence', 0):.2%}")
            print(f"   Avg Time: {metrics.get('avg_decision_time_ms', 0):.0f}ms")
        else:
            print(f"❌ Metrics failed: {response.status_code}")
            return False

    return True


async def main():
    """Run all tests"""
    print("="*60)
    print("🚀 Healthcare-AI-Quantum-System API Tests")
    print("="*60)

    all_passed = True

    # Test 1: Health check
    if not await test_health_check():
        all_passed = False

    # Test 2: Clinical diagnosis (requires LLM API key)
    if not await test_clinical_diagnosis():
        all_passed = False

    # Test 3: Metrics
    if not await test_metrics():
        all_passed = False

    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
