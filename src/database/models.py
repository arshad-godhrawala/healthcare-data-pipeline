from sqlalchemy import Column, Integer, String, Date, Float, Text, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    patient_id = Column(Integer, primary_key=True)
    patient_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10))
    address = Column(String(255))
    created_at = Column(TIMESTAMP)

    vital_signs = relationship("VitalSign", back_populates="patient")
    medical_history = relationship("MedicalHistory", back_populates="patient")

class VitalSign(Base):
    __tablename__ = "vital_signs"
    vital_sign_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    timestamp = Column(TIMESTAMP, nullable=False)
    heart_rate = Column(Float)
    blood_pressure = Column(String(20))
    temperature = Column(Float)
    respiration_rate = Column(Integer)

    patient = relationship("Patient", back_populates="vital_signs")

class MedicalHistory(Base):
    __tablename__ = "medical_history"
    medical_history_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"))
    condition = Column(String(100))
    diagnosis_date = Column(Date)
    notes = Column(Text)

    patient = relationship("Patient", back_populates="medical_history")