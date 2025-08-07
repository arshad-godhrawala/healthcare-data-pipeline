import pandas as pd
import numpy as np
from src.data_processing.data_cleaner import handle_missing_vitals, detect_outliers_iqr, create_health_features

def test_handle_missing_vitals():
    print("\n=== Testing handle_missing_vitals ===")
    data = {
        'heart_rate': [72, np.nan, 80, 76, np.nan, 90],
        'temperature': [36.8, 37.1, np.nan, 38.0, 37.2, np.nan],
        'respiration': [16, 18, 17, np.nan, 15, 16],
        'oxygen_saturation': [98, 97, np.nan, 99, 96, 97]
    }
    df = pd.DataFrame(data)
    print("Original Data:")
    print(df)
    df_filled = handle_missing_vitals(df, strategy='mean')
    print("\nAfter mean imputation:")
    print(df_filled)
    df_ffill = handle_missing_vitals(df, strategy='ffill')
    print("\nAfter forward fill:")
    print(df_ffill)
    df_drop = handle_missing_vitals(df, strategy='drop')
    print("\nAfter dropping missing:")
    print(df_drop)

def test_detect_outliers_iqr():
    print("\n=== Testing detect_outliers_iqr ===")
    data = {
        'heart_rate': [72, 75, 80, 76, 200, 90, 74, 73, 300, 77]
    }
    df = pd.DataFrame(data)
    print("Original Data:")
    print(df)
    df_out = detect_outliers_iqr(df, 'heart_rate')
    print("\nWith outlier flag:")
    print(df_out)
    print(f"Outliers detected: {df_out['heart_rate_is_outlier'].sum()}")

def test_create_health_features():
    print("\n=== Testing create_health_features ===")
    data = {
        'heart_rate': [72, 75, 80, 76, 90, 74, 73, 77],
        'temperature': [36.8, 37.1, 37.6, 38.0, 37.2, 36.9, 37.0, 37.3],
        'respiration': [16, 18, 17, 16, 15, 16, 17, 18],
        'oxygen_saturation': [98, 97, 99, 99, 96, 97, 98, 99]
    }
    df = pd.DataFrame(data)
    print("Original Data:")
    print(df)
    df_feat = create_health_features(df, window=3)
    print("\nWith health features:")
    print(df_feat)

def run_all_tests():
    test_handle_missing_vitals()
    test_detect_outliers_iqr()
    test_create_health_features()
    print("\nAll data cleaning tests completed.")

if __name__ == "__main__":
    run_all_tests() 