from fastapi import FastAPI
from app.database import Base, engine
from app import models
from app.routers import auth, doctors, appointments, admin

app = FastAPI(title="Clinic Appointment & Patient Management API", version="1.0.0",
              description="JWT-secured clinic API. Use Swagger Authorize to test protected endpoints.")

@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(admin.router)

@app.get("/", tags=["Health"])
def health_check():
    return {"message": "Clinic API is running", "docs": "/docs"}
