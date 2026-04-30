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
        SELECT 
            i.id, 
            i.title, 
            i.phase, 
            i.signatures_count, 
            i.url,
            (
                SELECT list(signatures_count) 
                FROM (
                    SELECT signatures_count 
                    FROM initiative_snapshots s 
                    WHERE s.initiative_id = i.id 
                      AND snapshot_date >= (SELECT max(snapshot_date) FROM initiative_snapshots) - interval 7 day
                    ORDER BY snapshot_date ASC
                )
            ) as history_7d
        FROM initiatives i
        WHERE i.phase = 'sign'
        """
        res = con.execute(query)
        try:
            records = res.df().to_dict(orient='records')
        except Exception:
            columns = [col[0] for col in res.description]
            records = [dict(zip(columns, row)) for row in res.fetchall()]
            
        for r in records:
            if not r.get('url'):
                r['url'] = f"https://rahvaalgatus.ee/initiatives/{r['id']}"
            
            # Process history array
            history = r.get('history_7d') or []
            if not history and r.get('signatures_count'):
                history = [r['signatures_count']]
                
            # Guarantee history ends with the most live data
            if history and history[-1] != r['signatures_count']:
                history.append(r['signatures_count'])
                
            r['history_array'] = history
            
            # Calculate velocity
            if len(history) >= 2:
                growth = history[-1] - history[0]
                days = len(history) - 1
                velocity = round(growth / days) if days > 0 else 0
            else:
                growth = 0
                velocity = 0
                
            r['growth_7d'] = growth
            r['velocity'] = velocity
            r.pop('history_7d', None)
        
        # Sort by velocity descending, then by total signatures
        records.sort(key=lambda x: (x.get('velocity', 0), x.get('signatures_count', 0)), reverse=True)
        
        return records[:limit]
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
        # 1. New initiatives in last 30 days (fallback to ingested_at if created_at is mostly null)
        q1 = "SELECT count(*) FROM initiatives WHERE coalesce(created_at, ingested_at) >= (SELECT max(coalesce(created_at, ingested_at)) FROM initiatives) - interval 30 day"
        new_count = con.execute(q1).fetchone()[0]

        # 2. Latest event
        # initiative_events might be stale, let's just get the last updated initiative
        q2 = "SELECT title, 'System', max(snapshot_date) FROM initiative_snapshots JOIN initiatives i ON i.id = initiative_id GROUP BY title ORDER BY max(snapshot_date) DESC LIMIT 1"
        latest_event = con.execute(q2).fetchone()
        
        event_dict = None
        if latest_event:
            event_dict = {
                "title": f"Update: {latest_event[0][:50]}...",
                "actor": latest_event[1],
                "date": latest_event[2].isoformat() if hasattr(latest_event[2], 'isoformat') else latest_event[2]
            }

        # 3. Last update time
        last_update_q = "SELECT max(snapshot_date) FROM initiative_snapshots"
        last_update = con.execute(last_update_q).fetchone()[0]

        return {
            "new_in_30_days": new_count,
            "latest_event": event_dict,
            "last_update": last_update.isoformat() if hasattr(last_update, 'isoformat') else last_update
        }
    finally:
        con.close()

def get_stalled_initiatives(limit: int = 5):
    """Retrieve initiatives stuck in a non-terminal phase with highest idle time."""
    con = get_db_connection()
    try:
        query = """
        SELECT 
            id, 
            title, 
            phase, 
            url,
            DATE_DIFF('day', CAST(updated_at AS DATE), CURRENT_DATE()) as days_stalled
        FROM initiatives
        WHERE phase NOT IN ('done', 'rejected', 'archived')
        ORDER BY updated_at ASC
        LIMIT ?
        """
        res = con.execute(query, [limit])
        try:
            records = res.df().to_dict(orient='records')
        except Exception:
            columns = [col[0] for col in res.description]
            records = [dict(zip(columns, row)) for row in res.fetchall()]
            
        for r in records:
            if not r.get('url'):
                r['url'] = f"https://rahvaalgatus.ee/initiatives/{r['id']}"
                
        return records
    finally:
        con.close()
