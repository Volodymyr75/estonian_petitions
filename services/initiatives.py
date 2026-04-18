import os
import duckdb

try:
    import pandas as pd
except ImportError:
    pass

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), 'petitions.duckdb'))

def get_db_connection():
    # Vercel serverless functions need a writable home directory (/tmp)
    config = {'home_directory': '/tmp'}
    if DB_PATH.startswith("md:"):
        return duckdb.connect(DB_PATH, config=config)
    return duckdb.connect(DB_PATH, read_only=True, config=config)

def get_active_initiatives():
    """Retrieve all active initiatives."""
    con = get_db_connection()
    try:
        query = """
        SELECT id, slug, title, target_type, target_name, phase, status, 
               deadline_at, signatures_count, url, updated_at
        FROM initiatives
        WHERE phase NOT IN ('archived', 'rejected')
        ORDER BY signatures_count DESC
        """
        res = con.execute(query)
        try:
            return res.df().to_dict(orient='records')
        except Exception:
            # Fallback if pandas is not installed
            columns = [col[0] for col in res.description]
            return [dict(zip(columns, row)) for row in res.fetchall()]
    finally:
        con.close()

def get_initiative_timeline(initiative_id: str):
    """Retrieve event timeline for a specific initiative."""
    con = get_db_connection()
    try:
        query = """
        SELECT event_id, event_type, event_title, event_date, actor
        FROM initiative_events
        WHERE initiative_id = ?
        ORDER BY event_date ASC
        """
        res = con.execute(query, [initiative_id])
        try:
            return res.df().to_dict(orient='records')
        except Exception:
            columns = [col[0] for col in res.description]
            return [dict(zip(columns, row)) for row in res.fetchall()]
    finally:
        con.close()
