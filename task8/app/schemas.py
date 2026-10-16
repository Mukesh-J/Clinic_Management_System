from datetime import date, time, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

Role = Literal["admin", "doctor", "patient"]
AppointmentStatus = Literal["Pending", "Confirmed", "Completed", "Cancelled"]

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class DoctorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    specialization: str = Field(min_length=2, max_length=120)
    consultation_fee: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    experience_years: int = Field(ge=0, le=70)

class DoctorUpdate(BaseModel):
    specialization: str | None = Field(default=None, min_length=2, max_length=120)
    consultation_fee: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    experience_years: int | None = Field(default=None, ge=0, le=70)

class DoctorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    specialization: str
    consultation_fee: Decimal
    experience_years: int
    name: str
    email: EmailStr
    is_active: bool

class AvailabilityCreate(BaseModel):
    available_date: date
    start_time: time
    end_time: time
    is_available: bool = True

    @model_validator(mode="after")
    def validate_window(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        if self.available_date < date.today():
            raise ValueError("Availability date cannot be in the past")
        return self

class AvailabilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    doctor_id: int
    available_date: date
    start_time: time
    end_time: time
    is_available: bool

class AppointmentCreate(BaseModel):
    doctor_id: int = Field(gt=0)
    appointment_date: date
    start_time: time
    end_time: time
    reason: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_slot(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        if self.appointment_date < date.today():
            raise ValueError("Cannot book an appointment in the past")
        return self

class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus

class AppointmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    start_time: time
    end_time: time
    reason: str | None
    status: str
    created_at: datetime

class AppointmentDetail(AppointmentOut):
    patient_name: str
    patient_email: EmailStr
    doctor_name: str
    specialization: str

class DailyCount(BaseModel):
    appointment_date: date
    count: int
