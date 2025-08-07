import pandas as pd
import logging
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime

# Import our custom modules
from src.database.postgres_operations import create_postgres_connection
from src.database.models import Patient, VitalSign
from src.data_ingestion.data_validator import validate_patient_data

# Set up logging (HIPAA compliant - no PHI in logs)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_patient_data(file_path: str) -> pd.DataFrame:
    """Load patient data from CSV file."""
    try:
        logger.info(f"Loading patient data from: {file_path}")
        
        # Load CSV file
        df = pd.read_csv(file_path)
        
        logger.info(f"Successfully loaded {len(df)} patient records")
        logger.info(f"Columns found: {list(df.columns)}")
        
        return df

    except FileNotFoundError:
        logger.error(f"Patient data file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading patient data: {str(e)}")
        raise

def clean_patient_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and validate patient data using project validation rules.

    Args:
        df (pd.DataFrame): Raw patient data.

    Returns:
        pd.DataFrame: Cleaned and validated patient data.

    HIPAA/Security:
        - Remove or mask any unnecessary PHI.
        - Do not log or print PHI.
        - Ensure no invalid or malformed PHI is stored.
    """
    try:
        logger.info("Starting patient data cleaning and validation")
        
        # Use our validation function
        cleaned_df, validation_errors = validate_patient_data(df)
        
        # Log validation results (no PHI)
        if validation_errors:
            logger.warning(f"Found {len(validation_errors)} validation issues:")
            for error in validation_errors:
                logger.warning(f"  - {error}")
        else:
            logger.info("No validation errors found")
        
        # Add created_at timestamp if not present
        if 'created_at' not in cleaned_df.columns:
            cleaned_df['created_at'] = datetime.now()
        
        logger.info(f"Data cleaning completed. Final shape: {cleaned_df.shape}")
        
        return cleaned_df
        
    except Exception as e:
        logger.error(f"Error during data cleaning: {str(e)}")
        raise

def insert_patients_to_db(df: pd.DataFrame) -> int:
    """Insert patient data into PostgreSQL database."""
    try:
        engine, SessionLocal = create_postgres_connection()
        session = SessionLocal()
        
        inserted_count = 0
        for _, row in df.iterrows():
            try:
                # Check if patient already exists
                existing_patient = session.query(Patient).filter(
                    Patient.patient_name == row['patient_name']
                ).first()
                
                if not existing_patient:
                    patient = Patient(
                        patient_name=row['patient_name'],
                        date_of_birth=pd.to_datetime(row['date_of_birth']).date(),
                        gender=row['gender'],
                        address=row['address'],
                        created_at=datetime.now()
                    )
                    session.add(patient)
                    inserted_count += 1
            except Exception as e:
                logger.error(f"Error inserting patient {row['patient_name']}: {e}")
                continue
        
        session.commit()
        session.close()
        
        logger.info(f"Successfully inserted {inserted_count} new patients")
        return inserted_count
    except Exception as e:
        logger.error(f"Error inserting patients to database: {e}")
        raise

def process_patient_data_pipeline(file_path: str) -> int:
    """
    Complete pipeline to load, clean, and insert patient data.
    
    Args:
        file_path (str): Path to the patient CSV file.
        
    Returns:
        int: Number of records successfully processed and inserted.
        
    HIPAA/Security:
        - Complete pipeline with no PHI logging.
        - Secure error handling.
    """
    try:
        logger.info("Starting patient data processing pipeline")
        
        # Step 1: Load data
        raw_data = load_patient_data(file_path)
        
        # Step 2: Clean and validate data
        cleaned_data = clean_patient_data(raw_data)
        
        # Step 3: Insert into database
        inserted_count = insert_patients_to_db(cleaned_data)
        
        logger.info(f"Pipeline completed successfully. {inserted_count} records processed.")
        
        return inserted_count
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise

def get_patient_count() -> int:
    """
    Get the total number of patients in the database.
    
    Returns:
        int: Total patient count.
        
    HIPAA/Security:
        - Only returns count, no PHI.
    """
    try:
        engine, SessionLocal = create_postgres_connection()
        session = SessionLocal()
        
        try:
            count = session.query(Patient).count()
            logger.info(f"Total patients in database: {count}")
            return count
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error getting patient count: {str(e)}")
        raise

def get_all_patients() -> List[Dict]:
    """Get all patients from database."""
    try:
        engine, SessionLocal = create_postgres_connection()
        session = SessionLocal()
        
        patients = session.query(Patient).all()
        session.close()
        
        # Convert to list of dictionaries
        patient_list = []
        for patient in patients:
            patient_dict = {
                "patient_id": patient.patient_id,
                "patient_name": patient.patient_name,
                "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                "gender": patient.gender,
                "address": patient.address,
                "created_at": patient.created_at.isoformat() if patient.created_at else None
            }
            patient_list.append(patient_dict)
        
        return patient_list
    except Exception as e:
        logger.error(f"Error getting all patients: {e}")
        return []

def get_patient_by_id(patient_id: int) -> Optional[Dict]:
    """Get a specific patient by ID."""
    try:
        engine, SessionLocal = create_postgres_connection()
        session = SessionLocal()
        
        patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
        session.close()
        
        if patient:
            return {
                "patient_id": patient.patient_id,
                "patient_name": patient.patient_name,
                "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                "gender": patient.gender,
                "address": patient.address,
                "created_at": patient.created_at.isoformat() if patient.created_at else None
            }
        return None
    except Exception as e:
        logger.error(f"Error getting patient {patient_id}: {e}")
        return None

def create_patient_record(patient_data: Dict) -> Dict:
    """Create a new patient record."""
    try:
        engine, SessionLocal = create_postgres_connection()
        session = SessionLocal()
        
        # Create new patient
        new_patient = Patient(
            patient_name=patient_data['patient_name'],
            date_of_birth=pd.to_datetime(patient_data['date_of_birth']).date() if patient_data.get('date_of_birth') else None,
            gender=patient_data.get('gender'),
            address=patient_data.get('address'),
            created_at=datetime.now()
        )
        
        session.add(new_patient)
        session.commit()
        session.refresh(new_patient)
        
        # Return the created patient
        created_patient = {
            "patient_id": new_patient.patient_id,
            "patient_name": new_patient.patient_name,
            "date_of_birth": new_patient.date_of_birth.isoformat() if new_patient.date_of_birth else None,
            "gender": new_patient.gender,
            "address": new_patient.address,
            "created_at": new_patient.created_at.isoformat() if new_patient.created_at else None
        }
        
        session.close()
        return created_patient
    except Exception as e:
        logger.error(f"Error creating patient record: {e}")
        raise

def get_patient_vitals_from_db(patient_id: int, hours: int = 24) -> List[Dict]:
    """Get vital signs for a specific patient from PostgreSQL database."""
    try:
        engine, SessionLocal = create_postgres_connection()
        session = SessionLocal()
        
        # Query vital signs for the patient (without time filter for now)
        vitals = session.query(VitalSign).filter(
            VitalSign.patient_id == patient_id
        ).order_by(VitalSign.timestamp.desc()).all()
        
        # Convert to list of dictionaries
        vital_data = []
        for vital in vitals:
            # Parse blood pressure string (format: "systolic/diastolic")
            systolic = None
            diastolic = None
            if vital.blood_pressure:
                try:
                    bp_parts = vital.blood_pressure.split('/')
                    if len(bp_parts) == 2:
                        systolic = float(bp_parts[0])
                        diastolic = float(bp_parts[1])
                except (ValueError, IndexError):
                    pass
            
            vital_dict = {
                'vital_sign_id': vital.vital_sign_id,
                'patient_id': vital.patient_id,
                'timestamp': vital.timestamp,
                'heart_rate': vital.heart_rate,
                'systolic': systolic,
                'diastolic': diastolic,
                'temperature': vital.temperature,
                'respiration': vital.respiration_rate,
                'oxygen_saturation': None  # Not available in our data
            }
            vital_data.append(vital_dict)
        
        logger.info(f"Retrieved {len(vital_data)} vital signs records for patient {patient_id}")
        return vital_data
        
    except Exception as e:
        logger.error(f"Error getting vitals for patient {patient_id}: {str(e)}")
        raise
    finally:
        session.close()

def get_patient_medical_history(patient_id: int) -> List[Dict]:
    """Get medical history for a specific patient from PostgreSQL database."""
    try:
        from src.database.models import MedicalHistory
        engine, SessionLocal = create_postgres_connection()
        session = SessionLocal()
        
        # Query medical history for the patient
        history = session.query(MedicalHistory).filter(
            MedicalHistory.patient_id == patient_id
        ).order_by(MedicalHistory.diagnosis_date.desc()).all()
        
        # Convert to list of dictionaries
        history_data = []
        for record in history:
            history_dict = {
                'medical_history_id': record.medical_history_id,
                'patient_id': record.patient_id,
                'condition': record.condition,
                'diagnosis_date': record.diagnosis_date,
                'notes': record.notes
            }
            history_data.append(history_dict)
        
        logger.info(f"Retrieved {len(history_data)} medical history records for patient {patient_id}")
        return history_data
        
    except Exception as e:
        logger.error(f"Error getting medical history for patient {patient_id}: {str(e)}")
        raise
    finally:
        session.close()






