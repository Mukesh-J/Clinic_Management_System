# Clinic Appointment & Patient Management API

FastAPI + MySQL + SQLAlchemy + Pydantic + JWT. Test endpoints using Swagger UI at `http://127.0.0.1:8000/docs`.

## 1. Setup
1. Install Python 3.10+ and MySQL.
2. Create the database:
   ```sql
   CREATE DATABASE clinic_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
3. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
   On macOS/Linux: `source .venv/bin/activate`
4. Install packages: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and update `DATABASE_URL` and `SECRET_KEY`.
6. Start the API from the project root:
   ```bash
   uvicorn app.main:app --reload
   ```
Tables are created automatically at startup for this training project. For production, use Alembic migrations.

## 2. Create an admin account
Public registration deliberately creates **patients only**. To create the first admin safely, register a patient, then promote that user directly in MySQL:
```sql
UPDATE users SET role='admin' WHERE email='your-email@example.com';
```
Log in again to obtain a token with the new role. Admins can create doctor profiles through `/admin/doctors`; the endpoint creates a linked doctor login user. Do not expose public role selection in registration.

## 3. Swagger workflow
1. `POST /auth/register` with name, email, password.
2. `POST /auth/login` using form fields `username` (email) and `password`.
3. Copy `access_token` from the response.
4. Click **Authorize** and enter `Bearer YOUR_TOKEN` if prompted for the full value; if the dialog expects just a token, paste the token only.
5. As admin, create a doctor via `/admin/doctors`.
6. As doctor, create availability via `POST /doctors/me/availability`.
7. As patient, book a slot via `POST /appointments`.
8. Test listing, cancellation, role failures, invalid slots and duplicate bookings.

## 4. Roles and business rules
- Roles: `admin`, `doctor`, `patient`. Public registration only permits patient accounts.
- Inactive accounts cannot log in or use protected endpoints.
- Patients can view/cancel only their own appointments. Cancellation is blocked for completed/cancelled appointments and appointments that have already started.
- Doctors can view their own appointments and update only appointments assigned to them.
- Allowed status transitions: `Pending -> Confirmed/Cancelled`; `Confirmed -> Completed/Cancelled`; terminal states cannot be changed.
- Appointment times must fit inside an available doctor time window. Overlap is checked against active appointments. The booking service locks the doctor row during the transaction to reduce concurrent booking conflicts; use a unique slot model / exclusion strategy and transaction tests for stronger guarantees in production.
- Time slots use a date and start/end times. Availability windows may host multiple appointments if their time ranges do not overlap.
- Admin statistics include user totals, appointment totals, counts by status and daily counts.

## 5. Endpoint summary
### Auth
- `POST /auth/register` — patient registration
- `POST /auth/login` — OAuth2 password form login; username is email
- `GET /auth/me` — current account

### Doctors
- `GET /doctors` — search/filter/sort/paginate active doctors
- `GET /doctors/{doctor_id}` — doctor profile
- `POST /doctors/me/availability` — doctor creates an availability window
- `GET /doctors/me/availability` — doctor's own windows

### Appointments
- `POST /appointments` — patient books
- `GET /appointments` — own appointments for patients/doctors; admin can see all
- `GET /appointments/{appointment_id}` — owner/assigned doctor/admin only
- `PATCH /appointments/{appointment_id}/cancel` — patient cancels own eligible appointment
- `PATCH /appointments/{appointment_id}/status` — assigned doctor or admin updates status

### Admin
- `POST /admin/doctors` — create doctor login + profile
- `PATCH /admin/doctors/{doctor_id}` — update doctor profile
- `PATCH /admin/doctors/{doctor_id}/deactivate` — deactivate doctor account
- `GET /admin/statistics` — totals, status groups and daily counts

## 6. Architecture
- `models.py`: SQLAlchemy tables and relationships
- `schemas.py`: request/response validation
- `core/security.py`: password hashing and JWT
- `dependencies.py`: database session, current user and role checks
- `services/appointments.py`: booking conflict and status workflow
- `routers/`: separated route groups
- `main.py`: application setup and startup table creation

## 7. Notes
- This is a runnable training baseline, not a production-certified medical system. Add Alembic migrations, audit logs, rate limiting, refresh-token strategy, privacy controls, automated tests, and stronger concurrency guarantees before deployment.
- Do not put real patient information in screenshots or public repositories.
