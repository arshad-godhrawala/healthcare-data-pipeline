import sys
import os
import pandas as pd
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.postgres_operations import create_postgres_connection
from src.database.models import Patient, VitalSign, MedicalHistory

def load_patients_data():
    """Load patients data from CSV to PostgreSQL."""
    print("🔄 Loading patients data...")
    
    try:
        # Read CSV file
        patients_df = pd.read_csv('data/sample_data/patients.csv')
        print(f"   📊 Found {len(patients_df)} patients in CSV")
        
        # Create database connection
        engine, SessionLocal = create_postgres_connection()
        
        with SessionLocal() as session:
            # Check if data already exists
            existing_count = session.query(Patient).count()
            if existing_count > 0:
                print(f"   ⚠️ Database already contains {existing_count} patients")
                response = input("   Do you want to clear existing data and reload? (y/N): ")
                if response.lower() != 'y':
                    print("   ❌ Data loading cancelled")
                    return False
                # Clear existing data
                session.query(Patient).delete()
                session.query(VitalSign).delete()
                session.query(MedicalHistory).delete()
                session.commit()
                print("   🗑️ Cleared existing data")
            
            # Insert patients
            for _, row in patients_df.iterrows():
                patient = Patient(
                    patient_id=row['patient_id'],
                    patient_name=row['patient_name'],
                    date_of_birth=pd.to_datetime(row['date_of_birth']).date(),
                    gender=row['gender'],
                    address=row['address'],
                    created_at=datetime.now()
                )
                session.add(patient)
            
            session.commit()
            print(f"   ✅ Successfully loaded {len(patients_df)} patients")
            return True
            
    except Exception as e:
        print(f"   ❌ Error loading patients: {e}")
        return False

def load_vitals_data():
    """Load vital signs data from CSV to PostgreSQL."""
    print("🔄 Loading vital signs data...")
    
    try:
        # Read CSV file
        vitals_df = pd.read_csv('data/sample_data/vitals.csv')
        print(f"   📊 Found {len(vitals_df)} vital signs records in CSV")
        
        # Create database connection
        engine, SessionLocal = create_postgres_connection()
        
        with SessionLocal() as session:
            # Check if data already exists
            existing_count = session.query(VitalSign).count()
            if existing_count > 0:
                print(f"   ⚠️ Database already contains {existing_count} vital signs records")
                return True  # Skip if data exists
            
            # Insert vital signs
            for _, row in vitals_df.iterrows():
                vital = VitalSign(
                    vital_sign_id=row['vital_sign_id'],
                    patient_id=row['patient_id'],
                    timestamp=pd.to_datetime(row['timestamp']),
                    heart_rate=row['heart_rate'],
                    blood_pressure=row['blood_pressure'],
                    temperature=row['temperature'],
                    respiration_rate=int(row['respiration'])
                )
                session.add(vital)
            
            session.commit()
            print(f"   ✅ Successfully loaded {len(vitals_df)} vital signs records")
            return True
            
    except Exception as e:
        print(f"   ❌ Error loading vital signs: {e}")
        return False

def load_medical_history_data():
    """Load medical history data from CSV to PostgreSQL."""
    print("🔄 Loading medical history data...")
    
    try:
        # Read CSV file
        history_df = pd.read_csv('data/sample_data/medical_history.csv')
        print(f"   📊 Found {len(history_df)} medical history records in CSV")
        
        # Create database connection
        engine, SessionLocal = create_postgres_connection()
        
        with SessionLocal() as session:
            # Check if data already exists
            existing_count = session.query(MedicalHistory).count()
            if existing_count > 0:
                print(f"   ⚠️ Database already contains {existing_count} medical history records")
                return True  # Skip if data exists
            
            # Insert medical history
            for _, row in history_df.iterrows():
                history = MedicalHistory(
                    medical_history_id=row['medical_history_id'],
                    patient_id=row['patient_id'],
                    condition=row['condition'],
                    diagnosis_date=pd.to_datetime(row['diagnosis_date']).date(),
                    notes=row['notes']
                )
                session.add(history)
            
            session.commit()
            print(f"   ✅ Successfully loaded {len(history_df)} medical history records")
            return True
            
    except Exception as e:
        print(f"   ❌ Error loading medical history: {e}")
        return False

def verify_data_loading():
    """Verify that data was loaded correctly."""
    print("\n🔄 Verifying data loading...")
    
    try:
        engine, SessionLocal = create_postgres_connection()
        
        with SessionLocal() as session:
            # Count records
            patient_count = session.query(Patient).count()
            vitals_count = session.query(VitalSign).count()
            history_count = session.query(MedicalHistory).count()
            
            print(f"   📊 Database Summary:")
            print(f"      - Patients: {patient_count}")
            print(f"      - Vital Signs: {vitals_count}")
            print(f"      - Medical History: {history_count}")
            
            # Show sample data
            if patient_count > 0:
                sample_patient = session.query(Patient).first()
                print(f"   👤 Sample Patient: {sample_patient.patient_name} (ID: {sample_patient.patient_id})")
            
            if vitals_count > 0:
                sample_vital = session.query(VitalSign).first()
                print(f"   💓 Sample Vital: Heart Rate {sample_vital.heart_rate}, BP {sample_vital.blood_pressure}")
            
            if history_count > 0:
                sample_history = session.query(MedicalHistory).first()
                print(f"   📋 Sample History: {sample_history.condition} diagnosed on {sample_history.diagnosis_date}")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Error verifying data: {e}")
        return False

def main():
    """Main function to load all sample data."""
    print("🚀 Starting Sample Data Loading Process")
    print("=" * 50)
    
    # Load data in order (patients first, then related data)
    results = []
    
    results.append(("Patients", load_patients_data()))
    results.append(("Vital Signs", load_vitals_data()))
    results.append(("Medical History", load_medical_history_data()))
    
    # Verify data loading
    results.append(("Data Verification", verify_data_loading()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Data Loading Summary:")
    print("=" * 50)
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for data_type, result in results:
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"   {data_type:<20} {status}")
    
    print(f"\n   Total Steps: {total_count}")
    print(f"   Successful: {success_count}")
    print(f"   Failed: {total_count - success_count}")
    
    if success_count == total_count:
        print("\n🎉 All data loaded successfully!")
        print("📊 You can now view the data in your dashboard at: http://localhost:3000")
    else:
        print("\n⚠️ Some data loading steps failed. Check the errors above.")

if __name__ == "__main__":
    main() 