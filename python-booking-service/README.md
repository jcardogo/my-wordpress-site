# Python Student Booking Service

This service provides student class booking and tracking endpoints for the WordPress theme.

## Features

- List active classes from MSSQL
- Create a booking per student and class
- Track bookings by student email
- Update booking status (booked, attended, cancelled)

## Requirements

- Python 3.10+
- SQL Server (MSSQL)
- ODBC Driver 18 for SQL Server

## Setup

1. Copy `.env.example` to `.env` and update values.
2. Create virtual environment:
   - `python -m venv .venv`
   - `.venv\Scripts\activate`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Run SQL scripts in order:
   - `sql/01_schema.sql`
   - `sql/02_seed_classes.sql`
5. Start API:
   - `python app.py`

Default API base URL:

- `http://127.0.0.1:5000/api`

## Endpoints

- `GET /api/health`
- `GET /api/classes`
- `POST /api/bookings`
- `GET /api/students/{email}/bookings`
- `PATCH /api/bookings/{tracking_id}/status`

## Sample Request: Create Booking

```json
POST /api/bookings
{
  "student_name": "Jane Doe",
  "student_email": "jane@example.com",
  "class_id": 1
}
```

## WordPress Integration

The theme uses this API in `wp-content/themes/my-theme/functions.php`.
If your API host is different, update function `my_theme_booking_api_base_url()` or hook filter `my_theme_booking_api_base_url`.
