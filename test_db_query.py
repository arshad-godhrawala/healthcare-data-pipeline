import sys
import os
sys.path.append(os.path.abspath('.'))

from src.database.postgres_operations import create_postgres_connection
from src.database.models import Patient, VitalSign, MedicalHistory

def test_database_query():
    """Test direct database query to check vital signs data."""
    print("🔄 Testing direct database query...")
    
    try:
        engine, SessionLocal = create_postgres_connection()
        
        with SessionLocal() as session:
            # Check patient count
            patient_count = session.query(Patient).count()
            print(f"   📊 Total patients: {patient_count}")
            
            # Check vital signs count
            vitals_count = session.query(VitalSign).count()
            print(f"   📊 Total vital signs: {vitals_count}")
            
            # Check medical history count
            history_count = session.query(MedicalHistory).count()
            print(f"   📊 Total medical history: {history_count}")
            
            # Get sample patient
            sample_patient = session.query(Patient).first()
            if sample_patient:
                print(f"   👤 Sample patient: {sample_patient.patient_name} (ID: {sample_patient.patient_id})")
                
                # Get vitals for this patient
                patient_vitals = session.query(VitalSign).filter(
                    VitalSign.patient_id == sample_patient.patient_id
                ).all()
                
                print(f"   💓 Vital signs for patient {sample_patient.patient_id}: {len(patient_vitals)} records")
                
                if patient_vitals:
                    for i, vital in enumerate(patient_vitals[:3]):  # Show first 3
                        print(f"      Record {i+1}: HR={vital.heart_rate}, BP={vital.blood_pressure}, Temp={vital.temperature}")
            
            # Check all patients with vitals
            patients_with_vitals = session.query(Patient).join(VitalSign).distinct().count()
            print(f"   📊 Patients with vital signs: {patients_with_vitals}")
            
            # List some patient IDs that have vitals
            patient_ids_with_vitals = session.query(VitalSign.patient_id).distinct().limit(5).all()
            print(f"   📋 Sample patient IDs with vitals: {[pid[0] for pid in patient_ids_with_vitals]}")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_database_query() 