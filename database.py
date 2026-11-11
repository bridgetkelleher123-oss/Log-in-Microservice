"""SQLite persistence for the Song Similarity authentication service."""
import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "users.db"


def get_connection():
    """Open the project database and make rows accessible by column name."""
    connection = sqlite3.connect(DATABASE, timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the user table if it does not already exist."""
    connection = get_connection()
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()
    finally:
        connection.close()


def create_user(username, password_hash):
    """Store a new user and return the newly created database ID."""
    connection = get_connection()
    try:
        cursor = connection.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def get_user_by_username(username):
    """Find a user by username; return None if no record matches."""
    connection = get_connection()
    try:
        return connection.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    finally:
        connection.close()
