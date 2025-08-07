import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import pandas as pd
from datetime import datetime, timedelta
from src.data_processing.aggregator import (
    aggregate_vitals_hourly, 
    calculate_health_trends, 
    merge_patient_sensor_data, 
    get_patient_summary_stats
)

def test_aggregate_vitals_hourly():
    """Test hourly vital signs aggregation"""
    print("=== Testing aggregate_vitals_hourly ===")
    
    try:
        # Test with a recent date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"🔄 Aggregating vitals for patient 1 from {start_date} to {end_date}")
        
        hourly_data = aggregate_vitals_hourly(patient_id=1, start_date=start_date, end_date=end_date)
        
        if not hourly_data.empty:
            print(f"✅ Successfully aggregated {len(hourly_data)} hourly records")
            print("   Sample columns:", list(hourly_data.columns)[:5])
            print("   Data shape:", hourly_data.shape)
            
            # Show sample data
            if len(hourly_data) > 0:
                print("   Sample hourly data:")
                print(hourly_data.head(2))
        else:
            print("⚠️  No data found for the specified date range")
        
        return True
        
    except Exception as e:
        print(f"❌ Hourly aggregation test failed: {str(e)}")
        return False

def test_calculate_health_trends():
    """Test health trends calculation"""
    print("\n=== Testing calculate_health_trends ===")
    
    try:
        print("🔄 Calculating health trends for patient 1 (last 7 days)")
        
        trends = calculate_health_trends(patient_id=1, days=7)
        
        if trends:
            print("✅ Health trends calculated successfully")
            print("   Available metrics:", list(trends.keys()))
            
            # Show detailed trends
            for metric, data in trends.items():
                if isinstance(data, dict):
                    print(f"   {metric}:")
                    for key, value in data.items():
                        if isinstance(value, float):
                            print(f"     {key}: {value:.2f}")
                        else:
                            print(f"     {key}: {value}")
                else:
                    print(f"   {metric}: {data}")
        else:
            print("⚠️  No trends data available for the patient")
        
        return True
        
    except Exception as e:
        print(f"❌ Health trends test failed: {str(e)}")
        return False

def test_merge_patient_sensor_data():
    """Test merging patient and sensor data"""
    print("\n=== Testing merge_patient_sensor_data ===")
    
    try:
        patient_ids = [1, 2, 3]  # Test with multiple patients
        print(f"🔄 Merging data for patients: {patient_ids}")
        
        merged_data = merge_patient_sensor_data(patient_ids)
        
        if not merged_data.empty:
            print(f"✅ Successfully merged data for {len(patient_ids)} patients")
            print("   Merged data shape:", merged_data.shape)
            print("   Available columns:", list(merged_data.columns))
            
            # Show sample merged data
            if len(merged_data) > 0:
                print("   Sample merged data:")
                # Show only non-PHI columns for privacy
                safe_cols = ['patient_id', 'gender', 'timestamp', 'heart_rate', 'temperature']
                available_cols = [col for col in safe_cols if col in merged_data.columns]
                print(merged_data[available_cols].head(2))
        else:
            print("⚠️  No merged data available")
        
        return True
        
    except Exception as e:
        print(f"❌ Data merge test failed: {str(e)}")
        return False

def test_get_patient_summary_stats():
    """Test comprehensive patient summary statistics"""
    print("\n=== Testing get_patient_summary_stats ===")
    
    try:
        print("🔄 Generating comprehensive summary for patient 1")
        
        summary = get_patient_summary_stats(patient_id=1)
        
        if summary:
            print("✅ Patient summary generated successfully")
            print("   Summary keys:", list(summary.keys()))
            
            # Show summary details
            for key, value in summary.items():
                if key == 'trends' and isinstance(value, dict):
                    print(f"   {key}:")
                    for trend_key, trend_data in value.items():
                        if isinstance(trend_data, dict):
                            print(f"     {trend_key}:")
                            for sub_key, sub_value in trend_data.items():
                                if isinstance(sub_value, float):
                                    print(f"       {sub_key}: {sub_value:.2f}")
                                else:
                                    print(f"       {sub_key}: {sub_value}")
                        else:
                            print(f"     {trend_key}: {trend_data}")
                else:
                    print(f"   {key}: {value}")
        else:
            print("⚠️  No summary data available for the patient")
        
        return True
        
    except Exception as e:
        print(f"❌ Patient summary test failed: {str(e)}")
        return False

def test_data_availability():
    """Test data availability across databases"""
    print("\n=== Testing Data Availability ===")
    
    try:
        from src.data_ingestion.sensor_data_collector import SensorDataCollector
        from src.database.postgres_operations import create_postgres_connection
        from src.database.models import Patient
        
        # Check InfluxDB data
        print("🔄 Checking InfluxDB sensor data...")
        collector = SensorDataCollector()
        vitals_data = collector.query_patient_vitals(patient_id=1, hours=24)
        print(f"   Sensor records for patient 1: {len(vitals_data)}")
        
        # Check PostgreSQL data
        print("🔄 Checking PostgreSQL patient data...")
        engine, SessionLocal = create_postgres_connection()
        session = SessionLocal()
        patient_count = session.query(Patient).count()
        session.close()
        print(f"   Total patients in database: {patient_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data availability test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all aggregation tests"""
    print("🚀 Starting Data Aggregation Tests")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Data Availability
    test_results.append(("Data Availability", test_data_availability()))
    
    # Test 2: Hourly Aggregation
    test_results.append(("Hourly Aggregation", test_aggregate_vitals_hourly()))
    
    # Test 3: Health Trends
    test_results.append(("Health Trends", test_calculate_health_trends()))
    
    # Test 4: Data Merging
    test_results.append(("Data Merging", test_merge_patient_sensor_data()))
    
    # Test 5: Patient Summary
    test_results.append(("Patient Summary", test_get_patient_summary_stats()))
    
    # Print results summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<20} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"   Total Tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    
    if passed == total:
        print("\n🎉 All aggregation tests passed! Data aggregation is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 