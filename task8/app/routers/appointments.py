from datetime import datetime,date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models import Appointment, Doctor, User
from app.schemas import AppointmentCreate, AppointmentOut, AppointmentStatusUpdate, AppointmentDetail
from app.services.appointments import book_appointment, update_status

router = APIRouter(prefix="/appointments", tags=["Appointments"])

def detail(a: Appointment):
    return {"id": a.id, "patient_id": a.patient_id, "doctor_id": a.doctor_id,
        "appointment_date": a.appointment_date, "start_time": a.start_time, "end_time": a.end_time,
        "reason": a.reason, "status": a.status, "created_at": a.created_at,
        "patient_name": a.patient.name, "patient_email": a.patient.email,
        "doctor_name": a.doctor.user.name, "specialization": a.doctor.specialization}

@router.post("", response_model=AppointmentOut, status_code=201)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db),
                       user: User = Depends(require_roles("patient"))):
    return book_appointment(db, user, payload)

@router.get("", response_model=list[AppointmentDetail])
def list_appointments(date_filter:date | None = Query(None, alias="date"),
                      status_filter: str | None = Query(None, alias="status", pattern="^(Pending|Confirmed|Completed|Cancelled)$"),
                      db: Session = Depends(get_db), user: User = Depends(get_current_user),
                      page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    q = db.query(Appointment).options(joinedload(Appointment.patient), joinedload(Appointment.doctor).joinedload(Doctor.user))
    if user.role == "patient":
        q = q.filter(Appointment.patient_id == user.id)
    elif user.role == "doctor":
        doctor = db.query(Doctor).filter(Doctor.user_id == user.id).first()
        if not doctor:
            return []
        q = q.filter(Appointment.doctor_id == doctor.id)
    if date_filter:
        q = q.filter(Appointment.appointment_date == date_filter)
    if status_filter:
        q = q.filter(Appointment.status == status_filter)
    rows = q.order_by(Appointment.appointment_date.desc(), Appointment.start_time).offset((page-1)*page_size).limit(page_size).all()
    return [detail(a) for a in rows]

@router.get("/{appointment_id}", response_model=AppointmentDetail)
def get_appointment(appointment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    a = db.query(Appointment).options(joinedload(Appointment.patient), joinedload(Appointment.doctor).joinedload(Doctor.user)).filter(Appointment.id == appointment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if user.role == "patient" and a.patient_id != user.id:
        raise HTTPException(status_code=403, detail="You cannot view another patient's appointment")
    if user.role == "doctor":
        doctor = db.query(Doctor).filter(Doctor.user_id == user.id).first()
        if not doctor or a.doctor_id != doctor.id:
            raise HTTPException(status_code=403, detail="This appointment is not assigned to you")
    return detail(a)

@router.patch("/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db),
                       user: User = Depends(require_roles("patient"))):
    a = db.get(Appointment, appointment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if a.patient_id != user.id:
        raise HTTPException(status_code=403, detail="You cannot cancel another patient's appointment")
    if a.appointment_date < datetime.now().date() or (a.appointment_date == datetime.now().date() and a.start_time <= datetime.now().time()):
        raise HTTPException(status_code=409, detail="An appointment that has started cannot be cancelled")
    return update_status(db, a, "Cancelled")

@router.patch("/{appointment_id}/status", response_model=AppointmentOut)
def change_status(appointment_id: int, payload: AppointmentStatusUpdate, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    if user.role not in ("doctor", "admin"):
        raise HTTPException(status_code=403, detail="Only the assigned doctor or admin can update appointment status")
    a = db.get(Appointment, appointment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if user.role == "doctor":
        doctor = db.query(Doctor).filter(Doctor.user_id == user.id).first()
        if not doctor or doctor.id != a.doctor_id:
            raise HTTPException(status_code=403, detail="This appointment is not assigned to you")
    if payload.status == "Cancelled" and user.role == "doctor" and a.appointment_date < datetime.now().date():
        raise HTTPException(status_code=409, detail="Past appointments cannot be cancelled")
    return update_status(db, a, payload.status)
