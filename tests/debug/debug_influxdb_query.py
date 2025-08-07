"""
Debug InfluxDB query to understand the data structure.
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from src.data_ingestion.sensor_data_collector import create_influx_connection, SensorDataCollector
from datetime import datetime, timedelta

def generate_test_data():
    """Generate some test data in InfluxDB."""
    print("🔄 Generating test data in InfluxDB...")
    
    try:
        collector = SensorDataCollector()
        
        # Generate data for patient 1
        sensor_data = collector.simulate_sensor_data(patient_id=1, duration_minutes=5)
        print(f"   Generated {len(sensor_data)} sensor measurements")
        
        # Process and write to InfluxDB
        processed_data = collector.process_sensor_batch(sensor_data)
        print(f"   Processed {len(processed_data)} valid measurements")
        
        # Write to InfluxDB
        collector.write_to_influxdb(processed_data)
        print("   ✅ Test data written to InfluxDB")
        
        return True
    except Exception as e:
        print(f"   ❌ Error generating test data: {e}")
        return False

def debug_influxdb_data():
    """Debug InfluxDB data structure."""
    print("🔄 Debugging InfluxDB data structure...")
    
    try:
        client, bucket = create_influx_connection()
        query_api = client.query_api()
        
        # Query 1: Get all data from last 24 hours
        print("\n=== Query 1: All data from last 24 hours ===")
        query1 = f'''
        from(bucket: "{bucket}")
            |> range(start: -24h)
            |> limit(n: 10)
        '''
        
        result1 = query_api.query(query1)
        print(f"   Tables returned: {len(list(result1))}")
        
        for i, table in enumerate(result1):
            print(f"   Table {i}:")
            for j, record in enumerate(table.records):
                if j < 3:  # Show first 3 records
                    print(f"     Record {j}: {record}")
        
        # Query 2: Get measurements
        print("\n=== Query 2: Available measurements ===")
        query2 = f'''
        from(bucket: "{bucket}")
            |> range(start: -24h)
            |> group(columns: ["_measurement"])
            |> distinct(column: "_measurement")
        '''
        
        result2 = query_api.query(query2)
        print(f"   Measurements: {len(list(result2))}")
        for table in result2:
            for record in table.records:
                print(f"     Measurement: {record.get_value()}")
        
        # Query 3: Get fields
        print("\n=== Query 3: Available fields ===")
        query3 = f'''
        from(bucket: "{bucket}")
            |> range(start: -24h)
            |> group(columns: ["_field"])
            |> distinct(column: "_field")
        '''
        
        result3 = query_api.query(query3)
        print(f"   Fields: {len(list(result3))}")
        for table in result3:
            for record in table.records:
                print(f"     Field: {record.get_value()}")
        
        # Query 4: Get tags
        print("\n=== Query 4: Available tags ===")
        query4 = f'''
        from(bucket: "{bucket}")
            |> range(start: -24h)
            |> keys()
            |> filter(fn: (r) => r["_value"] =~ /^_/)
        '''
        
        result4 = query_api.query(query4)
        print(f"   Tags: {len(list(result4))}")
        for table in result4:
            for record in table.records:
                print(f"     Tag: {record.get_value()}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    # First generate some test data
    generate_test_data()
    
    # Then debug the data structure
    debug_influxdb_data() 