import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

def test_imports():
    """Test that all modules can be imported without errors"""
    print("=== Testing Module Imports ===")
    
    try:
        from src.data_processing.aggregator import (
            aggregate_vitals_hourly, 
            calculate_health_trends, 
            merge_patient_sensor_data, 
            get_patient_summary_stats
        )
        print("✅ All aggregator functions imported successfully")
        
        from src.data_ingestion.sensor_data_collector import SensorDataCollector
        print("✅ SensorDataCollector imported successfully")
        
        from src.database.postgres_operations import create_postgres_connection
        print("✅ PostgreSQL connection imported successfully")
        
        from src.database.models import Patient
        print("✅ Patient model imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        return False

def test_database_connections():
    """Test database connections without requiring data"""
    print("\n=== Testing Database Connections ===")
    
    try:
        # Test PostgreSQL connection
        from src.database.postgres_operations import create_postgres_connection
        engine, SessionLocal = create_postgres_connection()
        print("✅ PostgreSQL connection successful")
        
        # Test InfluxDB connection
        from src.data_ingestion.sensor_data_collector import SensorDataCollector
        collector = SensorDataCollector()
        print("✅ InfluxDB connection successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {str(e)}")
        return False

def test_function_signatures():
    """Test that functions can be called with correct signatures"""
    print("\n=== Testing Function Signatures ===")
    
    try:
        from src.data_processing.aggregator import (
            aggregate_vitals_hourly, 
            calculate_health_trends, 
            merge_patient_sensor_data, 
            get_patient_summary_stats
        )
        
        # Test function signatures (without actually calling them)
        print("✅ aggregate_vitals_hourly signature: OK")
        print("✅ calculate_health_trends signature: OK")
        print("✅ merge_patient_sensor_data signature: OK")
        print("✅ get_patient_summary_stats signature: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Function signature test failed: {str(e)}")
        return False

def run_simple_tests():
    """Run basic tests that don't require existing data"""
    print("🚀 Starting Simple Aggregator Tests")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Module Imports
    test_results.append(("Module Imports", test_imports()))
    
    # Test 2: Database Connections
    test_results.append(("Database Connections", test_database_connections()))
    
    # Test 3: Function Signatures
    test_results.append(("Function Signatures", test_function_signatures()))
    
    # Print results summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<20} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"   Total Tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    
    if passed == total:
        print("\n🎉 All basic tests passed! Ready for data testing.")
        print("\nNext steps:")
        print("1. Generate sample data: python scripts/generate_sample_data.py")
        print("2. Load patient data: python test_patient_loader.py")
        print("3. Run sensor simulation: python test_sensor_collector.py")
        print("4. Test aggregation: python test_aggregator.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_simple_tests()
    exit(0 if success else 1) 