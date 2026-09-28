from datetime import datetime, timedelta

from database import get_connection
from alerts import create_alert


# =====================================================
# 1. REPEATED LATE ARRIVALS
# =====================================================

def detect_late_arrivals(user_id, late_limit=3):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE user_id = ?
        AND status = 'Late'
    """, (user_id,))

    late_count = cursor.fetchone()[0]

    connection.close()

    if late_count >= late_limit:

        return {
            "type": "Repeated Late Arrival",
            "message": (
                f"Employee has been late "
                f"{late_count} times."
            ),
            "severity": "Medium"
        }

    return None


# =====================================================
# 2. LOW WORKING HOURS
# =====================================================

def detect_low_working_hours(user_id, minimum_hours=4):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE user_id = ?
        AND working_hours > 0
        AND working_hours < ?
    """, (
        user_id,
        minimum_hours
    ))

    low_hours_count = cursor.fetchone()[0]

    connection.close()

    if low_hours_count >= 3:

        return {
            "type": "Low Working Hours",
            "message": (
                f"Employee has recorded working hours "
                f"below {minimum_hours} hours "
                f"{low_hours_count} times."
            ),
            "severity": "Medium"
        }

    return None


# =====================================================
# 3. FREQUENT ABSENCE
# =====================================================

def detect_frequent_absence(user_id, absence_limit=3):

    connection = get_connection()
    cursor = connection.cursor()

    today = datetime.now().date()
    start_date = today - timedelta(days=14)

    # Get attendance dates
    cursor.execute("""
        SELECT attendance_date
        FROM attendance
        WHERE user_id = ?
        AND attendance_date BETWEEN ? AND ?
    """, (
        user_id,
        start_date,
        today
    ))

    attendance_records = cursor.fetchall()

    attendance_dates = {
        str(record[0])
        for record in attendance_records
    }

    # Get approved leave dates
    cursor.execute("""
        SELECT start_date, end_date
        FROM leave_requests
        WHERE user_id = ?
        AND status = 'Approved'
        AND start_date <= ?
        AND end_date >= ?
    """, (
        user_id,
        today,
        start_date
    ))

    leave_records = cursor.fetchall()

    connection.close()

    # Create set of approved leave dates
    approved_leave_dates = set()

    for start_date_value, end_date_value in leave_records:

        leave_start = datetime.strptime(
            str(start_date_value),
            "%Y-%m-%d"
        ).date()

        leave_end = datetime.strptime(
            str(end_date_value),
            "%Y-%m-%d"
        ).date()

        current_date = max(
            leave_start,
            start_date
        )

        while current_date <= min(
            leave_end,
            today
        ):

            if current_date.weekday() < 5:
                approved_leave_dates.add(
                    current_date.strftime("%Y-%m-%d")
                )

            current_date += timedelta(days=1)

    # Calculate genuine absences
    absence_count = 0
    current_date = start_date

    while current_date <= today:

        date_string = current_date.strftime("%Y-%m-%d")

        # Only Monday-Friday
        if current_date.weekday() < 5:

            # Not attended and not on approved leave
            if (
                date_string not in attendance_dates
                and date_string not in approved_leave_dates
            ):
                absence_count += 1

        current_date += timedelta(days=1)

    if absence_count >= absence_limit:

        return {
            "type": "Frequent Absence",
            "message": (
                f"Employee may have been absent "
                f"for approximately {absence_count} "
                "working days in the last 14 days."
            ),
            "severity": "High"
        }

    return None


# =====================================================
# 4. IRREGULAR ATTENDANCE PATTERN
# =====================================================

def detect_irregular_attendance_pattern(
    user_id,
    incomplete_limit=2
):

    connection = get_connection()
    cursor = connection.cursor()

    today = datetime.now().date()

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE user_id = ?
        AND attendance_date < ?
        AND login_time IS NOT NULL
        AND logout_time IS NULL
    """, (
        user_id,
        today
    ))

    incomplete_count = cursor.fetchone()[0]

    connection.close()

    if incomplete_count >= incomplete_limit:

        return {
            "type": "Irregular Attendance Pattern",
            "message": (
                f"Employee has {incomplete_count} previous "
                "attendance records without a recorded logout."
            ),
            "severity": "Medium"
        }

    return None

# =====================================================
# MAIN ANOMALY DETECTION
# =====================================================

def detect_employee_anomalies(user_id):

    anomalies = []

    # Rule 1 - Late arrivals
    late_anomaly = detect_late_arrivals(user_id)

    if late_anomaly:
        anomalies.append(late_anomaly)

    # Rule 2 - Low working hours
    hours_anomaly = detect_low_working_hours(user_id)

    if hours_anomaly:
        anomalies.append(hours_anomaly)

    # Rule 3 - Frequent absence
    absence_anomaly = detect_frequent_absence(user_id)

    if absence_anomaly:
        anomalies.append(absence_anomaly)

    # Rule 4 - Irregular attendance pattern
    pattern_anomaly = detect_irregular_attendance_pattern(user_id)

    if pattern_anomaly:
        anomalies.append(pattern_anomaly)

    # Create alerts automatically
    for anomaly in anomalies:

        create_alert(
            user_id=user_id,
            alert_type=anomaly["type"],
            message=anomaly["message"],
            severity=anomaly["severity"]
        )

    return anomalies