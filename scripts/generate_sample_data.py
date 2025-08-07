import pandas as pd
import numpy as np
from datetime import datetime, date
import os

def generate_sample_patients(num_patients: int = 50) -> pd.DataFrame:
    """
    Generate sample patient data for testing.
    
    Args:
        num_patients (int): Number of patients to generate
        
    Returns:
        pd.DataFrame: Sample patient data
    """
    # Sample data for realistic patient generation
    first_names = [
        "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa",
        "James", "Jennifer", "William", "Jessica", "Richard", "Amanda", "Thomas",
        "Melissa", "Christopher", "Nicole", "Daniel", "Stephanie", "Matthew",
        "Rebecca", "Anthony", "Laura", "Mark", "Michelle", "Donald", "Kimberly",
        "Steven", "Deborah", "Paul", "Dorothy", "Andrew", "Helen", "Joshua",
        "Sharon", "Kenneth", "Carol", "Kevin", "Donna", "Brian", "Ruth",
        "George", "Julie", "Edward", "Joyce", "Ronald", "Virginia", "Timothy"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
        "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
        "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
        "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell"
    ]
    
    genders = ["Male", "Female"]
    
    # Generate random patient data
    patients = []
    
    for i in range(num_patients):
        # Generate realistic age (18-85)
        age = np.random.randint(18, 86)
        birth_year = datetime.now().year - age
        birth_month = np.random.randint(1, 13)
        birth_day = np.random.randint(1, 29)  # Simplified for date generation
        
        # Generate DOB
        try:
            dob = date(birth_year, birth_month, birth_day)
        except ValueError:
            # Handle invalid dates (e.g., Feb 30)
            dob = date(birth_year, birth_month, 15)
        
        # Generate address
        street_numbers = np.random.randint(1, 9999)
        street_names = [
            "Main St", "Oak Ave", "Pine Rd", "Elm St", "Maple Dr", "Cedar Ln",
            "Washington Blvd", "Park Ave", "Lake Dr", "River Rd", "Hill St",
            "Spring Ave", "Summer St", "Winter Rd", "Autumn Ln", "Sunset Blvd"
        ]
        cities = [
            "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
            "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
            "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis",
            "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville"
        ]
        states = [
            "NY", "CA", "IL", "TX", "AZ", "PA", "FL", "OH", "NC", "WA", "CO",
            "GA", "MI", "VA", "OR", "NJ", "TN", "IN", "MA", "MO", "MD", "WI"
        ]
        
        street_name = np.random.choice(street_names)
        city = np.random.choice(cities)
        state = np.random.choice(states)
        zip_code = f"{np.random.randint(10000, 99999)}"
        
        address = f"{street_numbers} {street_name}, {city}, {state} {zip_code}"
        
        # Create patient record
        patient = {
            'patient_id': i + 1,
            'patient_name': f"{np.random.choice(first_names)} {np.random.choice(last_names)}",
            'date_of_birth': dob,
            'gender': np.random.choice(genders),
            'address': address
        }
        
        patients.append(patient)
    
    return pd.DataFrame(patients)

def generate_sample_vitals(num_records: int = 200) -> pd.DataFrame:
    """
    Generate sample vital signs data for testing.
    
    Args:
        num_records (int): Number of vital signs records to generate
        
    Returns:
        pd.DataFrame: Sample vital signs data
    """
    vitals = []
    
    for i in range(num_records):
        patient_id = np.random.randint(1, 51)  # Assuming 50 patients
        
        # Generate realistic vital signs
        heart_rate = np.random.normal(75, 15)  # Normal distribution around 75
        heart_rate = max(40, min(200, heart_rate))  # Clamp to realistic range
        
        # Blood pressure (systolic/diastolic)
        systolic = np.random.normal(120, 20)
        diastolic = np.random.normal(80, 10)
        systolic = max(90, min(200, systolic))
        diastolic = max(60, min(120, diastolic))
        blood_pressure = f"{int(systolic)}/{int(diastolic)}"
        
        # Temperature (normal body temp with some variation)
        temperature = np.random.normal(37.0, 0.5)
        temperature = max(35.0, min(40.0, temperature))
        
        # Respiration rate
        respiration = np.random.normal(16, 4)
        respiration = max(8, min(30, respiration))
        
        # Generate timestamp (within last 30 days)
        days_ago = np.random.randint(0, 30)
        hours_ago = np.random.randint(0, 24)
        minutes_ago = np.random.randint(0, 60)
        
        timestamp = datetime.now() - pd.Timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        
        vital = {
            'vital_sign_id': i + 1,
            'patient_id': patient_id,
            'timestamp': timestamp,
            'heart_rate': round(heart_rate, 1),
            'blood_pressure': blood_pressure,
            'temperature': round(temperature, 1),
            'respiration': round(respiration, 1)
        }
        
        vitals.append(vital)
    
    return pd.DataFrame(vitals)

def generate_sample_medical_history(num_records: int = 100) -> pd.DataFrame:
    """
    Generate sample medical history data for testing.
    
    Args:
        num_records (int): Number of medical history records to generate
        
    Returns:
        pd.DataFrame: Sample medical history data
    """
    conditions = [
        "Hypertension", "Diabetes Type 2", "Asthma", "Depression", "Anxiety",
        "Obesity", "High Cholesterol", "Arthritis", "Migraine", "Insomnia",
        "GERD", "Allergies", "Back Pain", "Headache", "Fatigue"
    ]
    
    medical_history = []
    
    for i in range(num_records):
        patient_id = np.random.randint(1, 51)  # Assuming 50 patients
        condition = np.random.choice(conditions)
        
        # Generate diagnosis date (within last 5 years)
        years_ago = np.random.randint(0, 5)
        months_ago = np.random.randint(0, 12)
        days_ago = np.random.randint(0, 30)
        
        diagnosis_date = date.today() - pd.Timedelta(days=years_ago*365 + months_ago*30 + days_ago)
        
        # Generate notes
        notes_templates = [
            f"Diagnosed with {condition.lower()}. Monitoring required.",
            f"Patient reports {condition.lower()} symptoms. Treatment initiated.",
            f"Routine check for {condition.lower()}. No complications.",
            f"Follow-up appointment for {condition.lower()} management.",
            f"New diagnosis of {condition.lower()}. Prescription provided."
        ]
        
        notes = np.random.choice(notes_templates)
        
        history = {
            'medical_history_id': i + 1,
            'patient_id': patient_id,
            'condition': condition,
            'diagnosis_date': diagnosis_date,
            'notes': notes
        }
        
        medical_history.append(history)
    
    return pd.DataFrame(medical_history)

def create_sample_data_files():
    """
    Create sample CSV files for testing the data pipeline.
    """
    # Create data directory if it doesn't exist
    data_dir = "data/sample_data"
    os.makedirs(data_dir, exist_ok=True)
    
    print("Generating sample patient data...")
    patients_df = generate_sample_patients(50)
    patients_df.to_csv(f"{data_dir}/patients.csv", index=False)
    print(f"✅ Created {data_dir}/patients.csv with {len(patients_df)} patients")
    
    print("Generating sample vital signs data...")
    vitals_df = generate_sample_vitals(200)
    vitals_df.to_csv(f"{data_dir}/vitals.csv", index=False)
    print(f"✅ Created {data_dir}/vitals.csv with {len(vitals_df)} vital signs records")
    
    print("Generating sample medical history data...")
    history_df = generate_sample_medical_history(100)
    history_df.to_csv(f"{data_dir}/medical_history.csv", index=False)
    print(f"✅ Created {data_dir}/medical_history.csv with {len(history_df)} medical history records")
    
    print("\nSample data files created successfully!")
    print(f"📁 Files created in: {data_dir}/")
    print("   - patients.csv")
    print("   - vitals.csv") 
    print("   - medical_history.csv")

if __name__ == "__main__":
    create_sample_data_files()
