"""
Simple test for InfluxDB query syntax.
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from src.data_ingestion.sensor_data_collector import create_influx_connection
from datetime import datetime, timedelta

def test_simple_query():
    """Test a simple InfluxDB query."""
    print("🔄 Testing simple InfluxDB query...")
    
    try:
        client, bucket = create_influx_connection()
        query_api = client.query_api()
        
        # Simple query
        query = f'''
        from(bucket: "{bucket}")
            |> range(start: -1h)
            |> filter(fn: (r) => r["_measurement"] == "health_vitals")
            |> limit(n: 5)
        '''
        
        print(f"   Query: {query}")
        result = query_api.query(query)
        
        print(f"   ✅ Query successful")
        print(f"   Tables returned: {len(list(result))}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Query failed: {e}")
        return False

if __name__ == "__main__":
    test_simple_query() 