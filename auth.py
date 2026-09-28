import sqlite3
import bcrypt
from database import get_connection


def hash_password(password):
    """Securely hash a password."""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(password, hashed_password):
    """Verify a password against its hash."""
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_user(name, email, password, role, department_id=None):
    """Create a new user."""

    connection = get_connection()
    cursor = connection.cursor()

    hashed_password = hash_password(password)

    try:
        cursor.execute("""
            INSERT INTO users
            (name, email, password, role, department_id)
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            email,
            hashed_password,
            role,
            department_id
        ))

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def login_user(email, password):
    """Authenticate a user."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, email, password, role, department_id
        FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()
    connection.close()

    if user and verify_password(password, user[3]):
        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "role": user[4],
            "department_id": user[5]
        }

    return None