"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from enum import Enum

# Enums
class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(str, Enum):
    CRITICAL_HEART_RATE = "critical_heart_rate"
    CRITICAL_TEMPERATURE = "critical_temperature"
    CRITICAL_OXYGEN = "critical_oxygen"
    ANOMALY_DETECTED = "anomaly_detected"
    TREND_CHANGE = "trend_change"

# Base Models
class PatientBase(BaseModel):
    patient_name: str = Field(..., description="Patient's full name")
    date_of_birth: datetime = Field(..., description="Patient's date of birth")
    gender: Optional[str] = Field(None, description="Patient's gender")
    address: Optional[str] = Field(None, description="Patient's address")

class VitalSignBase(BaseModel):
    heart_rate: Optional[float] = Field(None, description="Heart rate in BPM")
    systolic: Optional[float] = Field(None, description="Systolic blood pressure")
    diastolic: Optional[float] = Field(None, description="Diastolic blood pressure")
    temperature: Optional[float] = Field(None, description="Body temperature in Celsius")
    respiration: Optional[int] = Field(None, description="Respiration rate")
    oxygen_saturation: Optional[float] = Field(None, description="Oxygen saturation percentage")

# Request Models
class PatientCreate(BaseModel):
    patient_name: str = Field(..., min_length=1, max_length=100, description="Patient full name")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    gender: Optional[str] = Field(None, max_length=10, description="Patient gender")
    address: Optional[str] = Field(None, max_length=255, description="Patient address")

class VitalSignCreate(VitalSignBase):
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the reading")

class MedicalHistoryCreate(BaseModel):
    patient_id: int = Field(..., description="Patient ID")
    condition: str = Field(..., description="Medical condition")
    diagnosis_date: datetime = Field(..., description="Date of diagnosis")
    notes: Optional[str] = Field(None, description="Additional notes")

# Response Models
class PatientResponse(BaseModel):
    patient_id: int = Field(..., description="Unique patient identifier")
    patient_name: str = Field(..., description="Patient full name")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    gender: Optional[str] = Field(None, description="Patient gender")
    address: Optional[str] = Field(None, description="Patient address")
    created_at: Optional[datetime] = Field(None, description="Record creation timestamp")
    
    class Config:
        from_attributes = True

class VitalSignResponse(VitalSignBase):
    vital_sign_id: Optional[int] = Field(None, description="Vital sign identifier")
    patient_id: int = Field(..., description="Patient ID")
    timestamp: datetime = Field(..., description="Timestamp of the reading")
    
    class Config:
        from_attributes = True

class MedicalHistoryResponse(BaseModel):
    medical_history_id: int = Field(..., description="Medical history identifier")
    patient_id: int = Field(..., description="Patient ID")
    condition: str = Field(..., description="Medical condition")
    diagnosis_date: datetime = Field(..., description="Date of diagnosis")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    class Config:
        from_attributes = True

class HealthAlertResponse(BaseModel):
    patient_id: int = Field(..., description="Patient ID")
    alert_type: AlertType = Field(..., description="Type of alert")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    message: str = Field(..., description="Alert message")
    timestamp: datetime = Field(..., description="Alert timestamp")
    vital_sign_value: Optional[float] = Field(None, description="Vital sign value that triggered alert")

class ForecastResponse(BaseModel):
    patient_id: int = Field(..., description="Patient ID")
    forecast_hours: int = Field(..., description="Number of hours forecasted")
    forecasts: Dict[str, Any] = Field(..., description="Forecast data for each vital sign")
    anomalies: Dict[str, Any] = Field(..., description="Anomaly detection results")
    timestamp: datetime = Field(..., description="Forecast generation timestamp")

class HealthSummaryResponse(BaseModel):
    patient_id: int = Field(..., description="Patient ID")
    summary_stats: Dict[str, Any] = Field(..., description="Summary statistics")
    recent_trends: Dict[str, Any] = Field(..., description="Recent health trends")
    alerts_count: int = Field(..., description="Number of active alerts")
    last_reading: Optional[datetime] = Field(None, description="Timestamp of last reading")

class SystemStatsResponse(BaseModel):
    total_patients: int = Field(..., description="Total number of patients")
    active_patients: int = Field(..., description="Number of active patients")
    recent_vital_readings: int = Field(..., description="Number of recent vital readings")
    api_uptime: str = Field(..., description="API uptime status")
    timestamp: datetime = Field(..., description="Stats timestamp")

class ActivePatientResponse(BaseModel):
    patient_id: int = Field(..., description="Patient ID")
    last_reading: Optional[datetime] = Field(None, description="Timestamp of last reading")
    readings_count: int = Field(..., description="Number of readings in last 24 hours")
    status: str = Field(..., description="Patient status")

class MonitoringResponse(BaseModel):
    total_patients: int = Field(..., description="Total number of patients")
    active_patients: List[ActivePatientResponse] = Field(..., description="List of active patients")
    timestamp: datetime = Field(..., description="Monitoring timestamp")

# Feature Engineering Models
class HealthMetricsResponse(BaseModel):
    patient_id: int = Field(..., description="Patient ID")
    metrics: Dict[str, Any] = Field(..., description="Calculated health metrics")
    features: Dict[str, Any] = Field(..., description="Engineered features")
    scores: Dict[str, Any] = Field(..., description="Health scores")
    timestamp: datetime = Field(..., description="Processing timestamp")

# Error Response Models
class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

class ValidationErrorResponse(BaseModel):
    detail: List[Dict[str, Any]] = Field(..., description="Validation error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

# Success Response Models
class SuccessResponse(BaseModel):
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")

# Pagination Models
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=10, ge=1, le=100, description="Page size")

class PaginatedResponse(BaseModel):
    data: List[Any] = Field(..., description="Paginated data")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")
