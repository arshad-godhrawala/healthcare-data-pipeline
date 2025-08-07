import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import asyncio
import time
from datetime import datetime, timedelta
from src.data_ingestion.sensor_data_collector import SensorDataCollector

def test_single_patient_simulation():
    """Test single patient sensor data simulation"""
    print("=== Testing Single Patient Sensor Simulation ===")
    
    try:
        # Create sensor collector
        collector = SensorDataCollector()
        
        # Test single patient simulation (2 minutes)
        print("🔄 Simulating sensor data for patient 1...")
        start_time = time.time()
        
        # Run async simulation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        measurements = loop.run_until_complete(
            collector.simulate_sensor_data(patient_id=1, duration_minutes=2)
        )
        
        simulation_time = time.time() - start_time
        print(f"✅ Simulation completed in {simulation_time:.2f} seconds")
        print(f"   Generated {len(measurements)} measurements")
        
        # Show sample measurements (without PHI)
        if measurements:
            print("   Sample measurement structure:")
            sample = measurements[0]
            for key, value in sample.items():
                if key != 'patient_id':  # Don't show patient ID in logs
                    print(f"     {key}: {value}")
        
        # Test batch processing
        print("\n🔄 Processing sensor data batch...")
        processed_data = collector.process_sensor_batch(measurements)
        print(f"✅ Processed {len(processed_data)} valid measurements")
        
        # Test InfluxDB write
        print("\n🔄 Writing to InfluxDB...")
        written_count = collector.write_to_influxdb(processed_data)
        print(f"✅ Successfully wrote {written_count} measurements to InfluxDB")
        
        # Test querying the data back
        print("\n🔄 Querying data from InfluxDB...")
        queried_data = collector.query_patient_vitals(patient_id=1, hours=1)
        print(f"✅ Retrieved {len(queried_data)} records from InfluxDB")
        
        if queried_data:
            print("   Sample queried data:")
            sample_query = queried_data[0]
            for key, value in sample_query.items():
                print(f"     {key}: {value}")
        
        loop.close()
        return True
        
    except Exception as e:
        print(f"❌ Single patient simulation failed: {str(e)}")
        return False

def test_multiple_patients():
    """Test sensor simulation for multiple patients"""
    print("\n=== Testing Multiple Patients Simulation ===")
    
    try:
        collector = SensorDataCollector()
        patient_ids = [1, 2, 3]
        
        print(f"🔄 Simulating data for {len(patient_ids)} patients...")
        
        # Run async simulation for multiple patients
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        all_measurements = []
        for patient_id in patient_ids:
            measurements = loop.run_until_complete(
                collector.simulate_sensor_data(patient_id=patient_id, duration_minutes=1)
            )
            all_measurements.extend(measurements)
            print(f"   Patient {patient_id}: {len(measurements)} measurements")
        
        print(f"✅ Total measurements generated: {len(all_measurements)}")
        
        # Process and write all measurements
        processed_data = collector.process_sensor_batch(all_measurements)
        written_count = collector.write_to_influxdb(processed_data)
        print(f"✅ Wrote {written_count} measurements to InfluxDB")
        
        loop.close()
        return True
        
    except Exception as e:
        print(f"❌ Multiple patients simulation failed: {str(e)}")
        return False

async def test_continuous_simulation():
    """Test continuous simulation (runs for 30 seconds)"""
    print("\n=== Testing Continuous Simulation ===")
    print("🔄 Running continuous simulation for 30 seconds...")
    print("   (Press Ctrl+C to stop early)")
    
    try:
        collector = SensorDataCollector()
        patient_ids = [1, 2]
        
        # Run continuous simulation for 30 seconds
        start_time = time.time()
        
        # Create task for continuous simulation
        simulation_task = asyncio.create_task(
            collector.run_continuous_simulation(patient_ids, interval_seconds=10)
        )
        
        # Wait for 30 seconds or until interrupted
        try:
            await asyncio.wait_for(simulation_task, timeout=30)
        except asyncio.TimeoutError:
            print("⏰ 30 seconds elapsed, stopping simulation")
        except KeyboardInterrupt:
            print("\n⏹️  Simulation stopped by user")
        
        simulation_time = time.time() - start_time
        print(f"✅ Continuous simulation completed in {simulation_time:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Continuous simulation failed: {str(e)}")
        return False

def test_data_validation():
    """Test sensor data validation with various scenarios"""
    print("\n=== Testing Data Validation ===")
    
    try:
        collector = SensorDataCollector()
        
        # Test data with some invalid values
        test_data = [
            {
                'patient_id': 1,
                'timestamp': datetime.now(),
                'heart_rate': 75,  # Valid
                'blood_pressure': '120/80',  # Valid
                'temperature': 37.0,  # Valid
                'respiration': 16  # Valid
            },
            {
                'patient_id': 1,
                'timestamp': datetime.now(),
                'heart_rate': 400,  # Invalid (too high)
                'blood_pressure': '80/120',  # Invalid (diastolic > systolic)
                'temperature': 50.0,  # Invalid (too high)
                'respiration': 150  # Invalid (too high)
            },
            {
                'patient_id': 1,
                'timestamp': datetime.now(),
                'heart_rate': 65,  # Valid
                'blood_pressure': '110/70',  # Valid
                'temperature': 36.5,  # Valid
                'respiration': 14  # Valid
            }
        ]
        
        print(f"🔄 Testing validation with {len(test_data)} records (including invalid data)...")
        processed_data = collector.process_sensor_batch(test_data)
        print(f"✅ Validation completed. {len(processed_data)} valid records retained")
        
        return True
        
    except Exception as e:
        print(f"❌ Data validation test failed: {str(e)}")
        return False

def test_influxdb_connection():
    """Test InfluxDB connection and basic operations"""
    print("\n=== Testing InfluxDB Connection ===")
    
    try:
        collector = SensorDataCollector()
        
        # Test basic connection by querying buckets
        print("🔄 Testing InfluxDB connection...")
        
        # Try to write a simple test point
        from influxdb_client import Point
        test_point = Point("test_measurement") \
            .tag("test_tag", "test_value") \
            .field("test_field", 123) \
            .time(datetime.now())
        
        collector.write_api.write(bucket=collector.bucket, record=[test_point])
        print("✅ Successfully wrote test point to InfluxDB")
        
        # Try to query the test point
        query = f'''
        from(bucket: "{collector.bucket}")
            |> range(start: -1h)
            |> filter(fn: (r) => r["_measurement"] == "test_measurement")
        '''
        
        result = collector.query_api.query(query)
        record_count = sum(len(table.records) for table in result)
        print(f"✅ Successfully queried {record_count} test records from InfluxDB")
        
        return True
        
    except Exception as e:
        print(f"❌ InfluxDB connection test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all sensor collector tests"""
    print("🚀 Starting Sensor Data Collector Tests")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: InfluxDB Connection
    test_results.append(("InfluxDB Connection", test_influxdb_connection()))
    
    # Test 2: Single Patient Simulation
    test_results.append(("Single Patient Simulation", test_single_patient_simulation()))
    
    # Test 3: Multiple Patients
    test_results.append(("Multiple Patients", test_multiple_patients()))
    
    # Test 4: Data Validation
    test_results.append(("Data Validation", test_data_validation()))
    
    # Test 5: Continuous Simulation (async)
    print("\n🔄 Running continuous simulation test...")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        continuous_result = loop.run_until_complete(test_continuous_simulation())
        loop.close()
        test_results.append(("Continuous Simulation", continuous_result))
    except Exception as e:
        print(f"❌ Continuous simulation test failed: {str(e)}")
        test_results.append(("Continuous Simulation", False))
    
    # Print results summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<25} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"   Total Tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    
    if passed == total:
        print("\n🎉 All tests passed! Sensor data collector is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 