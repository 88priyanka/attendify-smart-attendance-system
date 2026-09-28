import sqlite3
from pathlib import Path
import bcrypt


# =====================================================
# DATABASE LOCATION
# =====================================================

DATABASE_PATH = Path("data/attendance.db")


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection():
    """Create and return a database connection."""

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return sqlite3.connect(
        DATABASE_PATH
    )


# =====================================================
# CREATE TABLES
# =====================================================

def create_tables():
    """Create all required database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # -------------------------------------------------
    # USERS TABLE
    # -------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
                CHECK(role IN ('Admin', 'Manager', 'Employee')),
            department_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)

    # -------------------------------------------------
    # DEPARTMENTS TABLE
    # -------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT UNIQUE NOT NULL
        )
    """)

    # -------------------------------------------------
    # ATTENDANCE TABLE
    # -------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            attendance_date DATE NOT NULL,
            login_time DATETIME,
            logout_time DATETIME,
            status TEXT NOT NULL,
            working_hours REAL DEFAULT 0,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)

    # -------------------------------------------------
    # LEAVE REQUESTS TABLE
    # -------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)

    # -------------------------------------------------
    # ALERTS TABLE
    # -------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            alert_type TEXT NOT NULL,
            message TEXT NOT NULL,
            severity TEXT DEFAULT 'Medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_resolved INTEGER DEFAULT 0,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
    """)

    # -------------------------------------------------
    # DEFAULT DEPARTMENTS
    # -------------------------------------------------

    departments = [
        ("IT",),
        ("HR",),
        ("Finance",),
        ("Sales",),
        ("Operations",)
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO departments
        (department_name)
        VALUES (?)
    """, departments)

    # -------------------------------------------------
    # GET DEPARTMENT IDs
    # -------------------------------------------------

    cursor.execute("""
        SELECT id, department_name
        FROM departments
    """)

    department_data = cursor.fetchall()

    department_ids = {
        name: department_id
        for department_id, name in department_data
    }

    # -------------------------------------------------
    # DEFAULT USERS
    # -------------------------------------------------

    default_users = [
        (
            "Priyanka",
            "priya@attendify.com",
            "Priya@123",
            "Employee",
            department_ids.get("IT")
        ),
        (
            "Attendify Admin",
            "admin@attendify.com",
            "Admin@123",
            "Admin",
            department_ids.get("IT")
        ),
        (
            "Attendify Manager",
            "manager@attendify.com",
            "Manager@123",
            "Manager",
            department_ids.get("HR")
        )
    ]

    # -------------------------------------------------
    # INSERT DEFAULT USERS
    # -------------------------------------------------

    for name, email, password, role, department_id in default_users:

        cursor.execute("""
            SELECT id
            FROM users
            WHERE email = ?
        """, (email,))

        existing_user = cursor.fetchone()

        if existing_user is None:

            hashed_password = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            cursor.execute("""
                INSERT INTO users
                (
                    name,
                    email,
                    password,
                    role,
                    department_id,
                    is_active
                )
                VALUES (?, ?, ?, ?, ?, 1)
            """, (
                name,
                email,
                hashed_password,
                role,
                department_id
            ))

    # -------------------------------------------------
    # SAVE CHANGES
    # -------------------------------------------------

    connection.commit()
    connection.close()


# =====================================================
# RUN DATABASE SETUP
# =====================================================

if __name__ == "__main__":

    create_tables()

    print(
        "Database and tables created successfully!"
    )