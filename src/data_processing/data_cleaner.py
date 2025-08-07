import pandas as pd
import numpy as np
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_missing_vitals(df: pd.DataFrame, strategy: str = 'ffill') -> pd.DataFrame:
    """
    Handle missing values in vital signs data.
    Args:
        df (pd.DataFrame): DataFrame with vital signs
        strategy (str): Imputation strategy ('ffill', 'bfill', 'mean', 'drop')
    Returns:
        pd.DataFrame: DataFrame with missing values handled
    """
    df_clean = df.copy()
    vital_cols = ['heart_rate', 'blood_pressure', 'temperature', 'respiration', 'oxygen_saturation']
    for col in vital_cols:
        if col in df_clean.columns:
            if strategy == 'ffill':
                df_clean[col] = df_clean[col].fillna(method='ffill')
            elif strategy == 'bfill':
                df_clean[col] = df_clean[col].fillna(method='bfill')
            elif strategy == 'mean':
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
            elif strategy == 'drop':
                df_clean = df_clean[df_clean[col].notna()]
    logger.info(f"Missing values handled using strategy: {strategy}")
    return df_clean

def detect_outliers_iqr(df: pd.DataFrame, column: str, factor: float = 1.5) -> pd.DataFrame:
    """
    Detect outliers in a column using the IQR method.
    Args:
        df (pd.DataFrame): DataFrame
        column (str): Column to check for outliers
        factor (float): IQR multiplier (default 1.5)
    Returns:
        pd.DataFrame: DataFrame with an extra column '<column>_is_outlier'
    """
    if column not in df.columns:
        logger.warning(f"Column '{column}' not found in DataFrame")
        return df
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - factor * IQR
    upper_bound = Q3 + factor * IQR
    df_out = df.copy()
    df_out[f'{column}_is_outlier'] = (df_out[column] < lower_bound) | (df_out[column] > upper_bound)
    logger.info(f"Outlier detection complete for column '{column}'. Outliers found: {df_out[f'{column}_is_outlier'].sum()}")
    return df_out

def create_health_features(df: pd.DataFrame, window: int = 3) -> pd.DataFrame:
    """
    Create derived health features (e.g., moving averages, deltas, flags).
    Args:
        df (pd.DataFrame): DataFrame with vital signs
        window (int): Window size for rolling features
    Returns:
        pd.DataFrame: DataFrame with new features
    """
    df_feat = df.copy()
    # Moving averages
    for col in ['heart_rate', 'temperature', 'respiration', 'oxygen_saturation']:
        if col in df_feat.columns:
            df_feat[f'{col}_ma{window}'] = df_feat[col].rolling(window=window, min_periods=1).mean()
    # Heart rate delta
    if 'heart_rate' in df_feat.columns:
        df_feat['heart_rate_delta'] = df_feat['heart_rate'].diff()
    # Fever flag
    if 'temperature' in df_feat.columns:
        df_feat['fever_flag'] = df_feat['temperature'] > 37.5
    logger.info(f"Created health features with rolling window: {window}")
    return df_feat
   
    
