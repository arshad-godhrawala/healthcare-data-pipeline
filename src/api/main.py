"""
Main FastAPI application for Healthcare Pipeline API.
Provides REST endpoints for health monitoring, data processing, and forecasting.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import logging
import asyncio
from datetime import datetime, timedelta
import uvicorn

# Import our modules
from src.api.schemas import (
    PatientResponse, VitalSignResponse, HealthAlertResponse,
    ForecastResponse, PatientCreate, VitalSignCreate
)
from src.data_ingestion.patient_data_loader import get_patient_count
from src.data_ingestion.sensor_data_collector import SensorDataCollector
from src.data_processing.aggregator import get_patient_summary_stats
from src.data_processing.feature_engineer import process_patient_features
from src.forecasting.health_forecaster import create_health_forecaster

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare Pipeline API",
    description="Real-time health monitoring and forecasting API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
sensor_collector = SensorDataCollector()
health_forecaster = create_health_forecaster()

@app.on_event("startup")
async def startup_event():
    """Initialize API on startup."""
    logger.info("🚀 Healthcare Pipeline API starting up...")
    logger.info("✅ API initialized successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Healthcare Pipeline API shutting down...")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Patient endpoints
@app.get("/patients", response_model=List[PatientResponse], tags=["Patients"])
async def get_patients():
    """Get all patients."""
    try:
        from src.data_ingestion.patient_data_loader import get_all_patients
        patients = get_all_patients()
        return patients
    except Exception as e:
        logger.error(f"Error getting patients: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve patients")

@app.get("/patients/{patient_id}", response_model=PatientResponse, tags=["Patients"])
async def get_patient(patient_id: int):
    """Get a specific patient by ID."""
    try:
        from src.data_ingestion.patient_data_loader import get_patient_by_id
        patient = get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve patient")

@app.post("/patients", response_model=PatientResponse, tags=["Patients"])
async def create_patient(patient: PatientCreate):
    """Create a new patient."""
    try:
        from src.data_ingestion.patient_data_loader import create_patient_record
        
        # Convert date to string if it exists
        date_str = None
        if patient.date_of_birth:
            date_str = patient.date_of_birth.strftime('%Y-%m-%d')
        
        new_patient = create_patient_record({
            "patient_name": patient.patient_name,
            "date_of_birth": date_str,
            "gender": patient.gender,
            "address": patient.address
        })
        return new_patient
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create patient: {str(e)}")

# Vital signs endpoints
@app.get("/patients/{patient_id}/vitals", response_model=List[VitalSignResponse], tags=["Vital Signs"])
async def get_patient_vitals(patient_id: int, hours: int = 24):
    """Get vital signs for a specific patient."""
    try:
        from src.data_ingestion.patient_data_loader import get_patient_vitals_from_db
        from src.api.schemas import VitalSignResponse
        
        logger.info(f"Getting vitals for patient {patient_id}")
        vitals = get_patient_vitals_from_db(patient_id, hours)
        logger.info(f"Retrieved {len(vitals)} vitals for patient {patient_id}")
        
        if vitals:
            logger.info(f"Sample vital: {vitals[0]}")
            
            # Convert to response models
            response_models = []
            for vital in vitals:
                try:
                    response = VitalSignResponse(**vital)
                    response_models.append(response)
                except Exception as e:
                    logger.error(f"Error converting vital: {e}")
            
            logger.info(f"Successfully converted {len(response_models)} vitals to response models")
            return response_models
        else:
            logger.info("No vitals found for patient")
            return []
            
    except Exception as e:
        logger.error(f"Error getting vitals for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve vital signs")

@app.get("/patients/{patient_id}/vitals-raw", tags=["Vital Signs"])
async def get_patient_vitals_raw(patient_id: int, hours: int = 24):
    """Get vital signs for a specific patient (raw response without model validation)."""
    try:
        from src.data_ingestion.patient_data_loader import get_patient_vitals_from_db
        logger.info(f"Getting vitals for patient {patient_id} (raw)")
        vitals = get_patient_vitals_from_db(patient_id, hours)
        logger.info(f"Retrieved {len(vitals)} vitals for patient {patient_id}")
        return vitals
    except Exception as e:
        logger.error(f"Error getting vitals for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve vital signs")

@app.post("/patients/{patient_id}/vitals", response_model=VitalSignResponse, tags=["Vital Signs"])
async def add_vital_sign(patient_id: int, vital_sign: VitalSignCreate):
    """Add a new vital sign reading."""
    try:
        # Convert to sensor data format
        sensor_data = {
            'patient_id': patient_id,
            'timestamp': vital_sign.timestamp,
            'heart_rate': vital_sign.heart_rate,
            'systolic': vital_sign.systolic,
            'diastolic': vital_sign.diastolic,
            'temperature': vital_sign.temperature,
            'respiration': vital_sign.respiration,
            'oxygen_saturation': vital_sign.oxygen_saturation
        }
        
        # Process and write to InfluxDB
        try:
            processed_data = sensor_collector.process_sensor_batch([sensor_data])
            if processed_data:
                sensor_collector.write_to_influxdb(processed_data)
                logger.info(f"Successfully added vital sign for patient {patient_id}")
            else:
                logger.warning(f"No processed data for patient {patient_id}")
        except Exception as e:
            logger.error(f"Error processing vital sign data: {e}")
            # Continue anyway to return the vital sign data
        
        # Return the vital sign data
        return VitalSignResponse(
            vital_sign_id=None,
            patient_id=patient_id,
            timestamp=vital_sign.timestamp,
            heart_rate=vital_sign.heart_rate,
            systolic=vital_sign.systolic,
            diastolic=vital_sign.diastolic,
            temperature=vital_sign.temperature,
            respiration=vital_sign.respiration,
            oxygen_saturation=vital_sign.oxygen_saturation
        )
    except Exception as e:
        logger.error(f"Error adding vital sign for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to add vital sign")

# Health monitoring endpoints
@app.get("/patients/{patient_id}/health-summary", tags=["Health Monitoring"])
async def get_health_summary(patient_id: int):
    """Get health summary for a patient."""
    try:
        summary = get_patient_summary_stats(patient_id)
        return summary
    except Exception as e:
        logger.error(f"Error getting health summary for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve health summary")

@app.get("/patients/{patient_id}/alerts", response_model=List[HealthAlertResponse], tags=["Health Monitoring"])
async def get_health_alerts(patient_id: int):
    """Get health alerts for a patient."""
    try:
        # Get recent vitals
        vitals = sensor_collector.query_patient_vitals(patient_id, hours=1)
        
        alerts = []
        for vital in vitals:
            # Check for critical values
            if vital.heart_rate and (vital.heart_rate < 50 or vital.heart_rate > 120):
                alerts.append(HealthAlertResponse(
                    patient_id=patient_id,
                    alert_type="critical_heart_rate",
                    severity="high",
                    message=f"Heart rate critical: {vital.heart_rate}",
                    timestamp=vital.timestamp
                ))
            
            if vital.temperature and (vital.temperature < 35 or vital.temperature > 39):
                alerts.append(HealthAlertResponse(
                    patient_id=patient_id,
                    alert_type="critical_temperature",
                    severity="high",
                    message=f"Temperature critical: {vital.temperature}",
                    timestamp=vital.timestamp
                ))
        
        return alerts
    except Exception as e:
        logger.error(f"Error getting alerts for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")

# Forecasting endpoints
@app.get("/patients/{patient_id}/forecast", response_model=ForecastResponse, tags=["Forecasting"])
async def get_health_forecast(patient_id: int, hours: int = 24):
    """Get health forecast for a patient."""
    try:
        forecast_results = health_forecaster.forecast_patient_health(
            patient_id=patient_id,
            vital_signs=['heart_rate', 'temperature', 'oxygen_saturation'],
            forecast_hours=hours
        )
        
        if not forecast_results:
            raise HTTPException(status_code=404, detail="No forecast data available")
        
        return ForecastResponse(
            patient_id=patient_id,
            forecast_hours=hours,
            forecasts=forecast_results.get('forecasts', {}),
            anomalies=forecast_results.get('anomalies', {}),
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting forecast for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate forecast")

# Real-time monitoring endpoints
@app.get("/monitoring/active-patients", tags=["Real-time Monitoring"])
async def get_active_patients():
    """Get list of patients with recent activity."""
    try:
        # Get patient count
        patient_count = get_patient_count()
        
        # Get recent activity (last 24 hours)
        active_patients = []
        for patient_id in range(1, min(patient_count + 1, 11)):  # Limit to 10 patients for demo
            try:
                vitals = sensor_collector.query_patient_vitals(patient_id, hours=24)
                if vitals:
                    active_patients.append({
                        "patient_id": patient_id,
                        "last_reading": vitals[-1].timestamp if vitals else None,
                        "readings_count": len(vitals)
                    })
            except Exception as e:
                logger.warning(f"Error getting vitals for patient {patient_id}: {e}")
                continue
        
        return {
            "total_patients": patient_count,
            "active_patients": active_patients,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting active patients: {e}")
        # Return empty response instead of raising error
        return {
            "total_patients": 0,
            "active_patients": [],
            "timestamp": datetime.now().isoformat(),
            "error": "Unable to retrieve active patients"
        }

# Data processing endpoints
@app.post("/patients/{patient_id}/process-features", tags=["Data Processing"])
async def process_patient_features_endpoint(patient_id: int, days: int = 7):
    """Process features for a specific patient."""
    try:
        features = process_patient_features(patient_id, days)
        return features
    except Exception as e:
        logger.error(f"Error processing features for patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process features")

# System endpoints
@app.get("/system/stats", tags=["System"])
async def get_system_stats():
    """Get system statistics."""
    try:
        patient_count = get_patient_count()
        
        # Get recent data counts
        recent_vitals = 0
        for patient_id in range(1, min(patient_count + 1, 6)):
            try:
                vitals = sensor_collector.query_patient_vitals(patient_id, hours=1)
                recent_vitals += len(vitals)
            except Exception as e:
                logger.warning(f"Error getting vitals for patient {patient_id}: {e}")
                continue
        
        return {
            "total_patients": patient_count,
            "recent_vital_readings": recent_vitals,
            "api_uptime": "running",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        # Return default response instead of raising error
        return {
            "total_patients": 0,
            "recent_vital_readings": 0,
            "api_uptime": "running",
            "timestamp": datetime.now().isoformat(),
            "error": "Unable to retrieve complete system stats"
        }

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
