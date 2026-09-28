from datetime import datetime, timedelta

from database import get_connection
from auth import create_user
from anomaly_detection import detect_irregular_attendance_pattern


# =====================================================
# CREATE TEST EMPLOYEE
# =====================================================

test_email = "irregular_test@attendify.com"

connection = get_connection()
cursor = connection.cursor()

cursor.execute(
    "SELECT id FROM users WHERE email = ?",
    (test_email,)
)

existing_user = cursor.fetchone()

connection.close()


if existing_user:
    user_id = existing_user[0]

else:
    create_user(
        name="Irregular Test Employee",
        email=test_email,
        password="Test@123",
        role="Employee",
        department_id=1
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE email = ?",
        (test_email,)
    )

    user_id = cursor.fetchone()[0]

    connection.close()


print(f"Testing employee ID: {user_id}")


# =====================================================
# CREATE 2 INCOMPLETE ATTENDANCE RECORDS
# =====================================================

connection = get_connection()
cursor = connection.cursor()

for days_ago in [2, 3]:

    attendance_date = (
        datetime.now() - timedelta(days=days_ago)
    ).strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT id
        FROM attendance
        WHERE user_id = ?
        AND attendance_date = ?
    """, (user_id, attendance_date))

    if not cursor.fetchone():

        cursor.execute("""
            INSERT INTO attendance
            (
                user_id,
                attendance_date,
                login_time,
                logout_time,
                status,
                working_hours
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            attendance_date,
            attendance_date + " 09:45:00",
            None,
            "Present",
            0
        ))


connection.commit()
connection.close()


# =====================================================
# TEST IRREGULAR ATTENDANCE
# =====================================================

result = detect_irregular_attendance_pattern(user_id)


print("\n==============================")
print("IRREGULAR ATTENDANCE TEST")
print("==============================")

if result:

    print("✅ TEST PASSED")
    print(result)

else:

    print("❌ TEST FAILED")