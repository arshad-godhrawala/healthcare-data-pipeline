import sys
import os
sys.path.append(os.path.abspath('.'))

def test_api_logic():
    """Test the API logic directly."""
    print("🔄 Testing API logic directly...")
    
    try:
        from src.data_ingestion.patient_data_loader import get_patient_vitals_from_db
        from src.api.schemas import VitalSignResponse
        
        patient_id = 1
        hours = 24
        
        print(f"   📊 Getting vitals for patient {patient_id}")
        vitals = get_patient_vitals_from_db(patient_id, hours)
        print(f"   📊 Retrieved {len(vitals)} vitals")
        
        if vitals:
            print(f"   📋 Sample vital: {vitals[0]}")
            
            # Try to convert to response models
            response_models = []
            for vital in vitals:
                try:
                    response = VitalSignResponse(**vital)
                    response_models.append(response)
                except Exception as e:
                    print(f"   ❌ Error converting vital: {e}")
            
            print(f"   ✅ Successfully converted {len(response_models)} vitals to response models")
            
            # Convert back to dict for JSON serialization
            response_dicts = []
            for response in response_models:
                response_dicts.append(response.dict())
            
            print(f"   ✅ Successfully converted {len(response_dicts)} responses to dicts")
            if response_dicts:
                print(f"   📋 Sample response dict: {response_dicts[0]}")
            
            return True
        
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_api_logic() 