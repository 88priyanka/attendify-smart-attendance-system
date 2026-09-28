from datetime import datetime, timedelta

from database import get_connection
from auth import create_user
from anomaly_detection import detect_frequent_absence


# =====================================================
# CREATE TEST EMPLOYEE
# =====================================================

test_email = "absence_test@attendify.com"

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
        name="Absence Test Employee",
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
# CREATE ATTENDANCE RECORDS
# =====================================================

connection = get_connection()
cursor = connection.cursor()

# Use recent weekdays and leave some weekdays completely
# without attendance to simulate genuine absence.

today = datetime.now().date()

attendance_added = 0

for days_ago in range(1, 10):

    test_date = today - timedelta(days=days_ago)

    # Only weekdays
    if test_date.weekday() < 5:

        date_string = test_date.strftime("%Y-%m-%d")

        cursor.execute("""
            SELECT id
            FROM attendance
            WHERE user_id = ?
            AND attendance_date = ?
        """, (user_id, date_string))

        if not cursor.fetchone():

            # Attend only some days
            if attendance_added < 2:

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
                    date_string,
                    date_string + " 09:30:00",
                    date_string + " 18:00:00",
                    "Present",
                    8.5
                ))

                attendance_added += 1


connection.commit()
connection.close()


# =====================================================
# TEST FREQUENT ABSENCE
# =====================================================

result = detect_frequent_absence(user_id)


print("\n==============================")
print("FREQUENT ABSENCE TEST")
print("==============================")

if result:

    print("✅ TEST PASSED")
    print(result)

else:

    print("❌ TEST FAILED")