from database import get_connection
from auth import create_user


# =====================================================
# GET DEPARTMENTS
# =====================================================

def get_departments():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, department_name
        FROM departments
        ORDER BY department_name
    """)

    departments = cursor.fetchall()

    connection.close()

    return departments


# =====================================================
# ADD EMPLOYEE
# =====================================================

def add_employee(name, email, password, department_id):

    return create_user(
        name=name,
        email=email,
        password=password,
        role="Employee",
        department_id=department_id
    )


# =====================================================
# GET ALL EMPLOYEES
# =====================================================

def get_all_employees():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT
        users.id,
        users.name,
        users.email,
        departments.department_name,
        users.created_at,
        users.is_active
    FROM users
    LEFT JOIN departments
    ON users.department_id = departments.id
    WHERE users.role = 'Employee'
    ORDER BY users.id DESC
""")
    employees = cursor.fetchall()

    connection.close()

    return employees


# =====================================================
# UPDATE EMPLOYEE
# =====================================================

def update_employee(
    employee_id,
    name,
    email,
    department_id
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET name = ?,
            email = ?,
            department_id = ?
        WHERE id = ?
        AND role = 'Employee'
    """, (
        name,
        email,
        department_id,
        employee_id
    ))

    connection.commit()
    connection.close()

    return True


# =====================================================
# DEACTIVATE EMPLOYEE
# =====================================================

def deactivate_employee(employee_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET is_active = 0
        WHERE id = ?
        AND role = 'Employee'
    """, (employee_id,))

    connection.commit()
    connection.close()

    return True