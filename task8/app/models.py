from datetime import datetime, date, time
from sqlalchemy import String, Boolean, DateTime, Date, Time, Integer, ForeignKey, Numeric, Text, Enum, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(Enum("admin", "doctor", "patient", name="user_roles"), default="patient", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    doctor_profile: Mapped["Doctor"] = relationship(back_populates="user", uselist=False)
    appointments_as_patient: Mapped[list["Appointment"]] = relationship(back_populates="patient", foreign_keys="Appointment.patient_id")

class Doctor(Base):
    __tablename__ = "doctors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    specialization: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    consultation_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user: Mapped[User] = relationship(back_populates="doctor_profile")
    availability: Mapped[list["DoctorAvailability"]] = relationship(back_populates="doctor", cascade="all, delete-orphan")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="doctor")

class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"
    __table_args__ = (UniqueConstraint("doctor_id", "available_date", "start_time", "end_time", name="uq_doctor_availability_window"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True)
    available_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    doctor: Mapped[Doctor] = relationship(back_populates="availability")

class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (Index("ix_appointment_doctor_date_time", "doctor_id", "appointment_date", "start_time", "end_time"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False, index=True)
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Enum("Pending", "Confirmed", "Completed", "Cancelled", name="appointment_status"), default="Pending", nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    patient: Mapped[User] = relationship(back_populates="appointments_as_patient", foreign_keys=[patient_id])
    doctor: Mapped[Doctor] = relationship(back_populates="appointments")
