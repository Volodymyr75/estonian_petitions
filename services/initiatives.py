import os

# Fix for Vercel/Lambda where HOME might be empty or read-only
if os.environ.get("VERCEL") == "1" or not os.environ.get("HOME"):
    os.environ["HOME"] = "/tmp"

import duckdb

try:
    import pandas as pd
except ImportError:
    pass

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), 'petitions.duckdb'))

def get_db_connection():
    if DB_PATH.startswith("md:"):
        return duckdb.connect(DB_PATH)
    return duckdb.connect(DB_PATH, read_only=True)

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
            records = res.df().to_dict(orient='records')
        except Exception:
            columns = [col[0] for col in res.description]
            records = [dict(zip(columns, row)) for row in res.fetchall()]
            
        for r in records:
            if 'event_date' in r and hasattr(r['event_date'], 'isoformat'):
                r['event_date'] = r['event_date'].isoformat()
        return records
    finally:
        con.close()
