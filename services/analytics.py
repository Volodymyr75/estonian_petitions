import os

# Fix for Vercel/Lambda where HOME might be empty or read-only
if os.environ.get("VERCEL") == "1" or not os.environ.get("HOME"):
    os.environ["HOME"] = "/tmp"

import duckdb

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), 'petitions.duckdb'))

def get_db_connection():
    # Vercel serverless functions need a writable home directory (/tmp)
    config = {'home_directory': '/tmp'}
    if DB_PATH.startswith("md:"):
        return duckdb.connect(DB_PATH, config=config)
    return duckdb.connect(DB_PATH, read_only=True, config=config)

def get_overview_kpis():
    """Retrieve high-level KPIs."""
    con = get_db_connection()
    try:
        query = """
        SELECT 
            COUNT(*) as total_initiatives,
            SUM(CASE WHEN phase NOT IN ('archived', 'rejected') THEN 1 ELSE 0 END) as active_initiatives,
            SUM(signatures_count) as total_signatures
        FROM initiatives
        """
        res = con.execute(query)
        try:
            data = res.df().to_dict(orient='records')
            return data[0] if data else {}
        except Exception:
            columns = [col[0] for col in res.description]
            rows = res.fetchall()
            return dict(zip(columns, rows[0])) if rows else {}
    finally:
        con.close()

def get_trending_initiatives(limit: int = 5):
    """Retrieve trending initiatives based on signature count."""
    con = get_db_connection()
    try:
        query = """
        SELECT id, title, phase, signatures_count, url
        FROM initiatives
        WHERE phase = 'sign'
        ORDER BY signatures_count DESC
        LIMIT ?
        """
        res = con.execute(query, [limit])
        try:
            return res.df().to_dict(orient='records')
        except Exception:
            columns = [col[0] for col in res.description]
            return [dict(zip(columns, row)) for row in res.fetchall()]
    finally:
        con.close()

def get_phase_distribution():
    """Retrieve distribution of initiatives across different phases."""
    con = get_db_connection()
    try:
        query = """
        SELECT phase, count(*) as count 
        FROM initiatives 
        GROUP BY phase 
        ORDER BY count DESC
        """
        res = con.execute(query)
        try:
            return res.df().to_dict(orient='records')
        except Exception:
            columns = [col[0] for col in res.description]
            return [dict(zip(columns, row)) for row in res.fetchall()]
    finally:
        con.close()

def get_recent_summary():
    """Retrieve recent platform activity summary."""
    con = get_db_connection()
    try:
        # 1. New initiatives in last 30 days
        q1 = "SELECT count(*) FROM initiatives WHERE created_at >= current_date() - interval 30 day"
        new_count = con.execute(q1).fetchone()[0]

        # 2. Latest event
        q2 = "SELECT event_title, actor, event_date FROM initiative_events ORDER BY event_date DESC LIMIT 1"
        latest_event = con.execute(q2).fetchone()
        
        event_dict = None
        if latest_event:
            event_dict = {
                "title": latest_event[0],
                "actor": latest_event[1],
                "date": latest_event[2].isoformat() if hasattr(latest_event[2], 'isoformat') else latest_event[2]
            }

        return {
            "new_in_30_days": new_count,
            "latest_event": event_dict
        }
    finally:
        con.close()
