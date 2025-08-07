import sys
import os
sys.path.append(os.path.abspath('.'))

from src.data_ingestion.patient_data_loader import get_patient_vitals_from_db
from src.api.schemas import VitalSignResponse
from pydantic import ValidationError

def test_response_model():
    """Test if VitalSignResponse can serialize our data."""
    print("🔄 Testing VitalSignResponse model...")
    
    try:
        # Get vital signs data
        vitals = get_patient_vitals_from_db(1)
        print(f"   📊 Retrieved {len(vitals)} vital signs")
        
        if vitals:
            sample_vital = vitals[0]
            print(f"   📋 Sample vital data: {sample_vital}")
            
            # Try to create VitalSignResponse
            try:
                response = VitalSignResponse(**sample_vital)
                print(f"   ✅ Successfully created VitalSignResponse: {response}")
                return True
            except ValidationError as e:
                print(f"   ❌ Validation error: {e}")
                return False
            except Exception as e:
                print(f"   ❌ Error creating response: {e}")
                return False
        
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_response_model() 