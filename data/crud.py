import sqlite3
import os

# Define the database path relative to the project root
# This ensures that both the CLI and GUI use the same file regardless of where they are started from.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "checkpoints.db")

def get_existing_threads(db_path=DB_PATH):
    """Read: Get all unique thread IDs from the database."""
    if not os.path.exists(db_path):
        return []
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        threads = [row[0] for row in cursor.fetchall()]
        conn.close()
        return threads
    except Exception:
        return []

def delete_thread(thread_id, db_path=DB_PATH):
    """Delete: Remove all checkpoints and writes for a specific thread."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        cursor.execute("DELETE FROM writes WHERE thread_id = ?", (thread_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting thread: {e}")
        return False

# Create and Update are handled by LangGraph's SqliteSaver, 
# but we can add helper methods here if we need custom metadata in the future.
