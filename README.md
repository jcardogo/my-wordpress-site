# My WordPress Site

This repository contains a custom WordPress theme and a Python backend service that together provide:

- A content-focused homepage for posts
- Student class booking
- Booking tracking by student email
- Admin management for students, class sessions, and attendance logs

## Current Status

Implemented and working in code:

- WordPress theme with homepage hero and responsive post cards
- Booking form on homepage that submits student + class booking to Python API
- Tracking form on homepage that fetches booking history for a student
- Python Flask API integrated with Microsoft SQL Server (MSSQL)
- Admin UI for operational tasks:
	- Create student records
	- Create class sessions
	- Log and update attendance for students on sessions

## Architecture

1. Frontend
- WordPress theme in wp-content/themes/my-theme
- Forms are handled through WordPress admin-post actions

2. Backend
- Flask service in python-booking-service
- REST API endpoints for classes, bookings, tracking, and booking status updates

3. Database
- MSSQL schema for:
	- students
	- classes
	- bookings
	- class_sessions
	- attendance_logs

## Repository Structure

- README.md: Project overview and setup
- wp-content/themes/my-theme: WordPress theme files
- python-booking-service/app.py: Flask API and admin routes
- python-booking-service/templates/admin.html: Admin screen template
- python-booking-service/static/admin.css: Admin screen styling
- python-booking-service/sql/01_schema.sql: Core tables (students, classes, bookings)
- python-booking-service/sql/02_seed_classes.sql: Seed data for offered classes
- python-booking-service/sql/03_sessions_and_attendance.sql: Session and attendance tables
- python-booking-service/.env.example: Environment variables template
- python-booking-service/requirements.txt: Python dependencies

## Features Offered

1. Public Site Features
- Responsive hero and post grid layout
- Student class booking form
- Student booking tracking form

2. Admin Features
- Student creation
- Class session creation linked to classes
- Attendance logging with statuses:
	- present
	- absent
	- late
	- excused

3. API Features
- Health check
- List active classes
- Create booking
- Track bookings by student email
- Update booking status

## End-to-End Local Setup

1. Prepare WordPress
- Install WordPress locally
- Copy wp-content/themes/my-theme into your WordPress installation
- Activate My Theme in Appearance > Themes

2. Prepare MSSQL
- Create SQL Server database and tables by running:
	- python-booking-service/sql/01_schema.sql
	- python-booking-service/sql/02_seed_classes.sql
	- python-booking-service/sql/03_sessions_and_attendance.sql

3. Prepare Python Service
- Go to python-booking-service
- Copy .env.example to .env and set SQL Server credentials
- Create a virtual environment and install dependencies from requirements.txt
- Start the app with python app.py

4. Access UIs
- WordPress public forms: site homepage
- Python admin UI: http://127.0.0.1:5000/admin

## API Summary

- GET /api/health
- GET /api/classes
- POST /api/bookings
- GET /api/students/{email}/bookings
- PATCH /api/bookings/{tracking_id}/status

## Integration Notes

- WordPress API base URL defaults to http://127.0.0.1:5000/api
- You can override it via the WordPress filter my_theme_booking_api_base_url in theme logic

## Tech Stack

- WordPress 6.x
- PHP 7.4+
- Python 3.10+
- Flask
- Microsoft SQL Server (MSSQL)
- pyodbc + ODBC Driver 18 for SQL Server

## Next Improvements (Optional)

- Add authentication for Python admin UI
- Add edit/delete operations for students, sessions, and attendance rows
- Add pagination/filtering in admin tables
- Add deployment scripts for production environments
