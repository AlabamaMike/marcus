"""Session management for chat history."""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os


class SessionManager:
    """Manages chat sessions and message history using SQLite."""

    def __init__(self, db_path: str = "chat_sessions.db"):
        """Initialize the session manager with a database path."""
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                )
            """)

            conn.commit()

    def create_session(self, title: Optional[str] = None) -> int:
        """Create a new chat session.

        Args:
            title: Optional title for the session. If not provided, generates a default title.

        Returns:
            The ID of the newly created session.
        """
        if title is None:
            title = f"New Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (title) VALUES (?)",
                (title,)
            )
            conn.commit()
            return cursor.lastrowid

    def get_all_sessions(self) -> List[Dict]:
        """Get all chat sessions ordered by most recent first.

        Returns:
            List of session dictionaries with id, title, created_at, and updated_at.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, created_at, updated_at
                FROM sessions
                ORDER BY updated_at DESC
            """)

            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'id': row[0],
                    'title': row[1],
                    'created_at': row[2],
                    'updated_at': row[3]
                })

            return sessions

    def get_session(self, session_id: int) -> Optional[Dict]:
        """Get a specific session by ID.

        Args:
            session_id: The ID of the session to retrieve.

        Returns:
            Session dictionary or None if not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, created_at, updated_at FROM sessions WHERE id = ?",
                (session_id,)
            )
            row = cursor.fetchone()

            if row:
                return {
                    'id': row[0],
                    'title': row[1],
                    'created_at': row[2],
                    'updated_at': row[3]
                }
            return None

    def delete_session(self, session_id: int) -> bool:
        """Delete a session and all its messages.

        Args:
            session_id: The ID of the session to delete.

        Returns:
            True if successful, False otherwise.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False

    def save_message(self, session_id: int, role: str, content: str):
        """Save a message to a session.

        Args:
            session_id: The ID of the session.
            role: The role of the message sender ('user' or 'model').
            content: The message content (will be JSON-serialized if dict/list).
        """
        # Convert content to JSON string if it's a dict or list
        if isinstance(content, (dict, list)):
            content = json.dumps(content)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content)
            )
            # Update the session's updated_at timestamp
            cursor.execute(
                "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (session_id,)
            )
            conn.commit()

    def get_messages(self, session_id: int) -> List[Dict]:
        """Get all messages for a session.

        Args:
            session_id: The ID of the session.

        Returns:
            List of message dictionaries with role and content.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT role, content FROM messages
                   WHERE session_id = ?
                   ORDER BY created_at ASC""",
                (session_id,)
            )

            messages = []
            for row in cursor.fetchall():
                role, content = row
                # Try to parse JSON content back to dict/list
                try:
                    content = json.loads(content)
                except (json.JSONDecodeError, TypeError):
                    pass  # Keep as string if not valid JSON

                messages.append({
                    'role': role,
                    'content': content
                })

            return messages

    def update_session_title(self, session_id: int, title: str) -> bool:
        """Update the title of a session.

        Args:
            session_id: The ID of the session.
            title: The new title.

        Returns:
            True if successful, False otherwise.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE sessions SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (title, session_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False

    def generate_title_from_first_message(self, session_id: int) -> Optional[str]:
        """Generate a session title from the first user message.

        Args:
            session_id: The ID of the session.

        Returns:
            Generated title or None if no messages exist.
        """
        messages = self.get_messages(session_id)
        if messages:
            first_message = messages[0]
            content = first_message['content']

            # Extract text from content
            if isinstance(content, dict) and 'text' in content:
                text = content['text']
            elif isinstance(content, str):
                text = content
            else:
                text = str(content)

            # Truncate to reasonable length for title
            title = text[:50] + "..." if len(text) > 50 else text
            self.update_session_title(session_id, title)
            return title

        return None
