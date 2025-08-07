import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import pandas as pd
from datetime import datetime, date
from src.api.schemas import PatientSchema, VitalSignSchema, MedicalHistorySchema
from src.data_ingestion.data_validator import validate_patient_data, validate_sensor_data, detect_outliers_iqr

def test_pydantic_schemas():
    """Test Pydantic schema validation"""
    print("=== Testing Pydantic Schemas ===")
    
    # Test PatientSchema
    try:
        patient_data = {
            "patient_id": 1,
            "patient_name": "John Doe",
            "date_of_birth": 1990,
            "gender": "Male",
            "address": "123 Main St",
            "created_at": datetime.now()
        }
        patient = PatientSchema(**patient_data)
        print("✅ PatientSchema validation passed")
        print(f"   Patient: {patient.patient_name}")
    except Exception as e:
        print(f"❌ PatientSchema validation failed: {e}")
    
    # Test VitalSignSchema
    try:
        vital_data = {
            "vital_sign_id": 1,
            "patient_id": 1,
            "timestamp": datetime.now(),
            "heart_rate": 75.0,
            "blood_pressure": "120/80",
            "temperature": 37.0,
            "respiration": 16.0
        }
        vital = VitalSignSchema(**vital_data)
        print("✅ VitalSignSchema validation passed")
        print(f"   Heart Rate: {vital.heart_rate}")
    except Exception as e:
        print(f"❌ VitalSignSchema validation failed: {e}")
    
    # Test MedicalHistorySchema
    try:
        history_data = {
            "medical_history_id": 1,
            "patient_id": 1,
            "condition": "Hypertension",
            "diagnosis_date": date(2020, 1, 15),
            "notes": "Mild hypertension, monitor blood pressure"
        }
        history = MedicalHistorySchema(**history_data)
        print("✅ MedicalHistorySchema validation passed")
        print(f"   Condition: {history.condition}")
    except Exception as e:
        print(f"❌ MedicalHistorySchema validation failed: {e}")

def test_data_validation_functions():
    """Test data validation functions"""
    print("\n=== Testing Data Validation Functions ===")
    
    # Create sample patient data
    patient_data = {
        'patient_name': ['John Doe', 'Jane Smith', '', 'Bob Johnson'],
        'date_of_birth': ['1990-01-01', '1985-05-15', 'invalid_date', '1975-12-25'],
        'gender': ['Male', 'Female', 'Unknown', 'Male'],
        'address': ['123 Main St', '456 Oak Ave', '789 Pine Rd' * 20, '321 Elm St']
    }
    patient_df = pd.DataFrame(patient_data)
    
    print("Original patient data:")
    print(patient_df)
    print(f"Shape: {patient_df.shape}")
    
    # Test patient data validation
    cleaned_patients, patient_errors = validate_patient_data(patient_df)
    print(f"\nPatient validation errors: {len(patient_errors)}")
    for error in patient_errors:
        print(f"  - {error}")
    
    print("\nCleaned patient data:")
    print(cleaned_patients)
    print(f"Shape: {cleaned_patients.shape}")
    
    # Create sample sensor data
    sensor_data = {
        'patient_id': [1, 1, 2, 2, 3],
        'timestamp': ['2024-01-01 10:00:00', '2024-01-01 11:00:00', '2024-01-01 12:00:00', 'invalid_time', '2024-01-01 14:00:00'],
        'heart_rate': [75, 80, 120, 400, 65],  # 400 is outlier
        'blood_pressure': ['120/80', '125/85', '140/90', 'invalid_bp', '110/70'],
        'temperature': [37.0, 37.2, 38.5, 50.0, 36.8],  # 50.0 is outlier
        'respiration': [16, 18, 22, 150, 14]  # 150 is outlier
    }
    sensor_df = pd.DataFrame(sensor_data)
    
    print("\nOriginal sensor data:")
    print(sensor_df)
    print(f"Shape: {sensor_df.shape}")
    
    # Test sensor data validation
    cleaned_sensors, sensor_errors = validate_sensor_data(sensor_df)
    print(f"\nSensor validation errors: {len(sensor_errors)}")
    for error in sensor_errors:
        print(f"  - {error}")
    
    print("\nCleaned sensor data:")
    print(cleaned_sensors)
    print(f"Shape: {cleaned_sensors.shape}")
    
    # Test outlier detection
    if 'heart_rate' in cleaned_sensors.columns:
        outlier_df = detect_outliers_iqr(cleaned_sensors, 'heart_rate')
        outliers = outlier_df[outlier_df['heart_rate_is_outlier'] == True]
        print(f"\nOutlier detection for heart_rate:")
        print(f"Found {len(outliers)} outliers")
        if len(outliers) > 0:
            print(outliers[['patient_id', 'heart_rate']])

def test_error_cases():
    """Test error cases and edge cases"""
    print("\n=== Testing Error Cases ===")
    
    # Test invalid blood pressure format
    try:
        vital_data = {
            "vital_sign_id": 1,
            "patient_id": 1,
            "timestamp": datetime.now(),
            "heart_rate": 75.0,
            "blood_pressure": "80/120",  # Diastolic > Systolic
            "temperature": 37.0,
            "respiration": 16.0
        }
        vital = VitalSignSchema(**vital_data)
        print("❌ Should have failed for invalid blood pressure format")
    except Exception as e:
        print(f"✅ Correctly caught blood pressure error: {e}")
    
    # Test invalid gender
    try:
        patient_data = {
            "patient_id": 1,
            "patient_name": "Test User",
            "date_of_birth": 1990,
            "gender": "InvalidGender",
            "address": "123 Test St",
            "created_at": datetime.now()
        }
        patient = PatientSchema(**patient_data)
        print("❌ Should have failed for invalid gender")
    except Exception as e:
        print(f"✅ Correctly caught gender validation error: {e}")

if __name__ == "__main__":
    test_pydantic_schemas()
    test_data_validation_functions()
    test_error_cases()
    print("\n=== Validation Testing Complete ===") 