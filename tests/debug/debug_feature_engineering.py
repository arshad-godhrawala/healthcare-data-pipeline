"""
Debug script for Feature Engineering functions
Tests individual components to identify issues.
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from src.data_processing.feature_engineer import (
    calculate_health_metrics,
    create_time_based_features,
    generate_health_scores
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_simple_test_data():
    """Create simple test data."""
    data = [
        {
            'timestamp': datetime.now() - timedelta(hours=i),
            'heart_rate': 75 + np.random.normal(0, 5),
            'temperature': 37.0 + np.random.normal(0, 0.5),
            'systolic': 120 + np.random.normal(0, 10),
            'diastolic': 80 + np.random.normal(0, 5),
            'respiration': 16 + np.random.normal(0, 2),
            'oxygen_saturation': 98 + np.random.normal(0, 1)
        }
        for i in range(10)
    ]
    return pd.DataFrame(data)

def test_health_metrics_simple():
    """Test health metrics with simple data."""
    print("🔄 Testing health metrics with simple data...")
    
    try:
        df = create_simple_test_data()
        print(f"   Input data shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        
        df_metrics = calculate_health_metrics(df)
        print(f"   Output data shape: {df_metrics.shape}")
        print(f"   New columns: {list(set(df_metrics.columns) - set(df.columns))}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_time_features_simple():
    """Test time features with simple data."""
    print("🔄 Testing time features with simple data...")
    
    try:
        df = create_simple_test_data()
        print(f"   Input data shape: {df.shape}")
        
        df_time = create_time_based_features(df)
        print(f"   Output data shape: {df_time.shape}")
        print(f"   New columns: {list(set(df_time.columns) - set(df.columns))}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_health_scores_simple():
    """Test health scores with simple data."""
    print("🔄 Testing health scores with simple data...")
    
    try:
        df = create_simple_test_data()
        df_metrics = calculate_health_metrics(df)
        print(f"   Metrics data shape: {df_metrics.shape}")
        
        df_scores = generate_health_scores(df_metrics)
        print(f"   Scores data shape: {df_scores.shape}")
        print(f"   New columns: {list(set(df_scores.columns) - set(df_metrics.columns))}")
        
        # Check if composite score exists
        if 'composite_health_score' in df_scores.columns:
            print(f"   Composite score range: {df_scores['composite_health_score'].min():.1f} - {df_scores['composite_health_score'].max():.1f}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_influxdb_connection():
    """Test InfluxDB connection and query."""
    print("🔄 Testing InfluxDB connection...")
    
    try:
        from src.data_ingestion.sensor_data_collector import create_influx_connection
        
        client, bucket = create_influx_connection()
        query_api = client.query_api()
        
        # Simple query to test connection
        query = f'''
        from(bucket: "{bucket}")
            |> range(start: -1h)
            |> limit(n: 5)
        '''
        
        result = query_api.query(query)
        print(f"   ✅ InfluxDB connection successful")
        print(f"   Query returned {len(list(result))} tables")
        
        client.close()
        return True
    except Exception as e:
        print(f"   ❌ InfluxDB connection error: {e}")
        return False

def test_postgres_connection():
    """Test PostgreSQL connection."""
    print("🔄 Testing PostgreSQL connection...")
    
    try:
        from src.database.postgres_operations import create_postgres_connection
        from src.database.models import Patient
        
        engine, SessionLocal = create_postgres_connection()
        
        with SessionLocal() as session:
            # Try to query a patient
            patient = session.query(Patient).first()
            if patient:
                print(f"   ✅ PostgreSQL connection successful")
                print(f"   Found patient: {patient.patient_name}")
            else:
                print(f"   ⚠️ PostgreSQL connected but no patients found")
        
        return True
    except Exception as e:
        print(f"   ❌ PostgreSQL connection error: {e}")
        return False

def run_debug_tests():
    """Run debug tests."""
    print("🚀 Starting Debug Tests")
    print("=" * 50)
    
    tests = [
        ("Health Metrics (Simple)", test_health_metrics_simple),
        ("Time Features (Simple)", test_time_features_simple),
        ("Health Scores (Simple)", test_health_scores_simple),
        ("InfluxDB Connection", test_influxdb_connection),
        ("PostgreSQL Connection", test_postgres_connection)
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
    print("\n" + "=" * 50)
    print("📊 Debug Results:")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<25} {status}")
    
    print(f"\n   Total Tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    
    return passed == total

if __name__ == "__main__":
    run_debug_tests() 