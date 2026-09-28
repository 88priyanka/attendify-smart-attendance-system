from database import get_connection
import pandas as pd


# =========================================================
# GET ATTENDANCE DATA
# =========================================================

def get_attendance_data():

    connection = get_connection()

    query = """
        SELECT
            attendance.attendance_date,
            attendance.login_time,
            attendance.logout_time,
            attendance.status,
            attendance.working_hours,
            users.name,
            users.email,
            departments.department_name
        FROM attendance

        JOIN users
        ON attendance.user_id = users.id

        LEFT JOIN departments
        ON users.department_id = departments.id

        ORDER BY attendance.attendance_date ASC
    """

    df = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return df


# =========================================================
# ATTENDANCE SUMMARY
# =========================================================

def get_attendance_summary():

    connection = get_connection()

    query = """
        SELECT
            COUNT(*) AS total_records,

            SUM(
                CASE
                    WHEN status = 'Present'
                    THEN 1
                    ELSE 0
                END
            ) AS present_count,

            SUM(
                CASE
                    WHEN status = 'Late'
                    THEN 1
                    ELSE 0
                END
            ) AS late_count,

            ROUND(
                AVG(working_hours),
                2
            ) AS average_working_hours

        FROM attendance
    """

    cursor = connection.cursor()

    cursor.execute(query)

    result = cursor.fetchone()

    connection.close()

    return result


# =========================================================
# DEPARTMENT-WISE ATTENDANCE
# =========================================================

def get_department_attendance():

    connection = get_connection()

    query = """
        SELECT
            departments.department_name,
            COUNT(attendance.id) AS attendance_count
        FROM attendance

        JOIN users
        ON attendance.user_id = users.id

        LEFT JOIN departments
        ON users.department_id = departments.id

        GROUP BY departments.department_name

        ORDER BY attendance_count DESC
    """

    df = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return df


# =========================================================
# DAILY ATTENDANCE TREND
# =========================================================

def get_daily_attendance():

    connection = get_connection()

    query = """
        SELECT
            attendance_date,

            COUNT(*) AS total,

            SUM(
                CASE
                    WHEN status = 'Present'
                    THEN 1
                    ELSE 0
                END
            ) AS present,

            SUM(
                CASE
                    WHEN status = 'Late'
                    THEN 1
                    ELSE 0
                END
            ) AS late

        FROM attendance

        GROUP BY attendance_date

        ORDER BY attendance_date ASC
    """

    df = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return df