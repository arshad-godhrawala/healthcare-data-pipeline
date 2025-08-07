import sys
import os
sys.path.append(os.path.abspath('.'))

from src.data_ingestion.patient_data_loader import get_patient_vitals_from_db

def test_vitals_function():
    """Test the get_patient_vitals_from_db function directly."""
    print("🔄 Testing get_patient_vitals_from_db function...")
    
    try:
        # Test with patient ID 1
        vitals = get_patient_vitals_from_db(1)
        print(f"   📊 Retrieved {len(vitals)} vital signs for patient 1")
        
        if vitals:
            print("   📋 Sample vital signs:")
            for i, vital in enumerate(vitals[:3]):
                print(f"      Record {i+1}: {vital}")
        
        # Test with patient ID 42
        vitals2 = get_patient_vitals_from_db(42)
        print(f"   📊 Retrieved {len(vitals2)} vital signs for patient 42")
        
        if vitals2:
            print("   📋 Sample vital signs:")
            for i, vital in enumerate(vitals2[:3]):
                print(f"      Record {i+1}: {vital}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_vitals_function() 