import os
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

import pyodbc
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) else default


def _db_connection_string() -> str:
    server = _env("MSSQL_SERVER")
    database = _env("MSSQL_DATABASE")
    username = _env("MSSQL_USERNAME")
    password = _env("MSSQL_PASSWORD")
    driver = _env("MSSQL_DRIVER", "ODBC Driver 18 for SQL Server")
    encrypt = _env("MSSQL_ENCRYPT", "no")
    trust = _env("MSSQL_TRUST_SERVER_CERT", "yes")

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt={encrypt};"
        f"TrustServerCertificate={trust};"
    )


@contextmanager
def db_cursor(commit: bool = False):
    conn = pyodbc.connect(_db_connection_string(), timeout=10)
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


@app.get("/api/health")
def health():
    try:
        with db_cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return jsonify({"status": "ok"}), 200
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.get("/api/classes")
def list_classes():
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, code, name, description, capacity
            FROM dbo.classes
            WHERE is_active = 1
            ORDER BY name ASC
            """
        )
        rows = cursor.fetchall()

    classes = [
        {
            "id": row.id,
            "code": row.code,
            "name": row.name,
            "description": row.description,
            "capacity": row.capacity,
        }
        for row in rows
    ]

    return jsonify({"classes": classes}), 200


@app.post("/api/bookings")
def create_booking():
    payload = request.get_json(silent=True) or {}

    student_name = str(payload.get("student_name", "")).strip()
    student_email = str(payload.get("student_email", "")).strip().lower()
    class_id = payload.get("class_id")

    if not student_name or not student_email or not class_id:
        return jsonify({"message": "student_name, student_email and class_id are required"}), 400

    try:
        class_id = int(class_id)
    except (TypeError, ValueError):
        return jsonify({"message": "class_id must be an integer"}), 400

    tracking_id = str(uuid.uuid4())
    now_utc = datetime.now(timezone.utc)

    with db_cursor(commit=True) as cursor:
        cursor.execute(
            "SELECT id FROM dbo.classes WHERE id = ? AND is_active = 1",
            class_id,
        )
        class_row = cursor.fetchone()
        if not class_row:
            return jsonify({"message": "Selected class does not exist."}), 404

        cursor.execute("SELECT id FROM dbo.students WHERE email = ?", student_email)
        student_row = cursor.fetchone()

        if student_row:
            student_id = student_row.id
            cursor.execute(
                """
                UPDATE dbo.students
                SET full_name = ?, updated_at = ?
                WHERE id = ?
                """,
                student_name,
                now_utc,
                student_id,
            )
        else:
            cursor.execute(
                """
                INSERT INTO dbo.students (full_name, email, created_at, updated_at)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?)
                """,
                student_name,
                student_email,
                now_utc,
                now_utc,
            )
            student_id = cursor.fetchone().id

        cursor.execute(
            "SELECT id, tracking_id FROM dbo.bookings WHERE student_id = ? AND class_id = ?",
            student_id,
            class_id,
        )
        existing_booking = cursor.fetchone()

        if existing_booking:
            return jsonify(
                {
                    "message": "Student already has a booking for this class.",
                    "tracking_id": existing_booking.tracking_id,
                }
            ), 409

        cursor.execute(
            """
            INSERT INTO dbo.bookings (student_id, class_id, tracking_id, status, booked_at, updated_at)
            VALUES (?, ?, ?, 'booked', ?, ?)
            """,
            student_id,
            class_id,
            tracking_id,
            now_utc,
            now_utc,
        )

    return jsonify({"message": "Booking created", "tracking_id": tracking_id}), 201


@app.get("/api/students/<path:student_email>/bookings")
def track_bookings(student_email: str):
    normalized_email = student_email.strip().lower()
    if not normalized_email:
        return jsonify({"message": "student email is required"}), 400

    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT s.full_name, s.email, c.name AS class_name, c.code AS class_code,
                   b.status, b.tracking_id, b.booked_at, b.updated_at
            FROM dbo.students s
            INNER JOIN dbo.bookings b ON b.student_id = s.id
            INNER JOIN dbo.classes c ON c.id = b.class_id
            WHERE s.email = ?
            ORDER BY b.booked_at DESC
            """,
            normalized_email,
        )
        rows = cursor.fetchall()

    if not rows:
        return jsonify({"message": "No bookings found for this student.", "bookings": []}), 404

    bookings = [
        {
            "class_name": row.class_name,
            "class_code": row.class_code,
            "status": row.status,
            "tracking_id": row.tracking_id,
            "booked_at": row.booked_at.isoformat() if row.booked_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }
        for row in rows
    ]

    return (
        jsonify(
            {
                "student_name": rows[0].full_name,
                "student_email": rows[0].email,
                "bookings": bookings,
            }
        ),
        200,
    )


@app.patch("/api/bookings/<tracking_id>/status")
def update_booking_status(tracking_id: str):
    payload = request.get_json(silent=True) or {}
    new_status = str(payload.get("status", "")).strip().lower()

    valid_statuses = {"booked", "attended", "cancelled"}
    if new_status not in valid_statuses:
        return jsonify({"message": "status must be one of: booked, attended, cancelled"}), 400

    now_utc = datetime.now(timezone.utc)

    with db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            UPDATE dbo.bookings
            SET status = ?, updated_at = ?
            WHERE tracking_id = ?
            """,
            new_status,
            now_utc,
            tracking_id,
        )
        if cursor.rowcount == 0:
            return jsonify({"message": "Booking not found."}), 404

    return jsonify({"message": "Booking status updated", "tracking_id": tracking_id, "status": new_status}), 200


if __name__ == "__main__":
    host = _env("FLASK_HOST", "0.0.0.0")
    port = int(_env("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=True)
