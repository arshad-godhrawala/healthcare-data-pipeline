import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, date
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_patient_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Validate and clean patient data from DataFrame.
    
    Args:
        df: DataFrame containing patient data
        
    Returns:
        Tuple of (cleaned_dataframe, list_of_validation_errors)
    """
    errors = []
    cleaned_df = df.copy()
    
    # Check required columns
    required_columns = ['patient_name', 'date_of_birth', 'gender', 'address']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")
    
    # Validate name field
    if 'patient_name' in df.columns:
        # Remove leading/trailing whitespace
        cleaned_df['patient_name'] = cleaned_df['patient_name'].astype(str).str.strip()
        # Check for empty names
        empty_names = cleaned_df['patient_name'].isna() | (cleaned_df['patient_name'] == '')
        if empty_names.any():
            errors.append(f"Found {empty_names.sum()} empty patient names")
            cleaned_df = cleaned_df[~empty_names]
    
    # Validate date of birth
    if 'date_of_birth' in df.columns:
        try:
            cleaned_df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')
            invalid_dobs = cleaned_df['date_of_birth'].isna()
            if invalid_dobs.any():
                errors.append(f"Found {invalid_dobs.sum()} invalid dates of birth")
        except Exception as e:
            errors.append(f"Error processing dates of birth: {str(e)}")
    
    # Validate gender
    if 'gender' in df.columns:
        valid_genders = ['Male', 'Female', 'Other']
        cleaned_df['gender'] = cleaned_df['gender'].astype(str).str.strip()
        invalid_genders = ~cleaned_df['gender'].isin(valid_genders)
        if invalid_genders.any():
            errors.append(f"Found {invalid_genders.sum()} invalid gender values")
            # Replace invalid values with 'Other'
            cleaned_df.loc[invalid_genders, 'gender'] = 'Other'
    
    # Validate address
    if 'address' in df.columns:
        cleaned_df['address'] = cleaned_df['address'].astype(str).str.strip()
        # Check for unreasonably long addresses
        long_addresses = cleaned_df['address'].str.len() > 255
        if long_addresses.any():
            errors.append(f"Found {long_addresses.sum()} addresses exceeding 255 characters")
            # Truncate long addresses
            cleaned_df.loc[long_addresses, 'address'] = cleaned_df.loc[long_addresses, 'address'].str[:255]
    
    logger.info(f"Patient data validation completed. {len(errors)} issues found.")
    return cleaned_df, errors

def validate_sensor_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Validate and clean sensor/vital signs data from DataFrame.
    
    Args:
        df: DataFrame containing sensor data
        
    Returns:
        Tuple of (cleaned_dataframe, list_of_validation_errors)
    """
    errors = []
    cleaned_df = df.copy()
    
    # Check required columns
    required_columns = ['patient_id', 'timestamp']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")
    
    # Validate patient_id
    if 'patient_id' in df.columns:
        # Ensure patient_id is numeric and positive
        try:
            cleaned_df['patient_id'] = pd.to_numeric(df['patient_id'], errors='coerce')
            invalid_patient_ids = cleaned_df['patient_id'].isna() | (cleaned_df['patient_id'] <= 0)
            if invalid_patient_ids.any():
                errors.append(f"Found {invalid_patient_ids.sum()} invalid patient IDs")
                cleaned_df = cleaned_df[~invalid_patient_ids]
        except Exception as e:
            errors.append(f"Error processing patient IDs: {str(e)}")
    
    # Validate timestamp
    if 'timestamp' in df.columns:
        try:
            cleaned_df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            invalid_timestamps = cleaned_df['timestamp'].isna()
            if invalid_timestamps.any():
                errors.append(f"Found {invalid_timestamps.sum()} invalid timestamps")
                cleaned_df = cleaned_df[~invalid_timestamps]
        except Exception as e:
            errors.append(f"Error processing timestamps: {str(e)}")
    
    # Validate heart rate
    if 'heart_rate' in df.columns:
        try:
            cleaned_df['heart_rate'] = pd.to_numeric(df['heart_rate'], errors='coerce')
            # Check for physiologically impossible values
            invalid_hr = (cleaned_df['heart_rate'] < 0) | (cleaned_df['heart_rate'] > 300)
            if invalid_hr.any():
                errors.append(f"Found {invalid_hr.sum()} heart rate values outside normal range (0-300)")
                # Remove impossible values
                cleaned_df.loc[invalid_hr, 'heart_rate'] = np.nan
        except Exception as e:
            errors.append(f"Error processing heart rate: {str(e)}")
    
    # Validate blood pressure
    if 'blood_pressure' in df.columns:
        cleaned_df['blood_pressure'] = cleaned_df['blood_pressure'].astype(str).str.strip()
        # Check format (systolic/diastolic)
        bp_pattern = r'^\d{2,3}/\d{2,3}$'
        invalid_bp = ~cleaned_df['blood_pressure'].str.match(bp_pattern, na=False)
        if invalid_bp.any():
            errors.append(f"Found {invalid_bp.sum()} blood pressure values in incorrect format")
            # Set invalid values to NaN
            cleaned_df.loc[invalid_bp, 'blood_pressure'] = np.nan
    
    # Validate temperature
    if 'temperature' in df.columns:
        try:
            cleaned_df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
            # Check for physiologically impossible values
            invalid_temp = (cleaned_df['temperature'] < 30) | (cleaned_df['temperature'] > 45)
            if invalid_temp.any():
                errors.append(f"Found {invalid_temp.sum()} temperature values outside normal range (30-45°C)")
                # Remove impossible values
                cleaned_df.loc[invalid_temp, 'temperature'] = np.nan
        except Exception as e:
            errors.append(f"Error processing temperature: {str(e)}")
    
    # Validate respiration rate
    if 'respiration' in df.columns:
        try:
            cleaned_df['respiration'] = pd.to_numeric(df['respiration'], errors='coerce')
            # Check for physiologically impossible values
            invalid_resp = (cleaned_df['respiration'] < 0) | (cleaned_df['respiration'] > 100)
            if invalid_resp.any():
                errors.append(f"Found {invalid_resp.sum()} respiration values outside normal range (0-100)")
                # Remove impossible values
                cleaned_df.loc[invalid_resp, 'respiration'] = np.nan
        except Exception as e:
            errors.append(f"Error processing respiration rate: {str(e)}")
    
    logger.info(f"Sensor data validation completed. {len(errors)} issues found.")
    return cleaned_df, errors

def detect_outliers_iqr(df: pd.DataFrame, column: str, factor: float = 1.5) -> pd.DataFrame:
    """
    Detect outliers using the Interquartile Range (IQR) method.
    
    Args:
        df: DataFrame containing the data
        column: Column name to check for outliers
        factor: IQR factor (default 1.5)
        
    Returns:
        DataFrame with outliers marked
    """
    if column not in df.columns:
        logger.warning(f"Column '{column}' not found in DataFrame")
        return df
    
    # Calculate Q1, Q3, and IQR
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    
    # Define outlier bounds
    lower_bound = Q1 - factor * IQR
    upper_bound = Q3 + factor * IQR
    
    # Mark outliers
    df_copy = df.copy()
    df_copy[f'{column}_is_outlier'] = (df_copy[column] < lower_bound) | (df_copy[column] > upper_bound)
    
    outlier_count = df_copy[f'{column}_is_outlier'].sum()
    logger.info(f"Detected {outlier_count} outliers in column '{column}'")
    
    return df_copy

def validate_data_types(df: pd.DataFrame, expected_types: Dict[str, str]) -> List[str]:
    """
    Validate that DataFrame columns have expected data types.
    
    Args:
        df: DataFrame to validate
        expected_types: Dictionary mapping column names to expected types
        
    Returns:
        List of validation errors
    """
    errors = []
    
    for column, expected_type in expected_types.items():
        if column not in df.columns:
            errors.append(f"Column '{column}' not found")
            continue
            
        actual_type = str(df[column].dtype)
        if actual_type != expected_type:
            errors.append(f"Column '{column}' has type '{actual_type}', expected '{expected_type}'")
    
    return errors

def check_data_quality(df: pd.DataFrame) -> Dict[str, any]:
    """
    Perform comprehensive data quality checks.
    
    Args:
        df: DataFrame to check
        
    Returns:
        Dictionary with quality metrics
    """
    quality_report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'duplicate_rows': df.duplicated().sum(),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'data_types': df.dtypes.to_dict()
    }
    
    # Calculate missing percentage
    quality_report['missing_percentage'] = {
        col: (missing / len(df)) * 100 
        for col, missing in quality_report['missing_values'].items()
    }
    
    logger.info(f"Data quality report generated for DataFrame with {len(df)} rows")
    return quality_report
    