"""
Test script for Time Series Forecasting functionality.
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

from src.forecasting.health_forecaster import create_health_forecaster

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_forecaster_initialization():
    """Test forecaster initialization."""
    print("🔄 Testing forecaster initialization...")
    
    try:
        forecaster = create_health_forecaster()
        print("   ✅ Forecaster initialized successfully")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_data_preparation():
    """Test data preparation for Prophet."""
    print("🔄 Testing data preparation for Prophet...")
    
    try:
        forecaster = create_health_forecaster()
        
        # Create sample data
        dates = pd.date_range(start='2025-01-01', end='2025-01-07', freq='H')
        data = pd.DataFrame({
            'timestamp': dates,
            'heart_rate': 70 + 10 * np.sin(np.arange(len(dates)) * 0.1) + np.random.normal(0, 5, len(dates))
        })
        
        # Test data preparation
        prophet_data = forecaster.prepare_data_for_prophet(data, 'heart_rate')
        
        print(f"   ✅ Data preparation successful")
        print(f"   Input shape: {data.shape}")
        print(f"   Prophet data shape: {prophet_data.shape}")
        print(f"   Prophet columns: {list(prophet_data.columns)}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_model_training():
    """Test Prophet model training."""
    print("🔄 Testing Prophet model training...")
    
    try:
        forecaster = create_health_forecaster()
        
        # Create sample data
        dates = pd.date_range(start='2025-01-01', end='2025-01-15', freq='H')
        data = pd.DataFrame({
            'timestamp': dates,
            'heart_rate': 70 + 10 * np.sin(np.arange(len(dates)) * 0.1) + np.random.normal(0, 5, len(dates))
        })
        
        # Train model
        results = forecaster.train_health_model(data, 'heart_rate', forecast_periods=24)
        
        if results:
            print(f"   ✅ Model training successful")
            print(f"   Model keys: {list(results.keys())}")
            print(f"   Forecast shape: {results['forecast'].shape}")
            print(f"   Metrics: {results['metrics']}")
            return True
        else:
            print(f"   ❌ Model training failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_anomaly_detection():
    """Test anomaly detection."""
    print("🔄 Testing anomaly detection...")
    
    try:
        forecaster = create_health_forecaster()
        
        # Create sample data with some anomalies
        dates = pd.date_range(start='2025-01-01', end='2025-01-07', freq='H')
        heart_rate = 70 + 10 * np.sin(np.arange(len(dates)) * 0.1) + np.random.normal(0, 5, len(dates))
        
        # Add some anomalies
        heart_rate[50:55] = 150  # High heart rate anomaly
        heart_rate[100:105] = 40  # Low heart rate anomaly
        
        data = pd.DataFrame({
            'timestamp': dates,
            'heart_rate': heart_rate,
            'temperature': 37 + 0.5 * np.sin(np.arange(len(dates)) * 0.05) + np.random.normal(0, 0.2, len(dates))
        })
        
        # Detect anomalies
        anomalies = forecaster.detect_anomalies(data, ['heart_rate', 'temperature'])
        
        print(f"   ✅ Anomaly detection successful")
        print(f"   Anomalies detected: {len(anomalies)}")
        
        for vital_sign, anomaly_data in anomalies.items():
            print(f"   {vital_sign}: {anomaly_data['anomaly_count']} anomalies ({anomaly_data['anomaly_percentage']:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_health_trends():
    """Test health trend analysis."""
    print("🔄 Testing health trend analysis...")
    
    try:
        forecaster = create_health_forecaster()
        
        # Create sample data with trends
        dates = pd.date_range(start='2025-01-01', end='2025-01-31', freq='H')
        heart_rate = 70 + np.arange(len(dates)) * 0.1 + 10 * np.sin(np.arange(len(dates)) * 0.1) + np.random.normal(0, 5, len(dates))
        
        data = pd.DataFrame({
            'timestamp': dates,
            'heart_rate': heart_rate,
            'temperature': 37 + 0.5 * np.sin(np.arange(len(dates)) * 0.05) + np.random.normal(0, 0.2, len(dates))
        })
        
        # Analyze trends
        trends = forecaster.get_health_trends(data, ['heart_rate', 'temperature'])
        
        print(f"   ✅ Trend analysis successful")
        print(f"   Trends analyzed: {len(trends)}")
        
        for vital_sign, trend_data in trends.items():
            print(f"   {vital_sign}:")
            print(f"     Mean: {trend_data['mean']:.2f}")
            print(f"     Trend: {trend_data['trend_direction']}")
            print(f"     Volatility: {trend_data['volatility']:.3f}")
            print(f"     Trend changes: {len(trend_data['trend_changes'])}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_patient_forecasting():
    """Test complete patient health forecasting."""
    print("🔄 Testing patient health forecasting...")
    
    try:
        forecaster = create_health_forecaster()
        
        # Test forecasting for a patient
        results = forecaster.forecast_patient_health(
            patient_id=1,
            vital_signs=['heart_rate', 'temperature', 'oxygen_saturation'],
            forecast_hours=24
        )
        
        if results:
            print(f"   ✅ Patient forecasting successful")
            print(f"   Patient ID: {results['patient_id']}")
            print(f"   Forecasts: {len(results['forecasts'])}")
            print(f"   Anomalies: {len(results['anomalies'])}")
            print(f"   Forecast hours: {results['forecast_hours']}")
            
            # Show forecast details
            for vital_sign, forecast_data in results['forecasts'].items():
                print(f"   {vital_sign}:")
                print(f"     MAE: {forecast_data['metrics'].get('mae', 'N/A'):.2f}")
                print(f"     MAPE: {forecast_data['metrics'].get('mape', 'N/A'):.2f}%")
                print(f"     Forecast points: {len(forecast_data['forecast'])}")
            
            return True
        else:
            print(f"   ❌ Patient forecasting failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def run_all_tests():
    """Run all forecasting tests."""
    print("🚀 Starting Time Series Forecasting Tests")
    print("=" * 60)
    
    tests = [
        ("Forecaster Initialization", test_forecaster_initialization),
        ("Data Preparation", test_data_preparation),
        ("Model Training", test_model_training),
        ("Anomaly Detection", test_anomaly_detection),
        ("Health Trends", test_health_trends),
        ("Patient Forecasting", test_patient_forecasting)
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
    print("📊 Forecasting Test Results:")
    print("=" * 60)
    
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
    run_all_tests() 