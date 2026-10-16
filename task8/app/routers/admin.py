from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_roles
from app.models import User, Doctor, Appointment
from app.schemas import DoctorCreate, DoctorUpdate, DoctorOut

router = APIRouter(prefix="/admin", tags=["Administration"])

def doctor_out(d: Doctor):
    return {"id": d.id, "user_id": d.user_id, "specialization": d.specialization,
            "consultation_fee": d.consultation_fee, "experience_years": d.experience_years,
            "name": d.user.name, "email": d.user.email, "is_active": d.user.is_active}

@router.post("/doctors", response_model=DoctorOut, status_code=201)
def create_doctor(payload: DoctorCreate, db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    email = str(payload.email).lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email is already registered")
    from app.core.security import hash_password
    user = User(name=payload.name.strip(), email=email, password_hash=hash_password(payload.password), role="doctor")
    db.add(user)
    db.flush()
    doctor = Doctor(user_id=user.id, specialization=payload.specialization, consultation_fee=payload.consultation_fee, experience_years=payload.experience_years)
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor_out(doctor)

@router.patch("/doctors/{doctor_id}", response_model=DoctorOut)
def update_doctor(doctor_id: int, payload: DoctorUpdate, db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    d = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(d, key, value)
    db.commit()
    db.refresh(d)
    return doctor_out(d)

@router.patch("/doctors/{doctor_id}/deactivate")
def deactivate_doctor(doctor_id: int, db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    d = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    d.user.is_active = False
    db.commit()
    return {"message": "Doctor account deactivated", "doctor_id": doctor_id}

@router.get("/statistics")
def statistics(db: Session = Depends(get_db), _: User = Depends(require_roles("admin"))):
    total_doctors = db.query(func.count(Doctor.id)).scalar() or 0
    total_patients = db.query(func.count(User.id)).filter(User.role == "patient").scalar() or 0
    total_appointments = db.query(func.count(Appointment.id)).scalar() or 0
    grouped = db.query(Appointment.status, func.count(Appointment.id)).group_by(Appointment.status).all()
    daily = db.query(Appointment.appointment_date, func.count(Appointment.id)).group_by(Appointment.appointment_date).order_by(Appointment.appointment_date.desc()).limit(30).all()
    return {"total_doctors": total_doctors, "total_patients": total_patients,
            "total_appointments": total_appointments,
            "appointments_by_status": {status: count for status, count in grouped},
            "daily_appointment_counts": [{"date": str(day), "count": count} for day, count in daily]}
