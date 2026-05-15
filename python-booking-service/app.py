import os
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

import pyodbc
from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

load_dotenv()

app = Flask(__name__)


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) else default


app.secret_key = _env("FLASK_SECRET_KEY", "dev-change-me")


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


def _load_admin_data() -> dict:
    with db_cursor() as cursor:
        cursor.execute(
            """
            SELECT id, full_name, email, created_at
            FROM dbo.students
            ORDER BY full_name ASC
            """
        )
        students_rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT id, code, name
            FROM dbo.classes
            WHERE is_active = 1
            ORDER BY name ASC
            """
        )
        classes_rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT TOP 100 cs.id, cs.session_title, cs.session_date, cs.start_time,
                   cs.end_time, cs.location, c.name AS class_name, c.code AS class_code
            FROM dbo.class_sessions cs
            INNER JOIN dbo.classes c ON c.id = cs.class_id
            ORDER BY cs.session_date DESC, cs.start_time DESC
            """
        )
        sessions_rows = cursor.fetchall()

        cursor.execute(
            """
            SELECT TOP 100 al.id, al.attendance_status, al.notes, al.marked_at,
                   s.full_name, s.email, cs.session_title, cs.session_date,
                   c.name AS class_name
            FROM dbo.attendance_logs al
            INNER JOIN dbo.students s ON s.id = al.student_id
            INNER JOIN dbo.class_sessions cs ON cs.id = al.session_id
            INNER JOIN dbo.classes c ON c.id = cs.class_id
            ORDER BY al.marked_at DESC
            """
        )
        attendance_rows = cursor.fetchall()

    students = [
        {
            "id": row.id,
            "full_name": row.full_name,
            "email": row.email,
            "created_at": row.created_at,
        }
        for row in students_rows
    ]

    classes = [
        {
            "id": row.id,
            "code": row.code,
            "name": row.name,
        }
        for row in classes_rows
    ]

    sessions = [
        {
            "id": row.id,
            "session_title": row.session_title,
            "session_date": row.session_date,
            "start_time": row.start_time,
            "end_time": row.end_time,
            "location": row.location,
            "class_name": row.class_name,
            "class_code": row.class_code,
        }
        for row in sessions_rows
    ]

    attendance = [
        {
            "id": row.id,
            "attendance_status": row.attendance_status,
            "notes": row.notes,
            "marked_at": row.marked_at,
            "full_name": row.full_name,
            "email": row.email,
            "session_title": row.session_title,
            "session_date": row.session_date,
            "class_name": row.class_name,
        }
        for row in attendance_rows
    ]

    return {
        "students": students,
        "classes": classes,
        "sessions": sessions,
        "attendance": attendance,
        "attendance_statuses": ["present", "absent", "late", "excused"],
    }


@app.get("/admin")
def admin_dashboard():
    data = _load_admin_data()
    return render_template("admin.html", **data)


@app.post("/admin/students")
def admin_create_student():
    full_name = str(request.form.get("full_name", "")).strip()
    email = str(request.form.get("email", "")).strip().lower()

    if not full_name or not email:
        flash("Student name and email are required.", "error")
        return redirect(url_for("admin_dashboard"))

    now_utc = datetime.now(timezone.utc)
    try:
        with db_cursor(commit=True) as cursor:
            cursor.execute(
                """
                INSERT INTO dbo.students (full_name, email, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                full_name,
                email,
                now_utc,
                now_utc,
            )
        flash("Student created successfully.", "success")
    except pyodbc.IntegrityError:
        flash("A student with this email already exists.", "error")

    return redirect(url_for("admin_dashboard"))


@app.post("/admin/sessions")
def admin_create_session():
    class_id_raw = request.form.get("class_id", "")
    session_title = str(request.form.get("session_title", "")).strip()
    session_date_raw = str(request.form.get("session_date", "")).strip()
    start_time_raw = str(request.form.get("start_time", "")).strip()
    end_time_raw = str(request.form.get("end_time", "")).strip()
    location = str(request.form.get("location", "")).strip()

    if not class_id_raw or not session_title or not session_date_raw:
        flash("Class, session title, and session date are required.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        class_id = int(class_id_raw)
    except ValueError:
        flash("Invalid class selected.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        session_date = datetime.strptime(session_date_raw, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid session date format.", "error")
        return redirect(url_for("admin_dashboard"))

    start_time = None
    if start_time_raw:
        try:
            start_time = datetime.strptime(start_time_raw, "%H:%M").time()
        except ValueError:
            flash("Invalid start time format.", "error")
            return redirect(url_for("admin_dashboard"))

    end_time = None
    if end_time_raw:
        try:
            end_time = datetime.strptime(end_time_raw, "%H:%M").time()
        except ValueError:
            flash("Invalid end time format.", "error")
            return redirect(url_for("admin_dashboard"))

    now_utc = datetime.now(timezone.utc)
    with db_cursor(commit=True) as cursor:
        cursor.execute(
            "SELECT id FROM dbo.classes WHERE id = ? AND is_active = 1",
            class_id,
        )
        if not cursor.fetchone():
            flash("Selected class does not exist.", "error")
            return redirect(url_for("admin_dashboard"))

        cursor.execute(
            """
            INSERT INTO dbo.class_sessions (
                class_id, session_title, session_date, start_time, end_time,
                location, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            class_id,
            session_title,
            session_date,
            start_time,
            end_time,
            location or None,
            now_utc,
            now_utc,
        )

    flash("Class session created.", "success")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/attendance")
def admin_log_attendance():
    student_id_raw = request.form.get("student_id", "")
    session_id_raw = request.form.get("session_id", "")
    attendance_status = str(request.form.get("attendance_status", "")).strip().lower()
    notes = str(request.form.get("notes", "")).strip()

    valid_statuses = {"present", "absent", "late", "excused"}

    if not student_id_raw or not session_id_raw or attendance_status not in valid_statuses:
        flash("Student, session, and valid attendance status are required.", "error")
        return redirect(url_for("admin_dashboard"))

    try:
        student_id = int(student_id_raw)
        session_id = int(session_id_raw)
    except ValueError:
        flash("Invalid student or session id.", "error")
        return redirect(url_for("admin_dashboard"))

    now_utc = datetime.now(timezone.utc)

    with db_cursor(commit=True) as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM dbo.class_sessions cs
            INNER JOIN dbo.bookings b ON b.class_id = cs.class_id
            WHERE cs.id = ?
              AND b.student_id = ?
              AND b.status <> 'cancelled'
            """,
            session_id,
            student_id,
        )
        if not cursor.fetchone():
            flash("Student must have an active booking in the session class.", "error")
            return redirect(url_for("admin_dashboard"))

        cursor.execute(
            "SELECT id FROM dbo.attendance_logs WHERE student_id = ? AND session_id = ?",
            student_id,
            session_id,
        )
        existing_row = cursor.fetchone()

        if existing_row:
            cursor.execute(
                """
                UPDATE dbo.attendance_logs
                SET attendance_status = ?, notes = ?, marked_at = ?
                WHERE id = ?
                """,
                attendance_status,
                notes or None,
                now_utc,
                existing_row.id,
            )
            flash("Attendance updated.", "success")
        else:
            cursor.execute(
                """
                INSERT INTO dbo.attendance_logs (
                    session_id, student_id, attendance_status, notes, marked_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                session_id,
                student_id,
                attendance_status,
                notes or None,
                now_utc,
            )
            flash("Attendance logged.", "success")

    return redirect(url_for("admin_dashboard"))


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
