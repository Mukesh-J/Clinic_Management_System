from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, asc, desc
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.models import Doctor, DoctorAvailability, User
from app.schemas import DoctorOut, AvailabilityCreate, AvailabilityOut

router = APIRouter(prefix="/doctors", tags=["Doctors"])

def doctor_out(d: Doctor):
    return {"id": d.id, "user_id": d.user_id, "specialization": d.specialization,
            "consultation_fee": d.consultation_fee, "experience_years": d.experience_years,
            "name": d.user.name, "email": d.user.email, "is_active": d.user.is_active}

@router.get("", response_model=list[DoctorOut])
def list_doctors(specialization: str | None = None, search: str | None = None,
                 sort_by: str = Query("experience", pattern="^(experience|fee|name)$"),
                 order: str = Query("desc", pattern="^(asc|desc)$"),
                 page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100),
                 db: Session = Depends(get_db)):
    q = db.query(Doctor).join(User).filter(User.is_active.is_(True))
    if specialization:
        q = q.filter(Doctor.specialization.ilike(f"%{specialization}%"))
    if search:
        q = q.filter(or_(User.name.ilike(f"%{search}%"), Doctor.specialization.ilike(f"%{search}%")))
    col = {"experience": Doctor.experience_years, "fee": Doctor.consultation_fee, "name": User.name}[sort_by]
    q = q.order_by(asc(col) if order == "asc" else desc(col))
    return [doctor_out(d) for d in q.offset((page-1)*page_size).limit(page_size).all()]

@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    d = db.query(Doctor).join(User).filter(Doctor.id == doctor_id, User.is_active.is_(True)).first()
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor_out(d)

@router.post("/me/availability", response_model=AvailabilityOut, status_code=201)
def add_availability(payload: AvailabilityCreate, db: Session = Depends(get_db),
                     user: User = Depends(require_roles("doctor"))):
    doctor = db.query(Doctor).filter(Doctor.user_id == user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    if payload.available_date == __import__("datetime").date.today() and payload.start_time <= __import__("datetime").datetime.now().time():
        raise HTTPException(status_code=400, detail="Availability must start in the future")
    overlap = db.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.available_date == payload.available_date,
        DoctorAvailability.start_time < payload.end_time,
        DoctorAvailability.end_time > payload.start_time
    ).first()
    if overlap:
        raise HTTPException(status_code=409, detail="Availability windows cannot overlap")
    row = DoctorAvailability(doctor_id=doctor.id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@router.get("/me/availability", response_model=list[AvailabilityOut])
def my_availability(db: Session = Depends(get_db), user: User = Depends(require_roles("doctor"))):
    doctor = db.query(Doctor).filter(Doctor.user_id == user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return db.query(DoctorAvailability).filter(DoctorAvailability.doctor_id == doctor.id).order_by(DoctorAvailability.available_date).all()
