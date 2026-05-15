# Python Booking Service

This service is the backend for student class operations used by the WordPress site. It exposes REST APIs and an admin web interface backed by Microsoft SQL Server.

## Current Status

Implemented and available in code:

- API endpoints for health, classes, booking creation, booking tracking, and booking status updates
- Admin UI for creating students, creating class sessions, and logging attendance
- MSSQL persistence with relational tables and constraints
- WordPress integration-ready endpoint structure

## Architecture

1. Web/API Layer
- Flask application in app.py
- REST endpoints under /api/*
- Admin web interface under /admin

2. Data Layer
- pyodbc connection to MSSQL
- SQL scripts to create schema and seed classes

## Features Offered

1. Booking and Tracking
- List active classes
- Create a booking per student/class pair
- Track bookings by student email
- Update booking status: booked, attended, cancelled

2. Admin Management
- Create student records
- Create class sessions linked to classes
- Log or update attendance for a student in a session
- Attendance statuses: present, absent, late, excused

## Project Files

- app.py: Flask app, API routes, admin routes, and database logic
- templates/admin.html: Admin screen markup
- static/admin.css: Admin screen styling
- sql/01_schema.sql: Core schema (students, classes, bookings)
- sql/02_seed_classes.sql: Seed classes offered
- sql/03_sessions_and_attendance.sql: Session and attendance schema
- .env.example: Required environment variables
- requirements.txt: Python dependencies

## Requirements

- Python 3.10+
- SQL Server (MSSQL)
- ODBC Driver 18 for SQL Server

## Setup

1. Create environment file
- Copy .env.example to .env
- Set MSSQL server, database, username, password, and Flask secret key

2. Create Python environment and install dependencies
- python -m venv .venv
- .venv\Scripts\activate
- pip install -r requirements.txt

3. Create database schema
- Run sql/01_schema.sql
- Run sql/02_seed_classes.sql
- Run sql/03_sessions_and_attendance.sql

4. Start the service
- python app.py

## Access Points

- API base URL: http://127.0.0.1:5000/api
- Admin UI: http://127.0.0.1:5000/admin

## API Endpoints

- GET /api/health
- GET /api/classes
- POST /api/bookings
- GET /api/students/{email}/bookings
- PATCH /api/bookings/{tracking_id}/status

## Sample Request

Create booking:

```json
POST /api/bookings
{
  "student_name": "Jane Doe",
  "student_email": "jane@example.com",
  "class_id": 1
}
```

## WordPress Integration

The WordPress theme posts booking and tracking requests to this service.

- Theme integration file: wp-content/themes/my-theme/functions.php
- Default API base URL expected by the theme: http://127.0.0.1:5000/api

If your backend host changes, update the theme API base URL logic via the filter hook already provided in the theme.
