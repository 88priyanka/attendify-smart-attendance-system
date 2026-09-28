from datetime import datetime, time
from database import get_connection


# Company working time
OFFICE_START_TIME = time(9, 30)


def mark_attendance(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    login_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Check whether attendance already exists
    cursor.execute("""
        SELECT id
        FROM attendance
        WHERE user_id = ?
        AND attendance_date = ?
    """, (user_id, today))

    existing = cursor.fetchone()

    if existing:
        connection.close()
        return False

    # Automatically detect Present or Late
    if now.time() > OFFICE_START_TIME:
        status = "Late"
    else:
        status = "Present"

    cursor.execute("""
        INSERT INTO attendance
        (
            user_id,
            attendance_date,
            login_time,
            status,
            working_hours
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        today,
        login_time,
        status,
        0
    ))

    connection.commit()
    connection.close()

    return True


def logout_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    logout_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Get today's login time
    cursor.execute("""
        SELECT login_time
        FROM attendance
        WHERE user_id = ?
        AND attendance_date = ?
        AND logout_time IS NULL
    """, (user_id, today))

    result = cursor.fetchone()

    if not result:
        connection.close()
        return False

    login_time = datetime.strptime(
        result[0],
        "%Y-%m-%d %H:%M:%S"
    )

    working_hours = (
        now - login_time
    ).total_seconds() / 3600

    cursor.execute("""
        UPDATE attendance
        SET
            logout_time = ?,
            working_hours = ?
        WHERE user_id = ?
        AND attendance_date = ?
    """, (
        logout_time,
        round(working_hours, 2),
        user_id,
        today
    ))

    connection.commit()
    connection.close()

    return True


def get_today_attendance():
    connection = get_connection()
    cursor = connection.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT
            users.name,
            users.email,
            users.role,
            attendance.login_time,
            attendance.logout_time,
            attendance.status,
            attendance.working_hours
        FROM attendance
        JOIN users
        ON attendance.user_id = users.id
        WHERE attendance.attendance_date = ?
        ORDER BY attendance.login_time DESC
    """, (today,))

    data = cursor.fetchall()

    connection.close()

    return data