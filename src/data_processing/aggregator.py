import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

# Import our custom modules
from src.database.postgres_operations import create_postgres_connection
from src.database.models import Patient
from src.data_ingestion.sensor_data_collector import SensorDataCollector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def aggregate_vitals_hourly(patient_id: int, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Aggregate vital signs data for a patient by hour within a date range.
    
    Args:
        patient_id (int): Patient ID to aggregate data for
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
        
    Returns:
        pd.DataFrame: Hourly aggregated vital signs data
    """
    try:
        # Get sensor data from InfluxDB
        collector = SensorDataCollector()
        
        # Convert dates to datetime objects
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        # Query data for the date range
        vitals_data = collector.query_patient_vitals(patient_id, hours=int((end_dt - start_dt).total_seconds() / 3600))
        
        if not vitals_data:
            logger.warning(f"No vital signs data found for patient {patient_id} in date range {start_date} to {end_date}")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(vitals_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Set timestamp as index for resampling
        df.set_index('timestamp', inplace=True)
        
        # Aggregate by hour
        hourly_agg = df.resample('H').agg({
            'heart_rate': ['mean', 'min', 'max', 'std'],
            'systolic': ['mean', 'min', 'max'],
            'diastolic': ['mean', 'min', 'max'],
            'temperature': ['mean', 'min', 'max'],
            'respiration': ['mean', 'min', 'max'],
            'oxygen_saturation': ['mean', 'min', 'max']
        }).round(2)
        
        # Flatten column names
        hourly_agg.columns = ['_'.join(col).strip() for col in hourly_agg.columns]
        
        # Reset index to get timestamp as column
        hourly_agg.reset_index(inplace=True)
        
        logger.info(f"Aggregated {len(hourly_agg)} hourly records for patient {patient_id}")
        return hourly_agg
        
    except Exception as e:
        logger.error(f"Error aggregating vitals for patient {patient_id}: {str(e)}")
        raise

def calculate_health_trends(patient_id: int, days: int = 30) -> Dict:
    """
    Calculate health trends and summary statistics for a patient.
    
    Args:
        patient_id (int): Patient ID to calculate trends for
        days (int): Number of days to look back
        
    Returns:
        Dict: Dictionary containing health trends and statistics
    """
    try:
        # Get recent vital signs data
        collector = SensorDataCollector()
        vitals_data = collector.query_patient_vitals(patient_id, hours=days*24)
        
        if not vitals_data:
            logger.warning(f"No vital signs data found for patient {patient_id} in last {days} days")
            return {}
        
        df = pd.DataFrame(vitals_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Calculate trends and statistics
        trends = {}
        
        # Heart rate trends
        if 'heart_rate' in df.columns:
            trends['heart_rate'] = {
                'mean': df['heart_rate'].mean(),
                'std': df['heart_rate'].std(),
                'min': df['heart_rate'].min(),
                'max': df['heart_rate'].max(),
                'trend': 'increasing' if df['heart_rate'].iloc[-1] > df['heart_rate'].iloc[0] else 'decreasing'
            }
        
        # Temperature trends
        if 'temperature' in df.columns:
            trends['temperature'] = {
                'mean': df['temperature'].mean(),
                'std': df['temperature'].std(),
                'min': df['temperature'].min(),
                'max': df['temperature'].max(),
                'fever_episodes': (df['temperature'] > 37.5).sum()
            }
        
        # Blood pressure trends
        if 'systolic' in df.columns and 'diastolic' in df.columns:
            trends['blood_pressure'] = {
                'systolic_mean': df['systolic'].mean(),
                'diastolic_mean': df['diastolic'].mean(),
                'systolic_std': df['systolic'].std(),
                'diastolic_std': df['diastolic'].std(),
                'hypertension_episodes': ((df['systolic'] > 140) | (df['diastolic'] > 90)).sum()
            }
        
        # Oxygen saturation trends
        if 'oxygen_saturation' in df.columns:
            trends['oxygen_saturation'] = {
                'mean': df['oxygen_saturation'].mean(),
                'min': df['oxygen_saturation'].min(),
                'low_oxygen_episodes': (df['oxygen_saturation'] < 95).sum()
            }
        
        # Overall health score (simple calculation)
        health_score = 100
        if 'heart_rate' in trends:
            if trends['heart_rate']['mean'] > 100 or trends['heart_rate']['mean'] < 60:
                health_score -= 20
        if 'temperature' in trends and trends['temperature']['fever_episodes'] > 0:
            health_score -= 15
        if 'oxygen_saturation' in trends and trends['oxygen_saturation']['low_oxygen_episodes'] > 0:
            health_score -= 25
        
        trends['health_score'] = max(0, health_score)
        
        logger.info(f"Calculated health trends for patient {patient_id}")
        return trends
        
    except Exception as e:
        logger.error(f"Error calculating health trends for patient {patient_id}: {str(e)}")
        raise

def merge_patient_sensor_data(patient_ids: List[int]) -> pd.DataFrame:
    """
    Merge patient demographic data with their sensor/vital data.
    
    Args:
        patient_ids (List[int]): List of patient IDs to merge data for
        
    Returns:
        pd.DataFrame: Merged patient and sensor data
    """
    try:
        # Get patient demographic data from PostgreSQL
        engine, SessionLocal = create_postgres_connection()
        session = SessionLocal()
        
        patients_data = []
        for patient_id in patient_ids:
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            if patient:
                patients_data.append({
                    'patient_id': patient.patient_id,
                    'patient_name': patient.patient_name,
                    'date_of_birth': patient.date_of_birth,
                    'gender': patient.gender,
                    'address': patient.address
                })
        
        session.close()
        
        if not patients_data:
            logger.warning(f"No patient data found for IDs: {patient_ids}")
            return pd.DataFrame()
        
        patients_df = pd.DataFrame(patients_data)
        
        # Get sensor data for all patients
        collector = SensorDataCollector()
        all_sensor_data = []
        
        for patient_id in patient_ids:
            vitals_data = collector.query_patient_vitals(patient_id, hours=24)  # Last 24 hours
            if vitals_data:
                for record in vitals_data:
                    record['patient_id'] = patient_id
                    all_sensor_data.append(record)
        
        if not all_sensor_data:
            logger.warning(f"No sensor data found for patients: {patient_ids}")
            return patients_df
        
        sensor_df = pd.DataFrame(all_sensor_data)
        
        # Merge patient and sensor data
        merged_df = pd.merge(patients_df, sensor_df, on='patient_id', how='inner')
        
        logger.info(f"Merged data for {len(patient_ids)} patients with {len(merged_df)} sensor records")
        return merged_df
        
    except Exception as e:
        logger.error(f"Error merging patient and sensor data: {str(e)}")
        raise

def get_patient_summary_stats(patient_id: int) -> Dict:
    """
    Get comprehensive summary statistics for a patient.
    
    Args:
        patient_id (int): Patient ID to get summary for
        
    Returns:
        Dict: Summary statistics and health metrics
    """
    try:
        # Get health trends
        trends = calculate_health_trends(patient_id, days=7)  # Last 7 days
        
        # Get hourly aggregation for last 24 hours
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        hourly_data = aggregate_vitals_hourly(patient_id, start_date, end_date)
        
        summary = {
            'patient_id': patient_id,
            'analysis_period': '7 days',
            'trends': trends,
            'hourly_data_points': len(hourly_data),
            'last_updated': datetime.now().isoformat()
        }
        
        logger.info(f"Generated summary statistics for patient {patient_id}")
        return summary
        
    except Exception as e:
        logger.error(f"Error generating summary for patient {patient_id}: {str(e)}")
        raise
