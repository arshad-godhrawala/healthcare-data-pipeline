"""
Test script for Healthcare Dashboard functionality.
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

# Configuration
API_BASE_URL = "http://localhost:8002"
DASHBOARD_URL = "http://localhost:3000"  # Changed from 8080 to 3000

def test_api_connectivity():
    """Test API connectivity."""
    print("🔄 Testing API connectivity...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API is accessible")
            return True
        else:
            print(f"   ❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API server")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_dashboard_connectivity():
    """Test dashboard connectivity."""
    print("🔄 Testing dashboard connectivity...")
    
    try:
        response = requests.get(f"{DASHBOARD_URL}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Dashboard is accessible")
            return True
        else:
            print(f"   ❌ Dashboard returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to dashboard server")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_dashboard_files():
    """Test if dashboard files exist."""
    print("🔄 Testing dashboard files...")
    
    required_files = [
        "frontend/index.html",
        "frontend/styles.css", 
        "frontend/dashboard.js"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"   ❌ Missing files: {missing_files}")
        return False
    else:
        print("   ✅ All dashboard files exist")
        return True

def test_api_endpoints():
    """Test key API endpoints used by dashboard."""
    print("🔄 Testing API endpoints...")
    
    endpoints = [
        ("/health", "Health Check"),
        ("/patients", "Patients List"),
        ("/system/stats", "System Stats"),
        ("/monitoring/active-patients", "Active Patients")
    ]
    
    results = []
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {name} endpoint working")
                results.append(True)
            else:
                print(f"   ❌ {name} endpoint failed: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"   ❌ {name} endpoint error: {e}")
            results.append(False)
    
    return all(results)

def test_dashboard_functionality():
    """Test dashboard JavaScript functionality."""
    print("🔄 Testing dashboard functionality...")
    
    # Test if dashboard.js contains required functions
    try:
        with open("frontend/dashboard.js", "r") as f:
            js_content = f.read()
        
        required_functions = [
            "loadDashboardStats",
            "loadPatients", 
            "selectPatient",
            "loadPatientVitals",
            "displayAlerts"
        ]
        
        missing_functions = []
        for func in required_functions:
            if func not in js_content:
                missing_functions.append(func)
        
        if missing_functions:
            print(f"   ❌ Missing functions: {missing_functions}")
            return False
        else:
            print("   ✅ All required JavaScript functions present")
            return True
            
    except Exception as e:
        print(f"   ❌ Error reading dashboard.js: {e}")
        return False

def test_cors_headers():
    """Test CORS headers for API access."""
    print("🔄 Testing CORS headers...")
    
    try:
        response = requests.options(f"{API_BASE_URL}/health", timeout=5)
        cors_headers = response.headers.get('Access-Control-Allow-Origin')
        
        if cors_headers:
            print("   ✅ CORS headers present")
            return True
        else:
            print("   ⚠️ CORS headers not found (may cause issues)")
            return True  # Not critical for basic functionality
    except Exception as e:
        print(f"   ❌ Error testing CORS: {e}")
        return False

def test_sample_data():
    """Test with sample data."""
    print("🔄 Testing with sample data...")
    
    try:
        # Add a sample patient
        patient_data = {
            "patient_name": "Test Patient",
            "date_of_birth": "1990-01-01",
            "gender": "Male",
            "address": "Test Address"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/patients",
            json=patient_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            print("   ✅ Sample patient created successfully")
            
            # Add sample vital sign
            vital_data = {
                "heart_rate": 75.0,
                "systolic": 120.0,
                "diastolic": 80.0,
                "temperature": 37.0,
                "respiration": 16,
                "oxygen_saturation": 98.0,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{API_BASE_URL}/patients/1/vitals",
                json=vital_data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                print("   ✅ Sample vital sign added successfully")
                return True
            else:
                print(f"   ❌ Failed to add vital sign: {response.status_code}")
                return False
        else:
            print(f"   ❌ Failed to create patient: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing sample data: {e}")
        return False

def run_dashboard_tests():
    """Run all dashboard tests."""
    print("🚀 Starting Healthcare Dashboard Tests")
    print("=" * 60)
    
    tests = [
        ("Dashboard Files", test_dashboard_files),
        ("API Connectivity", test_api_connectivity),
        ("Dashboard Connectivity", test_dashboard_connectivity),
        ("API Endpoints", test_api_endpoints),
        ("Dashboard Functionality", test_dashboard_functionality),
        ("CORS Headers", test_cors_headers),
        ("Sample Data", test_sample_data)
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
    print("📊 Dashboard Test Results:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<25} {status}")
    
    print(f"\n   Total Tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    
    if passed == total:
        print("\n🎉 All dashboard tests passed!")
        print("📊 Dashboard is ready to use!")
        print(f"   - Dashboard URL: {DASHBOARD_URL}")
        print(f"   - API URL: {API_BASE_URL}")
        print(f"   - API Docs: {API_BASE_URL}/docs")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        print("Please check the errors above and fix them.")
    
    return passed == total

if __name__ == "__main__":
    run_dashboard_tests() 