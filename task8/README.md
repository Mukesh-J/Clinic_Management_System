# Clinic Appointment & Patient Management System
<img width="1920" height="1080" alt="Screenshot 2026-10-16 135228" src="https://github.com/user-attachments/assets/360de6c2-d7d5-4227-b336-ac343a1f5f15" />
<img width="1920" height="1080" alt="Screenshot 2026-10-16 135242" src="https://github.com/user-attachments/assets/20f6cdc9-7d66-4c0a-890c-d822793379d4" />
<img width="1896" height="145" alt="Screenshot 2026-10-16 135304" src="https://github.com/user-attachments/assets/db2ad84a-2aee-4b59-891f-3aaa1f44f260" />

## 1. Project Overview

The Clinic Appointment & Patient Management System is a REST API application developed using **FastAPI, Python, MySQL, and SQLAlchemy**.

The main purpose of this project is to manage clinic operations such as doctor information, patient registration, appointment booking, and appointment management through APIs.

The application provides authentication and authorization to control access to protected endpoints.

## 2. Objectives

- Manage user registration and login.
- Secure APIs using JWT authentication.
- Manage doctor information.
- Book and manage clinic appointments.
- Store application data in a MySQL database.
- Validate request data using Pydantic.
- Organize the application using a modular project structure.
- Handle errors and return appropriate HTTP status codes.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | Building REST APIs |
| MySQL | Storing application data |
| SQLAlchemy | Database operations and ORM |
| Pydantic | Request and response validation |
| PyMySQL | Connecting Python to MySQL |
| JWT | Authentication using access tokens |
| pwdlib with Argon2 | Password hashing |
| Uvicorn | Running the FastAPI application |
| Swagger UI | Testing API endpoints |

## 4. Application Modules / Departments

### 4.1 Authentication Module

This module manages user authentication.

Responsibilities:
- User registration.
- User login.
- Password hashing.
- JWT access-token generation.
- Protecting endpoints using authentication dependencies.

### 4.2 Doctor Management Module

This module manages doctor-related information.

Responsibilities:
- Create doctor records.
- Retrieve doctor information.
- Update doctor information.
- Delete doctor records, where supported by the implemented endpoints.

### 4.3 Appointment Management Module

This module manages clinic appointments.

Responsibilities:
- Create appointments.
- Retrieve appointment information.
- Update appointment details or status, where supported.
- Delete appointments, where supported.
- Filter appointments using available query parameters, including date filtering if configured.

### 4.4 Admin Module

This module provides administrative API endpoints intended for authorized users.

Its available operations depend on the routes and permission checks implemented in the project.

### 4.5 Database Module

This module manages the connection between FastAPI and MySQL using SQLAlchemy.

Responsibilities:
- Configure the database connection.
- Create database sessions.
- Provide sessions to API endpoints.
- Create database tables from SQLAlchemy models during application startup.

## 5. Concepts Used

### 5.1 REST API

REST APIs allow clients to communicate with the application using HTTP methods.

- `GET` – Retrieve information.
- `POST` – Create information.
- `PUT` or `PATCH` – Update information.
- `DELETE` – Remove information.

### 5.2 CRUD Operations

CRUD means Create, Read, Update, and Delete. These operations are used to manage application records through API endpoints.

### 5.3 SQLAlchemy ORM

SQLAlchemy ORM maps Python classes to database tables. It allows the application to perform database operations using Python objects and queries instead of writing every SQL statement manually.

### 5.4 Pydantic Validation

Pydantic validates incoming request data using schemas. It helps ensure that API requests contain the expected data types and required fields.

### 5.5 JWT Authentication

JWT stands for JSON Web Token. After successful login, the application can issue an access token. The client sends that token when calling protected endpoints.

The application validates the token before allowing access to protected operations.

### 5.6 Password Hashing

Passwords should not be stored as plain text. Password hashing stores a derived hash, which can be verified during login without storing the original password.

### 5.7 Dependency Injection

FastAPI dependencies provide reusable functionality such as database sessions and authenticated-user information to API endpoints.

### 5.8 HTTP Status Codes

The API uses HTTP status codes to communicate request results.

- `200 OK` – Request successful.
- `201 Created` – A resource was created.
- `204 No Content` – Successful operation with no response body.
- `400 Bad Request` – Invalid request or business-rule failure.
- `401 Unauthorized` – Authentication is missing or invalid.
- `403 Forbidden` – Access is not permitted.
- `404 Not Found` – Requested resource does not exist.
- `422 Unprocessable Entity` – Request validation failed.

The exact codes depend on the behavior implemented by each endpoint.

## 6. Project Structure

```text
task8/
│
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── doctors.py
│   │   ├── appointments.py
│   │   └── admin.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── appointments.py
│   │
│   ├── __init__.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── .env
├── .env.example
├── README.md
└── requirements.txt
```

### File Responsibilities

- `main.py` – Creates the FastAPI application, registers routers, and initializes database tables.
- `database.py` – Configures the SQLAlchemy engine and database session.
- `models.py` – Defines database models.
- `schemas.py` – Defines Pydantic request and response schemas.
- `dependencies.py` – Provides shared dependencies, such as database sessions and authentication checks.
- `core/config.py` – Loads application configuration.
- `core/security.py` – Contains security-related functionality, including password hashing and JWT handling.
- `routers/auth.py` – Contains authentication endpoints.
- `routers/doctors.py` – Contains doctor-management endpoints.
- `routers/appointments.py` – Contains appointment-management endpoints.
- `routers/admin.py` – Contains administrative endpoints.
- `services/appointments.py` – Contains reusable appointment-related business logic.
- `.env` – Contains local configuration values and database credentials.
- `.env.example` – Provides a template for configuration.
- `requirements.txt` – Lists the required Python packages.

## 7. How the Application Works

### Step 1: Start the application

Uvicorn starts the FastAPI application. During startup, SQLAlchemy connects to MySQL and the application initializes the database tables.

### Step 2: Register a user

The client sends registration data to the authentication API. The application validates the input and securely hashes the password before storing the user, if registration is implemented for that request.

### Step 3: Log in

The user submits login credentials. The application verifies the credentials and returns an access token when authentication succeeds.

### Step 4: Access protected APIs

The client includes the JWT access token in the HTTP Authorization header:

`Authorization: Bearer <access_token>`

The authentication dependency validates the token before allowing the request to continue.

### Step 5: Manage doctors and appointments

The client sends requests to the doctor and appointment endpoints. FastAPI validates the request data, the application performs the required operations, and SQLAlchemy interacts with MySQL.

### Step 6: Return the response

FastAPI returns the result as JSON, together with an appropriate HTTP status code.

## 8. Installation and Setup

### Prerequisites

- Python installed.
- MySQL Server installed and running.
- VS Code or another Python editor.
- Required Python packages installed.

### Step 1: Create the database

Run this SQL in MySQL Workbench:

```sql
CREATE DATABASE IF NOT EXISTS clinic_db;
```

### Step 2: Configure environment variables

Create a `.env` file in the root `task8` directory:

```env
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/clinic_db
SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Update the database username and password if your MySQL configuration differs.

Do not commit `.env` or real database credentials to a public repository.

### Step 3: Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Start the server

Run these commands from the `task8` directory:

```bash
python -m uvicorn app.main:app --reload
```

### Step 5: Open Swagger UI

Visit:

http://127.0.0.1:8000/docs

Use Swagger UI to inspect and test the available API endpoints.

## 9. API Testing

The API can be tested using Swagger UI.

Suggested testing sequence:

1. Register a user, if the registration endpoint is available.
2. Log in and obtain an access token.
3. Use the **Authorize** option if configured for bearer-token authentication.
4. Test doctor endpoints.
5. Test appointment creation and retrieval.
6. Test available appointment filters.
7. Test invalid requests and unauthenticated access.
8. Verify that records are saved in MySQL.

The exact endpoint paths and required request bodies can be checked in Swagger UI.

## 10. What I Implemented

The project brings together the following development tasks:

- Created a FastAPI application with a modular folder structure.
- Configured MySQL connectivity using SQLAlchemy and PyMySQL.
- Defined database models and Pydantic schemas.
- Organized endpoints into separate routers for authentication, doctors, appointments, and administration.
- Implemented security-related utilities for password hashing and JWT authentication.
- Used dependencies to share database sessions and authentication logic.
- Added appointment-related service logic.
- Configured database table initialization during application startup.
- Prepared the application for API testing through Swagger UI.
- Created environment configuration files and project documentation.

**Note:** This list describes the project's intended structure and implementation based on its files. Only claim an endpoint or feature is fully working after testing it successfully.

## 11. Learning Outcomes

Through this project, I practiced:

- Building REST APIs with FastAPI.
- Working with MySQL databases.
- Using SQLAlchemy ORM.
- Validating data with Pydantic.
- Implementing JWT-based authentication.
- Understanding password hashing.
- Using dependency injection.
- Structuring a Python application into modules.
- Handling HTTP status codes and validation errors.
- Testing APIs through Swagger UI.

## 12. Conclusion

The Clinic Appointment & Patient Management System is a backend application designed to organize clinic-related data through REST APIs. It combines FastAPI, MySQL, SQLAlchemy, Pydantic, and authentication concepts in a modular project structure.

The project provides practical experience in backend development, database integration, API design, security, and API testing.
