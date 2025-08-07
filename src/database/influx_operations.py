from influxdb_client import InfluxDBClient
from influxdb_client.client.bucket_api import BucketsApi
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

def create_influx_connection():
    """
    Creates and returns an InfluxDB client connection.
    Reads credentials from environment variables.
    """
    URL = os.getenv('INFLUXDB_URL', 'http://localhost:8086')
    TOKEN = os.getenv('INFLUXDB_TOKEN')
    ORG = os.getenv('INFLUXDB_ORG')
    BUCKET = os.getenv('INFLUXDB_BUCKET')
    
    if not all([TOKEN, ORG, BUCKET]):
        raise ValueError("Missing required InfluxDB environment variables: INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET")
    
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    return client, BUCKET

def test_influx_connection():
    """
    Test the InfluxDB connection and print connection details.
    """
    try:
        client, BUCKET = create_influx_connection()
        
        # Test the connection by querying buckets
        query_api = client.query_api()
        buckets = BucketsApi(client).find_buckets().buckets
        
        print("✅ InfluxDB connection successful!")
        print(f"   URL: {client.url}")
        print(f"   Organization: {client.org}")
        print(f"   Bucket: {BUCKET}")
        print(f"   Available buckets: {[b.name for b in buckets]}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ InfluxDB connection failed: {e}")
        return False

if __name__ == "__main__":
    test_influx_connection()
