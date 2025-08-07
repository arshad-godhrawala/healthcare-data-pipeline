#!/usr/bin/env python3
"""
Comprehensive system test for Healthcare Data Pipeline
"""
import sys
import os
import requests
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_database_connections():
    """Test database connections"""
    print("🔍 Testing Database Connections...")
    
    try:
        from src.database.postgres_operations import create_postgres_connection
        engine, SessionLocal = create_postgres_connection()
        print("✅ PostgreSQL connection successful")
        
        # Test table creation
        from src.database.models import Base
        Base.metadata.create_all(engine)
        print("✅ PostgreSQL tables created/verified")
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False
    
    try:
        from src.database.influx_operations import create_influx_connection
        client, bucket = create_influx_connection()
        print("✅ InfluxDB connection successful")
        
    except Exception as e:
        print(f"❌ InfluxDB connection failed: {e}")
        return False
    
    return True

def test_data_ingestion():
    """Test data ingestion components"""
    print("\n🔍 Testing Data Ingestion...")
    
    try:
        from src.data_ingestion.patient_data_loader import get_patient_count
        count = get_patient_count()
        print(f"✅ Patient data loader working - {count} patients found")
        
    except Exception as e:
        print(f"❌ Patient data loader failed: {e}")
        return False
    
    try:
        from src.data_ingestion.sensor_data_collector import SensorDataCollector
        collector = SensorDataCollector()
        vitals = collector.query_patient_vitals(1, 1)  # Get 1 hour of data for patient 1
        print(f"✅ Sensor data collector working - {len(vitals)} vital records found")
        
    except Exception as e:
        print(f"❌ Sensor data collector failed: {e}")
        return False
    
    return True

def test_data_processing():
    """Test data processing components"""
    print("\n🔍 Testing Data Processing...")
    
    try:
        from src.data_processing.aggregator import get_patient_summary_stats
        stats = get_patient_summary_stats(1)
        print("✅ Data aggregation working")
        
    except Exception as e:
        print(f"❌ Data aggregation failed: {e}")
        return False
    
    try:
        from src.data_processing.feature_engineer import process_patient_features
        features = process_patient_features(1)
        print("✅ Feature engineering working")
        
    except Exception as e:
        print(f"❌ Feature engineering failed: {e}")
        return False
    
    return True

def test_forecasting():
    """Test forecasting components"""
    print("\n🔍 Testing Forecasting...")
    
    try:
        from src.forecasting.health_forecaster import HealthForecaster
        forecaster = HealthForecaster()
        print("✅ Health forecaster initialized")
        
    except Exception as e:
        print(f"❌ Health forecaster failed: {e}")
        return False
    
    return True

def test_api():
    """Test API endpoints"""
    print("\n🔍 Testing API...")
    
    # Start API server in background
    import subprocess
    import threading
    
    def start_api():
        subprocess.run([sys.executable, "run_api.py"], capture_output=True)
    
    # Start API in background
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Wait for API to start
    print("⏳ Starting API server...")
    time.sleep(5)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ API health endpoint working")
        else:
            print(f"❌ API health endpoint failed: {response.status_code}")
            return False
        
        # Test patients endpoint
        response = requests.get("http://localhost:8000/patients", timeout=10)
        if response.status_code == 200:
            print("✅ API patients endpoint working")
        else:
            print(f"❌ API patients endpoint failed: {response.status_code}")
            return False
        
        # Test vitals endpoint
        response = requests.get("http://localhost:8000/vitals", timeout=10)
        if response.status_code == 200:
            print("✅ API vitals endpoint working")
        else:
            print(f"❌ API vitals endpoint failed: {response.status_code}")
            return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API test failed: {e}")
        return False
    
    return True

def test_dashboard():
    """Test dashboard"""
    print("\n🔍 Testing Dashboard...")
    
    try:
        # Check if frontend files exist
        frontend_dir = Path(__file__).parent / "frontend"
        if not frontend_dir.exists():
            print("❌ Frontend directory not found")
            return False
        
        index_file = frontend_dir / "index.html"
        if not index_file.exists():
            print("❌ index.html not found")
            return False
        
        print("✅ Frontend files found")
        
        # Test dashboard server
        import subprocess
        import threading
        
        def start_dashboard():
            subprocess.run([sys.executable, "run_dashboard.py"], capture_output=True)
        
        dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
        dashboard_thread.start()
        
        print("⏳ Starting dashboard server...")
        time.sleep(3)
        
        # Test dashboard endpoint
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard server working")
        else:
            print(f"❌ Dashboard server failed: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False
    
    return True

def main():
    """Run all system tests"""
    print("🚀 Starting Healthcare Data Pipeline System Test")
    print("=" * 50)
    
    tests = [
        ("Database Connections", test_database_connections),
        ("Data Ingestion", test_data_ingestion),
        ("Data Processing", test_data_processing),
        ("Forecasting", test_forecasting),
        ("API", test_api),
        ("Dashboard", test_dashboard)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working properly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main() 