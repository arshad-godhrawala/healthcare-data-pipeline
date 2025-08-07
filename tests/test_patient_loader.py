import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.data_ingestion.patient_data_loader import process_patient_data_pipeline, get_patient_count

def test_patient_data_loader():
    """Test the complete patient data loader pipeline"""
    print("=== Testing Patient Data Loader Pipeline ===")
    
    # Check if sample data exists
    sample_file = "data/sample_data/patients.csv"
    
    if not os.path.exists(sample_file):
        print(f"❌ Sample data file not found: {sample_file}")
        print("Please run: python scripts/generate_sample_data.py")
        return False
    
    try:
        # Test the complete pipeline
        print(f"📁 Loading data from: {sample_file}")
        
        # Run the complete pipeline
        inserted_count = process_patient_data_pipeline(sample_file)
        
        print(f"✅ Pipeline completed successfully!")
        print(f"   Records inserted: {inserted_count}")
        
        # Verify the data was inserted
        total_patients = get_patient_count()
        print(f"   Total patients in database: {total_patients}")
        
        if total_patients > 0:
            print("✅ Patient data successfully loaded into database!")
            return True
        else:
            print("❌ No patients found in database after insertion")
            return False
            
    except Exception as e:
        print(f"❌ Pipeline test failed: {str(e)}")
        return False

def test_individual_functions():
    """Test individual functions of the patient data loader"""
    print("\n=== Testing Individual Functions ===")
    
    from src.data_ingestion.patient_data_loader import load_patient_data, clean_patient_data
    
    sample_file = "data/sample_data/patients.csv"
    
    if not os.path.exists(sample_file):
        print(f"❌ Sample data file not found: {sample_file}")
        return False
    
    try:
        # Test load function
        print("1. Testing load_patient_data()...")
        raw_data = load_patient_data(sample_file)
        print(f"   ✅ Loaded {len(raw_data)} records")
        print(f"   Columns: {list(raw_data.columns)}")
        
        # Test clean function
        print("2. Testing clean_patient_data()...")
        cleaned_data = clean_patient_data(raw_data)
        print(f"   ✅ Cleaned data shape: {cleaned_data.shape}")
        
        # Show sample of cleaned data (without PHI)
        print(f"   Sample data types:")
        for col, dtype in cleaned_data.dtypes.items():
            print(f"     {col}: {dtype}")
        
        return True
        
    except Exception as e:
        print(f"❌ Individual function test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Patient Data Loader Tests")
    print("=" * 50)
    
    # Test individual functions first
    individual_success = test_individual_functions()
    
    # Test complete pipeline
    pipeline_success = test_patient_data_loader()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Individual functions: {'✅ PASS' if individual_success else '❌ FAIL'}")
    print(f"   Complete pipeline: {'✅ PASS' if pipeline_success else '❌ FAIL'}")
    
    if individual_success and pipeline_success:
        print("\n🎉 All tests passed! Patient data loader is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.") 