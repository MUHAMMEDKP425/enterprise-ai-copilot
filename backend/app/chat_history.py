import sqlite3
from pathlib import Path


# Store the database in the project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "chat_history.db"


def get_connection():
    """Create a connection to the chat history database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the conversations and messages tables."""
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                document_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
            )
        """)

        connection.commit()


def create_conversation(title, document_name=None):
    """Create a new conversation and return its ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO conversations (title, document_name)
            VALUES (?, ?)
            """,
            (title, document_name),
        )
        connection.commit()
        return cursor.lastrowid


def list_conversations():
    """Return conversations, newest activity first."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, document_name, created_at, updated_at
            FROM conversations
            ORDER BY updated_at DESC, id DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]


def save_message(conversation_id, role, content, sources=None):
    """Save a message and update the conversation activity time."""
    import json

    sources_json = json.dumps(sources or [])

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO messages (
                conversation_id, role, content, sources
            )
            VALUES (?, ?, ?, ?)
            """,
            (conversation_id, role, content, sources_json),
        )

        connection.execute(
            """
            UPDATE conversations
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (conversation_id,),
        )

        connection.commit()


def get_messages(conversation_id):
    """Return all messages belonging to a conversation."""
    import json

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT role, content, sources, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,),
        ).fetchall()

        messages = []

        for row in rows:
            message = dict(row)

            try:
                message["sources"] = json.loads(
                    message["sources"] or "[]"
                )
            except (json.JSONDecodeError, TypeError):
                message["sources"] = []

            messages.append(message)

        return messages


def delete_conversation(conversation_id):
    """Delete a conversation and its messages."""
    with get_connection() as connection:
        connection.execute("PRAGMA foreign_keys = ON")

        cursor = connection.execute(
            "DELETE FROM conversations WHERE id = ?",
            (conversation_id,),
        )

        connection.commit()
        return cursor.rowcount > 0


# Initialize the database when this module is imported
initialize_database()