
import bcrypt

from database.db_connection import get_connection
import secrets
import hashlib
from datetime import datetime, timedelta, timezone

# Create a persistent login session
def create_login_session(user_id):

    # Generate a random session token
    session_token = secrets.token_urlsafe(32)

    # Store only its hash in the database
    token_hash = hashlib.sha256(
        session_token.encode("utf-8")
    ).hexdigest()

    # Session expires after 30 days
    expiry_date = datetime.now(timezone.utc) + timedelta(days=30)

    connection = get_connection()
    cursor = connection.cursor()

    # Create the sessions table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT UNIQUE NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
                REFERENCES users(user_id)
                ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        INSERT INTO login_sessions
        (user_id, token_hash, expires_at)
        VALUES (?, ?, ?)
    """, (
        user_id,
        token_hash,
        expiry_date.isoformat()
    ))

    connection.commit()
    connection.close()

    return session_token


# Restore a user from a saved browser session
def get_user_by_session_token(session_token):

    if not session_token:
        return None

    token_hash = hashlib.sha256(
        session_token.encode("utf-8")
    ).hexdigest()

    current_time = datetime.now(timezone.utc).isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT users.user_id, users.name, users.email
        FROM login_sessions
        JOIN users
        ON login_sessions.user_id = users.user_id
        WHERE login_sessions.token_hash = ?
        AND login_sessions.expires_at > ?
    """, (token_hash, current_time))

    user = cursor.fetchone()

    connection.close()

    if user:

        return {
            "user_id": user[0],
            "name": user[1],
            "email": user[2]
        }

    return None


# Revoke a login session during logout
def revoke_login_session(session_token):

    if not session_token:
        return

    token_hash = hashlib.sha256(
        session_token.encode("utf-8")
    ).hexdigest()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM login_sessions
        WHERE token_hash = ?
    """, (token_hash,))

    connection.commit()
    connection.close()

# Register a new buyer
def register_user(name, email, password):

    connection = get_connection()
    cursor = connection.cursor()

    # Check whether email already exists
    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        connection.close()
        return False, "Email already registered!"

    # Hash the password
    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    # Insert buyer details
    cursor.execute("""
        INSERT INTO users (name, email, password_hash)
        VALUES (?, ?, ?)
    """, (
        name,
        email,
        hashed_password.decode("utf-8")
    ))

    connection.commit()
    connection.close()

    return True, "Registration successful!"


# Login existing buyer
def login_user(email, password):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_id, name, email, password_hash
        FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    connection.close()

    if user is None:
        return None

    stored_password = user[3].encode("utf-8")

    if bcrypt.checkpw(
        password.encode("utf-8"),
        stored_password
    ):

        return {
            "user_id": user[0],
            "name": user[1],
            "email": user[2]
        }

    return None


# Get buyer details using user ID
def get_user_by_id(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_id, name, email
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    user = cursor.fetchone()

    connection.close()

    if user:
        return {
            "user_id": user[0],
            "name": user[1],
            "email": user[2]
        }

    return None


# Change buyer password
def change_password(user_id, current_password, new_password):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT password_hash
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    user = cursor.fetchone()

    if user is None:
        connection.close()
        return False, "User not found!"

    stored_password = user[0].encode("utf-8")

    if not bcrypt.checkpw(
        current_password.encode("utf-8"),
        stored_password
    ):
        connection.close()
        return False, "Current password is incorrect!"

    hashed_password = bcrypt.hashpw(
        new_password.encode("utf-8"),
        bcrypt.gensalt()
    )

    cursor.execute("""
        UPDATE users
        SET password_hash = ?
        WHERE user_id = ?
    """, (
        hashed_password.decode("utf-8"),
        user_id
    ))

    connection.commit()
    connection.close()

    return True, "Password changed successfully!"
