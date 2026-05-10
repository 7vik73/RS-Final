"""Small SQLite helper module for ResumeIQ.

The project intentionally uses simple SQL statements instead of an ORM so the
database layer is easy to explain during an academic viva.
"""

import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "database" / "database.db"


def get_connection():
    """Return a SQLite connection with rows accessible like dictionaries."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    """Create all project tables if they do not already exist."""
    with get_connection() as connection:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                required_skills TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                raw_text TEXT NOT NULL,
                cleaned_text TEXT NOT NULL,
                email TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                skills TEXT DEFAULT '',
                sections TEXT DEFAULT '{}',
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                candidate_name TEXT NOT NULL,
                semantic_score REAL DEFAULT 0,
                skill_score REAL DEFAULT 0,
                experience_score REAL DEFAULT 0,
                project_score REAL DEFAULT 0,
                resume_strength REAL DEFAULT 0,
                final_score REAL DEFAULT 0,
                overlap_skills TEXT DEFAULT '',
                missing_skills TEXT DEFAULT '',
                status TEXT DEFAULT 'Pending',
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resumes(id),
                FOREIGN KEY (job_id) REFERENCES jobs(id)
            )
            """
        )

        connection.commit()


def fetch_all(query, params=()):
    """Run a SELECT query and return all rows."""
    with get_connection() as connection:
        return connection.execute(query, params).fetchall()


def fetch_one(query, params=()):
    """Run a SELECT query and return one row."""
    with get_connection() as connection:
        return connection.execute(query, params).fetchone()


def execute(query, params=()):
    """Run an INSERT/UPDATE/DELETE query and return the inserted row id."""
    with get_connection() as connection:
        cursor = connection.execute(query, params)
        connection.commit()
        return cursor.lastrowid
