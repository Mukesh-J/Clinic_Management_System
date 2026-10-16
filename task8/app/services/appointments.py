from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Appointment, Doctor, DoctorAvailability, User

def book_appointment(db: Session, patient: User, payload):
    # Lock doctor row to serialize booking attempts for the same doctor on MySQL.
    doctor = db.scalar(select(Doctor).where(Doctor.id == payload.doctor_id).with_for_update())
    if not doctor or not doctor.user.is_active:
        raise HTTPException(status_code=404, detail="Active doctor not found")
    if payload.appointment_date == datetime.now().date() and payload.start_time <= datetime.now().time():
        raise HTTPException(status_code=400, detail="Appointment start time must be in the future")
    available = db.scalar(select(DoctorAvailability).where(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.available_date == payload.appointment_date,
        DoctorAvailability.is_available.is_(True),
        DoctorAvailability.start_time <= payload.start_time,
        DoctorAvailability.end_time >= payload.end_time
    ))
    if not available:
        raise HTTPException(status_code=409, detail="Requested time is outside the doctor's available schedule")
    conflict = db.scalar(select(Appointment.id).where(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_date == payload.appointment_date,
        Appointment.status.in_(["Pending", "Confirmed"]),
        Appointment.start_time < payload.end_time,
        Appointment.end_time > payload.start_time
    ).limit(1))
    if conflict:
        raise HTTPException(status_code=409, detail="This doctor already has an overlapping appointment")
    appointment = Appointment(patient_id=patient.id, doctor_id=doctor.id,
        appointment_date=payload.appointment_date, start_time=payload.start_time,
        end_time=payload.end_time, reason=payload.reason, status="Pending")
    db.add(appointment)
    try:
        db.commit()
        db.refresh(appointment)
        return appointment
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Could not reserve this slot; it may have just been booked")

def update_status(db: Session, appointment: Appointment, new_status: str):
    allowed = {
        "Pending": {"Confirmed", "Cancelled"},
        "Confirmed": {"Completed", "Cancelled"},
        "Completed": set(),
        "Cancelled": set(),
    }
    if new_status not in allowed[appointment.status]:
        raise HTTPException(status_code=409, detail=f"Invalid status transition: {appointment.status} -> {new_status}")
    appointment.status = new_status
    db.commit()
    db.refresh(appointment)
    return appointment
