from database import get_connection


# =========================================================
# CREATE ALERT
# =========================================================

def create_alert(
    user_id,
    alert_type,
    message,
    severity="Medium"
):
    connection = get_connection()
    cursor = connection.cursor()

    # Check whether the same unresolved alert already exists
    cursor.execute("""
        SELECT id
        FROM alerts
        WHERE user_id = ?
        AND alert_type = ?
        AND is_resolved = 0
    """, (
        user_id,
        alert_type
    ))

    existing_alert = cursor.fetchone()

    if existing_alert:
        connection.close()
        return False

    cursor.execute("""
        INSERT INTO alerts
        (
            user_id,
            alert_type,
            message,
            severity
        )
        VALUES (?, ?, ?, ?)
    """, (
        user_id,
        alert_type,
        message,
        severity
    ))

    connection.commit()
    connection.close()

    return True


# =========================================================
# GET ALL ALERTS
# =========================================================

def get_all_alerts():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            alerts.id,
            users.name,
            users.email,
            alerts.alert_type,
            alerts.message,
            alerts.severity,
            alerts.created_at,
            alerts.is_resolved
        FROM alerts
        JOIN users
        ON alerts.user_id = users.id
        ORDER BY alerts.id DESC
    """)

    alerts = cursor.fetchall()

    connection.close()

    return alerts


# =========================================================
# GET UNRESOLVED ALERTS
# =========================================================

def get_unresolved_alerts():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            alerts.id,
            users.name,
            alerts.alert_type,
            alerts.message,
            alerts.severity,
            alerts.created_at
        FROM alerts
        JOIN users
        ON alerts.user_id = users.id
        WHERE alerts.is_resolved = 0
        ORDER BY alerts.id DESC
    """)

    alerts = cursor.fetchall()

    connection.close()

    return alerts


# =========================================================
# RESOLVE ALERT
# =========================================================

def resolve_alert(alert_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE alerts
        SET is_resolved = 1
        WHERE id = ?
    """, (alert_id,))

    connection.commit()
    connection.close()

    return True


# =========================================================
# COUNT UNRESOLVED ALERTS
# =========================================================

def get_unresolved_alert_count():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM alerts
        WHERE is_resolved = 0
    """)

    count = cursor.fetchone()[0]

    connection.close()

    return count