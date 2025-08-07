"""
Time Series Forecasting for Healthcare Data
Implements health trend prediction and anomaly detection using Prophet.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
from prophet import Prophet
from src.data_ingestion.sensor_data_collector import SensorDataCollector
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_health_forecaster():
    """Create and return a HealthForecaster instance."""
    return HealthForecaster()

class HealthForecaster:
    """
    Time series forecasting for healthcare data using Prophet and anomaly detection.
    """
    
    def __init__(self):
        """Initialize the health forecaster."""
        self.sensor_collector = SensorDataCollector()
        self.models = {}  # To store trained Prophet models
        self.anomaly_detectors = {}  # To store IsolationForest models
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        
    def prepare_data_for_prophet(self, df: pd.DataFrame, vital_sign: str) -> pd.DataFrame:
        """
        Prepare data for Prophet forecasting.
        
        Args:
            df: DataFrame with timestamp and value columns
            value_column: Name of the value column to forecast
            
        Returns:
            DataFrame formatted for Prophet (ds, y columns)
        """
        try:
            # Prophet requires 'ds' (date) and 'y' (value) columns
            prophet_df = df[['timestamp', vital_sign]].copy()
            prophet_df.columns = ['ds', 'y']
            
            # Remove missing values
            prophet_df = prophet_df.dropna()
            
            # Ensure datetime format
            prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
            
            return prophet_df
            
        except Exception as e:
            logger.error(f"Error preparing data for Prophet: {e}")
            return pd.DataFrame()
    
    def train_health_model(self, df: pd.DataFrame, vital_sign: str, 
                          forecast_periods: int = 24) -> Dict:
        """
        Train a Prophet model for a specific vital sign.
        
        Args:
            df: DataFrame with health data
            vital_sign: Name of the vital sign to forecast
            forecast_periods: Number of periods to forecast
            
        Returns:
            Dictionary with model results and forecasts
        """
        try:
            logger.info(f"Training Prophet model for {vital_sign}")
            
            # Prepare data for Prophet
            prophet_df = self.prepare_data_for_prophet(df, vital_sign)
            
            if len(prophet_df) < 10:
                logger.warning(f"Insufficient data for {vital_sign} forecasting")
                return {}
            
            # Initialize and fit Prophet model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=True,
                seasonality_mode='multiplicative'
            )
            
            # Add custom seasonality for healthcare patterns
            model.add_seasonality(name='hourly', period=1, fourier_order=5)
            model.add_seasonality(name='daily', period=24, fourier_order=10)
            model.add_seasonality(name='weekly', period=168, fourier_order=10)
            
            # Fit the model
            model.fit(prophet_df)
            
            # Make future predictions
            future = model.make_future_dataframe(periods=forecast_periods, freq='H')
            forecast = model.predict(future)
            
            # Store model
            self.models[vital_sign] = model
            
            # Calculate metrics
            metrics = self._calculate_forecast_metrics(prophet_df, forecast)
            
            results = {
                'model': model,
                'forecast': forecast,
                'metrics': metrics,
                'vital_sign': vital_sign,
                'forecast_periods': forecast_periods
            }
            
            logger.info(f"Successfully trained model for {vital_sign}")
            return results
            
        except Exception as e:
            logger.error(f"Error training model for {vital_sign}: {e}")
            return {}
    
    def _calculate_forecast_metrics(self, actual: pd.DataFrame, forecast: pd.DataFrame) -> Dict:
        """Calculate forecast accuracy metrics."""
        try:
            # Merge actual and forecast data
            merged = pd.merge(actual, forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], on='ds')
            
            # Calculate metrics
            mae = np.mean(np.abs(merged['y'] - merged['yhat']))
            mape = np.mean(np.abs((merged['y'] - merged['yhat']) / merged['y'])) * 100
            
            return {
                'mae': mae,
                'mape': mape,
                'data_points': len(merged)
            }
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {}
    
    def detect_anomalies(self, df: pd.DataFrame, vital_signs: List[str]) -> Dict:
        """
        Detect anomalies in vital signs using Isolation Forest.
        
        Args:
            df: DataFrame with health data
            vital_signs: List of vital signs to check for anomalies
            
        Returns:
            Dictionary with anomaly detection results
        """
        try:
            logger.info("Detecting anomalies in vital signs")
            
            anomalies = {}
            
            for vital_sign in vital_signs:
                if vital_sign not in df.columns:
                    continue
                
                # Prepare data for anomaly detection
                data = df[vital_sign].dropna().values.reshape(-1, 1)
                
                if len(data) < 10:
                    continue
                
                # Fit anomaly detector
                self.anomaly_detector.fit(data)
                
                # Predict anomalies
                predictions = self.anomaly_detector.predict(data)
                
                # Get anomaly indices
                anomaly_indices = np.where(predictions == -1)[0]
                
                anomalies[vital_sign] = {
                    'anomaly_count': len(anomaly_indices),
                    'anomaly_percentage': (len(anomaly_indices) / len(data)) * 100,
                    'anomaly_values': data[anomaly_indices].flatten().tolist(),
                    'anomaly_timestamps': df.iloc[anomaly_indices]['timestamp'].tolist() if 'timestamp' in df.columns else []
                }
            
            logger.info(f"Detected anomalies in {len(anomalies)} vital signs")
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return {}
    
    def forecast_patient_health(self, patient_id: int, vital_signs: List[str], 
                              forecast_hours: int = 24) -> Dict:
        """
        Forecast health trends for a specific patient.
        
        Args:
            patient_id: Patient ID
            vital_signs: List of vital signs to forecast
            forecast_hours: Number of hours to forecast
            
        Returns:
            Dictionary with forecast results
        """
        try:
            logger.info(f"Forecasting health trends for patient {patient_id}")
            
            # This would typically get data from InfluxDB
            # For now, we'll use sample data
            sample_data = self._generate_sample_patient_data(patient_id)
            
            forecasts = {}
            anomalies = {}
            
            # Train models and get forecasts for each vital sign
            for vital_sign in vital_signs:
                if vital_sign in sample_data.columns:
                    # Train model
                    model_results = self.train_health_model(sample_data, vital_sign, forecast_hours)
                    
                    if model_results:
                        forecasts[vital_sign] = {
                            'forecast': model_results['forecast'].tail(forecast_hours).to_dict('records'),
                            'metrics': model_results['metrics']
                        }
            
            # Detect anomalies
            anomalies = self.detect_anomalies(sample_data, vital_signs)
            
            results = {
                'patient_id': patient_id,
                'forecasts': forecasts,
                'anomalies': anomalies,
                'forecast_hours': forecast_hours,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Completed forecasting for patient {patient_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error forecasting for patient {patient_id}: {e}")
            return {}
    
    def _generate_sample_patient_data(self, patient_id: int) -> pd.DataFrame:
        """Generate sample patient data for testing."""
        # Create sample time series data
        dates = pd.date_range(start='2025-01-01', end='2025-01-31', freq='H')
        
        data = {
            'timestamp': dates,
            'heart_rate': 70 + 10 * np.sin(np.arange(len(dates)) * 0.1) + np.random.normal(0, 5, len(dates)),
            'temperature': 37 + 0.5 * np.sin(np.arange(len(dates)) * 0.05) + np.random.normal(0, 0.2, len(dates)),
            'oxygen_saturation': 98 + 1 * np.sin(np.arange(len(dates)) * 0.02) + np.random.normal(0, 0.5, len(dates)),
            'systolic': 120 + 10 * np.sin(np.arange(len(dates)) * 0.08) + np.random.normal(0, 8, len(dates)),
            'diastolic': 80 + 5 * np.sin(np.arange(len(dates)) * 0.08) + np.random.normal(0, 5, len(dates))
        }
        
        return pd.DataFrame(data)
    
    def get_health_trends(self, df: pd.DataFrame, vital_signs: List[str]) -> Dict:
        """
        Analyze health trends and patterns.
        
        Args:
            df: DataFrame with health data
            vital_signs: List of vital signs to analyze
            
        Returns:
            Dictionary with trend analysis results
        """
        try:
            logger.info("Analyzing health trends")
            
            trends = {}
            
            for vital_sign in vital_signs:
                if vital_sign not in df.columns:
                    continue
                
                data = df[vital_sign].dropna()
                
                if len(data) < 10:
                    continue
                
                # Calculate trend metrics
                trend_analysis = {
                    'mean': data.mean(),
                    'std': data.std(),
                    'min': data.min(),
                    'max': data.max(),
                    'trend_direction': 'increasing' if data.iloc[-1] > data.iloc[0] else 'decreasing',
                    'volatility': data.std() / data.mean() if data.mean() != 0 else 0,
                    'data_points': len(data)
                }
                
                # Detect trend changes
                trend_changes = self._detect_trend_changes(data)
                trend_analysis['trend_changes'] = trend_changes
                
                trends[vital_sign] = trend_analysis
            
            logger.info(f"Analyzed trends for {len(trends)} vital signs")
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {}
    
    def _detect_trend_changes(self, data: pd.Series) -> List[Dict]:
        """Detect significant trend changes in the data."""
        try:
            changes = []
            
            # Simple trend change detection using rolling windows
            window_size = min(10, len(data) // 4)
            
            if window_size < 3:
                return changes
            
            # Calculate rolling means
            rolling_mean = data.rolling(window=window_size).mean()
            
            # Detect changes in trend
            for i in range(window_size, len(data) - window_size):
                before_mean = rolling_mean.iloc[i-window_size:i].mean()
                after_mean = rolling_mean.iloc[i:i+window_size].mean()
                
                change_threshold = data.std() * 0.5
                
                if abs(after_mean - before_mean) > change_threshold:
                    changes.append({
                        'timestamp': data.index[i] if hasattr(data.index[i], 'isoformat') else str(i),
                        'change_magnitude': after_mean - before_mean,
                        'before_value': before_mean,
                        'after_value': after_mean
                    })
            
            return changes
            
        except Exception as e:
            logger.error(f"Error detecting trend changes: {e}")
            return [] 