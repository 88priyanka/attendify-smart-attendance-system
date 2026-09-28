from datetime import datetime, timedelta
from database import get_connection
from anomaly_detection import detect_late_arrivals


# Get an existing employee
connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    SELECT id, name
    FROM users
    WHERE role = 'Employee'
    LIMIT 1
""")

employee = cursor.fetchone()

if not employee:
    print("❌ No employee found.")
    connection.close()
    exit()

user_id = employee[0]
employee_name = employee[1]

print(f"Testing employee: {employee_name}")


# Add 3 previous Late attendance records
for days_ago in [3, 4, 5]:

    attendance_date = (
        datetime.now() - timedelta(days=days_ago)
    ).strftime("%Y-%m-%d")

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
        attendance_date + " 10:15:00",
        attendance_date + " 18:00:00",
        "Late",
        7.75
    ))


connection.commit()
connection.close()


# Test anomaly rule
result = detect_late_arrivals(user_id)


print("\n==============================")
print("REPEATED LATE ARRIVAL TEST")
print("==============================")

if result:
    print("✅ TEST PASSED")
    print(result)
else:
    print("❌ TEST FAILED")