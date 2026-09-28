from database import get_connection


# =========================================================
# CREATE LEAVE REQUEST
# =========================================================

def create_leave_request(
    user_id,
    leave_type,
    start_date,
    end_date,
    reason
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO leave_requests
        (
            user_id,
            leave_type,
            start_date,
            end_date,
            reason,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        leave_type,
        start_date,
        end_date,
        reason,
        "Pending"
    ))

    connection.commit()
    connection.close()

    return True


# =========================================================
# GET EMPLOYEE LEAVE REQUESTS
# =========================================================

def get_employee_leave_requests(user_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            leave_type,
            start_date,
            end_date,
            reason,
            status
        FROM leave_requests
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    requests = cursor.fetchall()

    connection.close()

    return requests


# =========================================================
# GET ALL LEAVE REQUESTS
# =========================================================

def get_all_leave_requests():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            leave_requests.id,
            users.name,
            users.email,
            leave_requests.leave_type,
            leave_requests.start_date,
            leave_requests.end_date,
            leave_requests.reason,
            leave_requests.status
        FROM leave_requests
        JOIN users
        ON leave_requests.user_id = users.id
        ORDER BY leave_requests.id DESC
    """)

    requests = cursor.fetchall()

    connection.close()

    return requests


# =========================================================
# UPDATE LEAVE STATUS
# =========================================================

def update_leave_status(leave_id, status):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE leave_requests
        SET status = ?
        WHERE id = ?
    """, (
        status,
        leave_id
    ))

    connection.commit()
    connection.close()

    return True