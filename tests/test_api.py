"""
Test script for Healthcare Pipeline API endpoints.
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

import requests
import json
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
BASE_URL = "http://localhost:8002"
API_ENDPOINTS = {
    "health": "/health",
    "patients": "/patients",
    "patient": "/patients/{patient_id}",
    "vitals": "/patients/{patient_id}/vitals",
    "health_summary": "/patients/{patient_id}/health-summary",
    "alerts": "/patients/{patient_id}/alerts",
    "forecast": "/patients/{patient_id}/forecast",
    "active_patients": "/monitoring/active-patients",
    "system_stats": "/system/stats",
    "process_features": "/patients/{patient_id}/process-features"
}

def test_health_endpoint():
    """Test the health check endpoint."""
    print("🔄 Testing health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check successful")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Cannot connect to API server. Is it running?")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_patients_endpoint():
    """Test the patients endpoint."""
    print("🔄 Testing patients endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/patients")
        
        if response.status_code == 200:
            patients = response.json()
            print(f"   ✅ Patients endpoint successful")
            print(f"   Found {len(patients)} patients")
            return True
        else:
            print(f"   ❌ Patients endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_patient_detail_endpoint():
    """Test the patient detail endpoint."""
    print("🔄 Testing patient detail endpoint...")
    
    try:
        # Test with patient ID 1
        response = requests.get(f"{BASE_URL}/patients/1")
        
        if response.status_code == 200:
            patient = response.json()
            print(f"   ✅ Patient detail endpoint successful")
            print(f"   Patient: {patient.get('patient_name')}")
            return True
        elif response.status_code == 404:
            print(f"   ⚠️ Patient not found (expected for empty database)")
            return True
        else:
            print(f"   ❌ Patient detail endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_vitals_endpoint():
    """Test the vitals endpoint."""
    print("🔄 Testing vitals endpoint...")
    
    try:
        # Test with patient ID 1
        response = requests.get(f"{BASE_URL}/patients/1/vitals?hours=24")
        
        if response.status_code == 200:
            vitals = response.json()
            print(f"   ✅ Vitals endpoint successful")
            print(f"   Found {len(vitals)} vital readings")
            return True
        elif response.status_code == 404:
            print(f"   ⚠️ No vitals found (expected for empty database)")
            return True
        else:
            print(f"   ❌ Vitals endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_health_summary_endpoint():
    """Test the health summary endpoint."""
    print("🔄 Testing health summary endpoint...")
    
    try:
        # Test with patient ID 1
        response = requests.get(f"{BASE_URL}/patients/1/health-summary")
        
        if response.status_code == 200:
            summary = response.json()
            print(f"   ✅ Health summary endpoint successful")
            print(f"   Summary keys: {list(summary.keys())}")
            return True
        elif response.status_code == 404:
            print(f"   ⚠️ No health summary found (expected for empty database)")
            return True
        else:
            print(f"   ❌ Health summary endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_alerts_endpoint():
    """Test the alerts endpoint."""
    print("🔄 Testing alerts endpoint...")
    
    try:
        # Test with patient ID 1
        response = requests.get(f"{BASE_URL}/patients/1/alerts")
        
        if response.status_code == 200:
            alerts = response.json()
            print(f"   ✅ Alerts endpoint successful")
            print(f"   Found {len(alerts)} alerts")
            return True
        elif response.status_code == 404:
            print(f"   ⚠️ No alerts found (expected for empty database)")
            return True
        else:
            print(f"   ❌ Alerts endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_forecast_endpoint():
    """Test the forecast endpoint."""
    print("🔄 Testing forecast endpoint...")
    
    try:
        # Test with patient ID 1
        response = requests.get(f"{BASE_URL}/patients/1/forecast?hours=24")
        
        if response.status_code == 200:
            forecast = response.json()
            print(f"   ✅ Forecast endpoint successful")
            print(f"   Forecast hours: {forecast.get('forecast_hours')}")
            print(f"   Forecasts: {len(forecast.get('forecasts', {}))}")
            return True
        elif response.status_code == 404:
            print(f"   ⚠️ No forecast data available (expected for empty database)")
            return True
        else:
            print(f"   ❌ Forecast endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_active_patients_endpoint():
    """Test the active patients endpoint."""
    print("🔄 Testing active patients endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/monitoring/active-patients")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Active patients endpoint successful")
            print(f"   Total patients: {data.get('total_patients')}")
            print(f"   Active patients: {len(data.get('active_patients', []))}")
            return True
        else:
            print(f"   ❌ Active patients endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_system_stats_endpoint():
    """Test the system stats endpoint."""
    print("🔄 Testing system stats endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/system/stats")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ System stats endpoint successful")
            print(f"   Total patients: {stats.get('total_patients')}")
            print(f"   Recent readings: {stats.get('recent_vital_readings')}")
            return True
        else:
            print(f"   ❌ System stats endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_add_vital_sign():
    """Test adding a vital sign."""
    print("🔄 Testing add vital sign endpoint...")
    
    try:
        # Create sample vital sign data
        vital_data = {
            "heart_rate": 75.0,
            "systolic": 120.0,
            "diastolic": 80.0,
            "temperature": 37.0,
            "respiration": 16,
            "oxygen_saturation": 98.0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Test with patient ID 1
        response = requests.post(
            f"{BASE_URL}/patients/1/vitals",
            json=vital_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Add vital sign endpoint successful")
            print(f"   Added vital sign for patient 1")
            return True
        else:
            print(f"   ❌ Add vital sign endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_api_documentation():
    """Test API documentation endpoints."""
    print("🔄 Testing API documentation...")
    
    try:
        # Test OpenAPI docs
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print(f"   ✅ API documentation available at /docs")
        else:
            print(f"   ❌ API documentation not available")
            return False
        
        # Test ReDoc
        response = requests.get(f"{BASE_URL}/redoc")
        if response.status_code == 200:
            print(f"   ✅ ReDoc documentation available at /redoc")
        else:
            print(f"   ❌ ReDoc documentation not available")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def run_all_api_tests():
    """Run all API tests."""
    print("🚀 Starting Healthcare Pipeline API Tests")
    print("=" * 60)
    
    tests = [
        ("Health Endpoint", test_health_endpoint),
        ("Patients Endpoint", test_patients_endpoint),
        ("Patient Detail Endpoint", test_patient_detail_endpoint),
        ("Vitals Endpoint", test_vitals_endpoint),
        ("Health Summary Endpoint", test_health_summary_endpoint),
        ("Alerts Endpoint", test_alerts_endpoint),
        ("Forecast Endpoint", test_forecast_endpoint),
        ("Active Patients Endpoint", test_active_patients_endpoint),
        ("System Stats Endpoint", test_system_stats_endpoint),
        ("Add Vital Sign Endpoint", test_add_vital_sign),
        ("API Documentation", test_api_documentation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n=== {test_name} ===")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 API Test Results:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<30} {status}")
    
    print(f"\n   Total Tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    
    if passed == total:
        print("\n🎉 All API tests passed!")
        print("📖 API Documentation available at:")
        print(f"   - Swagger UI: {BASE_URL}/docs")
        print(f"   - ReDoc: {BASE_URL}/redoc")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
    
    return passed == total

if __name__ == "__main__":
    run_all_api_tests() 