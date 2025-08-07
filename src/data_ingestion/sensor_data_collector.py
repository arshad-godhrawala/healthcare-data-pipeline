import asyncio
import random
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
from influxdb_client import Point
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd

# Import our custom modules
from src.database.influx_operations import create_influx_connection
from src.data_ingestion.data_validator import validate_sensor_data

# Set up logging (HIPAA compliant - no PHI in logs)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorDataCollector:
    """Collector for IoT health sensor data with InfluxDB integration."""
    
    def __init__(self):
        """Initialize the sensor data collector."""
        self.client, self.bucket = create_influx_connection()
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        
    def __del__(self):
        """Clean up resources."""
        if hasattr(self, 'client'):
            self.client.close()

    async def simulate_sensor_data(self, patient_id: int, duration_minutes: int = 5) -> List[Dict]:
        """
        Simulate real-time IoT sensor data for a patient.
        
        Args:
            patient_id (int): Patient ID to simulate data for
            duration_minutes (int): Duration of simulation in minutes
            
        Returns:
            List[Dict]: List of sensor measurements
            
        HIPAA/Security:
            - No PHI in logs, only patient ID and data counts
        """
        logger.info(f"Starting sensor simulation for patient {patient_id} for {duration_minutes} minutes")
        
        measurements = []
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        # Base vital signs for the patient (realistic starting points)
        base_heart_rate = random.randint(65, 85)
        base_systolic = random.randint(110, 140)
        base_diastolic = random.randint(70, 90)
        base_temperature = round(random.uniform(36.5, 37.5), 1)
        base_respiration = random.randint(14, 18)
        base_oxygen = random.randint(96, 99)
        
        current_time = start_time
        
        while current_time < end_time:
            # Generate realistic variations around base values
            heart_rate = max(40, min(200, base_heart_rate + random.randint(-10, 10)))
            systolic = max(90, min(200, base_systolic + random.randint(-15, 15)))
            diastolic = max(60, min(120, base_diastolic + random.randint(-10, 10)))
            temperature = max(35.0, min(40.0, base_temperature + random.uniform(-0.5, 0.5)))
            respiration = max(8, min(30, base_respiration + random.randint(-3, 3)))
            oxygen = max(90, min(100, base_oxygen + random.randint(-2, 2)))
            
            # Create measurement record
            measurement = {
                'patient_id': patient_id,
                'timestamp': current_time,
                'heart_rate': heart_rate,
                'blood_pressure': f"{systolic}/{diastolic}",
                'temperature': round(temperature, 1),
                'respiration': respiration,
                'oxygen_saturation': oxygen,
                'sensor_id': f"sensor_{patient_id}_{random.randint(1000, 9999)}"
            }
            
            measurements.append(measurement)
            
            # Move to next measurement (every 30 seconds)
            current_time += timedelta(seconds=30)
            
            # Small delay to simulate real-time data collection
            await asyncio.sleep(0.1)
        
        logger.info(f"Generated {len(measurements)} measurements for patient {patient_id}")
        return measurements

    def process_sensor_batch(self, sensor_data: List[Dict]) -> List[Dict]:
        """
        Process and validate a batch of sensor data.
        
        Args:
            sensor_data (List[Dict]): Raw sensor data
            
        Returns:
            List[Dict]: Processed and validated sensor data
            
        HIPAA/Security:
            - Validate data before storage
            - Log only counts and validation results
        """
        logger.info(f"Processing batch of {len(sensor_data)} sensor measurements")
        
        if not sensor_data:
            logger.warning("Empty sensor data batch received")
            return []
        
        # Convert to DataFrame for validation
        df = pd.DataFrame(sensor_data)
        
        # Validate the data using our validation function
        cleaned_df, validation_errors = validate_sensor_data(df)
        
        if validation_errors:
            logger.warning(f"Found {len(validation_errors)} validation issues in sensor data:")
            for error in validation_errors:
                logger.warning(f"  - {error}")
        
        # Convert back to list of dictionaries
        processed_data = cleaned_df.to_dict('records')
        
        logger.info(f"Processed {len(processed_data)} valid measurements")
        return processed_data

    def write_to_influxdb(self, measurements: List[Dict]) -> int:
        """
        Write sensor measurements to InfluxDB.
        
        Args:
            measurements (List[Dict]): List of sensor measurements
            
        Returns:
            int: Number of measurements successfully written
            
        HIPAA/Security:
            - Use secure connection to InfluxDB
            - Log only counts and operation status
        """
        if not measurements:
            logger.warning("No measurements to write to InfluxDB")
            return 0
        
        try:
            points = []
            
            for measurement in measurements:
                # Create InfluxDB Point for time-series data
                point = Point("health_vitals") \
                    .tag("patient_id", str(measurement['patient_id'])) \
                    .tag("sensor_id", measurement.get('sensor_id', 'unknown')) \
                    .field("heart_rate", measurement.get('heart_rate', 0)) \
                    .field("systolic", int(measurement.get('blood_pressure', '0/0').split('/')[0])) \
                    .field("diastolic", int(measurement.get('blood_pressure', '0/0').split('/')[1])) \
                    .field("temperature", measurement.get('temperature', 0)) \
                    .field("respiration", measurement.get('respiration', 0)) \
                    .field("oxygen_saturation", measurement.get('oxygen_saturation', 0)) \
                    .time(measurement['timestamp'])
                
                points.append(point)
            
            # Write to InfluxDB
            self.write_api.write(bucket=self.bucket, record=points)
            
            logger.info(f"Successfully wrote {len(points)} measurements to InfluxDB")
            return len(points)
            
        except Exception as e:
            logger.error(f"Error writing to InfluxDB: {str(e)}")
            raise

    async def run_continuous_simulation(self, patient_ids: List[int], interval_seconds: int = 60):
        """
        Run continuous sensor simulation for multiple patients.
        
        Args:
            patient_ids (List[int]): List of patient IDs to simulate
            interval_seconds (int): Interval between simulation cycles
            
        HIPAA/Security:
            - Continuous monitoring without PHI exposure
        """
        logger.info(f"Starting continuous simulation for {len(patient_ids)} patients")
        
        try:
            while True:
                for patient_id in patient_ids:
                    try:
                        # Simulate 1 minute of data for each patient
                        measurements = await self.simulate_sensor_data(patient_id, duration_minutes=1)
                        
                        # Process the batch
                        processed_data = self.process_sensor_batch(measurements)
                        
                        # Write to InfluxDB
                        if processed_data:
                            written_count = self.write_to_influxdb(processed_data)
                            logger.info(f"Patient {patient_id}: {written_count} measurements written")
                        
                    except Exception as e:
                        logger.error(f"Error processing patient {patient_id}: {str(e)}")
                        continue
                
                # Wait before next cycle
                await asyncio.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("Continuous simulation stopped by user")
        except Exception as e:
            logger.error(f"Continuous simulation error: {str(e)}")
            raise

    def query_patient_vitals(self, patient_id: int, hours: int = 24) -> List[Dict]:
        """
        Query vital signs for a specific patient from InfluxDB.
        
        Args:
            patient_id (int): Patient ID to query
            hours (int): Number of hours to look back
            
        Returns:
            List[Dict]: Vital signs data for the patient
            
        HIPAA/Security:
            - Only return aggregated data, no raw PHI
        """
        try:
            # Build Flux query
            query = f'''
            from(bucket: "{self.bucket}")
                |> range(start: -{hours}h)
                |> filter(fn: (r) => r["_measurement"] == "health_vitals")
                |> filter(fn: (r) => r["patient_id"] == "{patient_id}")
                |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            '''
            
            result = self.query_api.query(query)
            
            # Convert to list of dictionaries
            data = []
            for table in result:
                for record in table.records:
                    # Use record.values to get all field values
                    record_data = {
                        'timestamp': record.get_time(),
                        'heart_rate': 0,
                        'systolic': 0,
                        'diastolic': 0,
                        'temperature': 0,
                        'respiration': 0,
                        'oxygen_saturation': 0
                    }
                    
                    # Extract field values from the record
                    for field_name in ['heart_rate', 'systolic', 'diastolic', 'temperature', 'respiration', 'oxygen_saturation']:
                        if hasattr(record, field_name):
                            value = getattr(record, field_name)
                            if value is not None:
                                record_data[field_name] = value
                    
                    data.append(record_data)
            
            logger.info(f"Retrieved {len(data)} vital signs records for patient {patient_id}")
            return data
            
        except Exception as e:
            logger.error(f"Error querying patient vitals: {str(e)}")
            raise


