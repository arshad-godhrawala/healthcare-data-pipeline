"""
Test script for Feature Engineering functions
Tests health metrics calculation, time-based features, and health scoring.
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
    generate_health_scores,
    process_patient_features
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_vital_signs_data():
    """Create sample vital signs data for testing."""
    np.random.seed(42)
    
    # Generate 24 hours of data (every 30 minutes)
    timestamps = pd.date_range(
        start=datetime.now() - timedelta(days=1),
        end=datetime.now(),
        freq='30min'
    )
    
    # Generate realistic vital signs
    data = []
    for i, timestamp in enumerate(timestamps):
        # Simulate realistic vital signs with some variation
        heart_rate = np.random.normal(75, 10)  # Normal range 60-90
        temperature = np.random.normal(37.0, 0.5)  # Normal range 36.5-37.5
        systolic = np.random.normal(120, 15)  # Normal range 90-140
        diastolic = np.random.normal(80, 10)  # Normal range 60-90
        respiration = np.random.normal(16, 3)  # Normal range 12-20
        oxygen_saturation = np.random.normal(98, 1)  # Normal range 95-100
        
        # Add some anomalies for testing
        if i % 8 == 0:  # Every 4 hours, add some variation
            heart_rate += np.random.normal(0, 20)
            temperature += np.random.normal(0, 1)
        
        data.append({
            'timestamp': timestamp,
            'heart_rate': max(40, min(150, heart_rate)),
            'temperature': max(35, min(40, temperature)),
            'systolic': max(70, min(180, systolic)),
            'diastolic': max(50, min(110, diastolic)),
            'respiration': max(8, min(25, respiration)),
            'oxygen_saturation': max(90, min(100, oxygen_saturation))
        })
    
    return pd.DataFrame(data)

def test_health_metrics_calculation():
    """Test health metrics calculation."""
    print("🔄 Testing health metrics calculation...")
    
    # Create sample data
    df = create_sample_vital_signs_data()
    print(f"   Created sample data with {len(df)} records")
    
    # Calculate health metrics
    df_metrics = calculate_health_metrics(df)
    
    # Check if new metrics were added
    original_cols = set(df.columns)
    new_cols = set(df_metrics.columns) - original_cols
    
    print(f"   ✅ Added {len(new_cols)} new health metrics")
    print(f"   New metrics: {list(new_cols)}")
    
    # Verify specific metrics
    expected_metrics = ['hrv', 'heart_rate_trend', 'map', 'pulse_pressure', 
                       'bp_category', 'fever_status', 'temp_trend', 
                       'oxygen_status', 'respiratory_status', 
                       'vital_signs_stability', 'overall_health_indicator']
    
    found_metrics = [col for col in expected_metrics if col in df_metrics.columns]
    print(f"   Found {len(found_metrics)}/{len(expected_metrics)} expected metrics")
    
    return len(new_cols) > 0

def test_time_based_features():
    """Test time-based feature creation."""
    print("🔄 Testing time-based feature creation...")
    
    # Create sample data
    df = create_sample_vital_signs_data()
    
    # Create time-based features
    df_time = create_time_based_features(df)
    
    # Check if new time features were added
    original_cols = set(df.columns)
    new_cols = set(df_time.columns) - original_cols
    
    print(f"   ✅ Added {len(new_cols)} new time-based features")
    print(f"   New features: {list(new_cols)}")
    
    # Verify specific time features
    expected_time_features = ['hour', 'day_of_week', 'day_of_month', 'month',
                            'time_period', 'is_weekend', 'hr_hourly_avg',
                            'hr_daily_avg', 'temp_hourly_avg', 'hr_lag_1',
                            'hr_diff', 'temp_lag_1', 'temp_diff',
                            'hr_rolling_5min', 'hr_rolling_15min', 'temp_rolling_5min']
    
    found_features = [col for col in expected_time_features if col in df_time.columns]
    print(f"   Found {len(found_features)}/{len(expected_time_features)} expected time features")
    
    return len(new_cols) > 0

def test_health_scores():
    """Test health score generation."""
    print("🔄 Testing health score generation...")
    
    # Create sample data with metrics
    df = create_sample_vital_signs_data()
    df_metrics = calculate_health_metrics(df)
    
    # Generate health scores
    df_scores = generate_health_scores(df_metrics)
    
    # Check if new score features were added
    original_cols = set(df_metrics.columns)
    new_cols = set(df_scores.columns) - original_cols
    
    print(f"   ✅ Added {len(new_cols)} new health score features")
    print(f"   New scores: {list(new_cols)}")
    
    # Verify specific score features
    expected_scores = ['hr_score', 'bp_score', 'temp_score', 'oxygen_score',
                      'resp_score', 'composite_health_score', 'risk_level',
                      'alert_priority', 'health_trend', 'stability_score']
    
    found_scores = [col for col in expected_scores if col in df_scores.columns]
    print(f"   Found {len(found_scores)}/{len(expected_scores)} expected score features")
    
    # Check score ranges
    if 'composite_health_score' in df_scores.columns:
        score_range = df_scores['composite_health_score'].describe()
        print(f"   Health score range: {score_range['min']:.1f} - {score_range['max']:.1f}")
    
    return len(new_cols) > 0

def test_complete_feature_pipeline():
    """Test the complete feature engineering pipeline."""
    print("🔄 Testing complete feature engineering pipeline...")
    
    # Create sample data
    df = create_sample_vital_signs_data()
    print(f"   Input data shape: {df.shape}")
    
    # Apply complete pipeline
    df_metrics = calculate_health_metrics(df)
    df_time = create_time_based_features(df_metrics)
    df_scores = generate_health_scores(df_time)
    
    print(f"   Final data shape: {df_scores.shape}")
    print(f"   Total features added: {len(df_scores.columns) - len(df.columns)}")
    
    # Show sample of processed data
    print("   Sample processed data:")
    sample_cols = ['timestamp', 'heart_rate', 'hrv', 'bp_category', 
                   'composite_health_score', 'risk_level', 'health_trend']
    available_cols = [col for col in sample_cols if col in df_scores.columns]
    
    if available_cols:
        sample_data = df_scores[available_cols].head(3)
        print(sample_data.to_string())
    
    return len(df_scores.columns) > len(df.columns)

def test_patient_feature_processing():
    """Test patient feature processing with real data."""
    print("🔄 Testing patient feature processing...")
    
    try:
        # Process features for patient 1
        results = process_patient_features(patient_id=1, days=7)
        
        if results:
            print("   ✅ Successfully processed patient features")
            print(f"   Patient info: {results.get('patient_info', {})}")
            
            feature_summary = results.get('feature_summary', {})
            print(f"   Total records: {feature_summary.get('total_records', 0)}")
            print(f"   Health metrics: {feature_summary.get('health_metrics', {})}")
            
            return True
        else:
            print("   ⚠️ No results returned (possibly no data for patient)")
            return False
            
    except Exception as e:
        print(f"   ❌ Error processing patient features: {e}")
        return False

def run_all_tests():
    """Run all feature engineering tests."""
    print("🚀 Starting Feature Engineering Tests")
    print("=" * 60)
    
    tests = [
        ("Health Metrics Calculation", test_health_metrics_calculation),
        ("Time-based Features", test_time_based_features),
        ("Health Scores", test_health_scores),
        ("Complete Pipeline", test_complete_feature_pipeline),
        ("Patient Processing", test_patient_feature_processing)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n=== Testing {test_name} ===")
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
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:<30} {status}")
    
    print(f"\n   Total Tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    
    if passed == total:
        print("\n🎉 All feature engineering tests passed!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests() 