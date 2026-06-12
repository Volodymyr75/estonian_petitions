import os

# Fix for Vercel/Lambda where HOME might be empty or read-only
if os.environ.get("VERCEL") == "1" or not os.environ.get("HOME"):
    os.environ["HOME"] = "/tmp"

import duckdb

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), 'petitions.duckdb'))

def get_db_connection():
    if DB_PATH.startswith("md:"):
        return duckdb.connect(DB_PATH)
    return duckdb.connect(DB_PATH, read_only=True)

def get_overview_kpis():
    """Retrieve high-level KPIs."""
    con = get_db_connection()
    try:
        query = """
        SELECT 
            COUNT(*) as total_initiatives,
            SUM(CASE WHEN phase NOT IN ('archived', 'rejected') THEN 1 ELSE 0 END) as active_initiatives,
            SUM(CASE WHEN signatures_count >= 1000 OR phase IN ('parliament', 'government', 'done') THEN 1 ELSE 0 END) as threshold_passed,
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
                SELECT list({'date': snapshot_date::VARCHAR, 'value': signatures_count}) 
                FROM (
                    SELECT snapshot_date, signatures_count 
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
            history = r.get('history_7d')
            import numpy as np
            if isinstance(history, np.ndarray):
                history = history.tolist()
            if history is None:
                history = []
            
            # Ensure history is a normal list of dicts
            if len(history) > 0 and isinstance(history[0], str):
                pass # just in case, but duckdb usually returns dicts here
                
            if len(history) == 0 and r.get('signatures_count'):
                history = [{'date': 'Now', 'value': r['signatures_count']}]
                
            # Guarantee history ends with the most live data
            if len(history) > 0 and history[-1].get('value') != r['signatures_count']:
                history.append({'date': 'Now', 'value': r['signatures_count']})
                
            r['history_array'] = history
            
            # Calculate velocity
            if len(history) >= 2:
                growth = history[-1]['value'] - history[0]['value']
                # Count days based on dates or fallback to total history duration
                days = (len(history) - 1)
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

def get_approaching_deadline_initiatives(limit: int = 5):
    """Retrieve initiatives in sign phase that are approaching deadline."""
    con = get_db_connection()
    try:
        query = """
        SELECT 
            i.id, 
            i.title, 
            i.phase, 
            i.signatures_count, 
            i.url,
            i.deadline_at,
            DATE_DIFF('day', CURRENT_DATE(), CAST(i.deadline_at AS DATE)) as days_left,
            (
                SELECT list({'date': snapshot_date::VARCHAR, 'value': signatures_count}) 
                FROM (
                    SELECT snapshot_date, signatures_count 
                    FROM initiative_snapshots s 
                    WHERE s.initiative_id = i.id 
                      AND snapshot_date >= (SELECT max(snapshot_date) FROM initiative_snapshots) - interval 7 day
                    ORDER BY snapshot_date ASC
                )
            ) as history_7d
        FROM initiatives i
        WHERE i.phase = 'sign' AND i.signatures_count < 1000 AND i.deadline_at IS NOT NULL
          AND DATE_DIFF('day', CURRENT_DATE(), CAST(i.deadline_at AS DATE)) >= 0
        ORDER BY days_left ASC
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
            
            # Convert timestamp to string if needed
            if hasattr(r.get('deadline_at'), 'isoformat'):
                r['deadline_at'] = r['deadline_at'].isoformat()
                
            # Process history array
            history = r.get('history_7d')
            import numpy as np
            if isinstance(history, np.ndarray):
                history = history.tolist()
            if history is None:
                history = []
            
            if len(history) == 0 and r.get('signatures_count'):
                history = [{'date': 'Now', 'value': r['signatures_count']}]
                
            if len(history) > 0 and history[-1].get('value') != r['signatures_count']:
                history.append({'date': 'Now', 'value': r['signatures_count']})
                
            r['history_array'] = history
            
            # missing signatures
            r['missing_sigs'] = max(0, 1000 - r.get('signatures_count', 0))
            
            r.pop('history_7d', None)
        
        return records
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
        q1 = "SELECT count(*) FROM initiatives WHERE created_at >= (SELECT max(created_at) FROM initiatives) - interval 30 day"
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

def get_stalled_and_recent_successes(limit_stalled=5, limit_recent=5):
    """Retrieve longest stalled initiatives and recently completed ones."""
    con = get_db_connection()
    try:
        # 1. Stalled
        stalled_query = """
        SELECT 
            id, 
            title, 
            phase, 
            url,
            signatures_count,
            DATE_DIFF('month', CAST(coalesce(created_at, ingested_at) AS DATE), CURRENT_DATE()) as months_pending
        FROM initiatives
        WHERE phase IN ('parliament', 'government')
        ORDER BY coalesce(created_at, ingested_at) ASC NULLS LAST
        LIMIT ?
        """
        res_stalled = con.execute(stalled_query, [limit_stalled])
        try:
            stalled_records = res_stalled.df().to_dict(orient='records')
        except Exception:
            columns = [col[0] for col in res_stalled.description]
            stalled_records = [dict(zip(columns, row)) for row in res_stalled.fetchall()]
            
        # 2. Recent Successes
        recent_query = """
        SELECT 
            id, 
            title, 
            phase, 
            url,
            signatures_count,
            DATE_DIFF('month', CAST(coalesce(created_at, ingested_at) AS DATE), CAST(updated_at AS DATE)) as months_to_success
        FROM initiatives
        WHERE phase = 'done'
        ORDER BY updated_at DESC NULLS LAST
        LIMIT ?
        """
        res_recent = con.execute(recent_query, [limit_recent])
        try:
            recent_records = res_recent.df().to_dict(orient='records')
        except Exception:
            columns = [col[0] for col in res_recent.description]
            recent_records = [dict(zip(columns, row)) for row in res_recent.fetchall()]

        for lst in [stalled_records, recent_records]:
            for r in lst:
                if not r.get('url'):
                    r['url'] = f"https://rahvaalgatus.ee/initiatives/{r['id']}"

        return {
            "stalled": stalled_records,
            "recent_successes": recent_records
        }
    finally:
        con.close()

def get_process_metrics():
    """Retrieve process analytics including phase durations, stalled status, and yearly activity pulse."""
    con = get_db_connection()
    try:
        # 1. Median days to 1000 signatures
        q_threshold = """
        SELECT median(date_diff('day', CAST(i.created_at AS DATE), CAST(e.event_date AS DATE)))
        FROM initiatives i
        JOIN initiative_events e ON i.id = e.initiative_id
        WHERE e.event_type = 'milestone-1000' AND i.created_at IS NOT NULL AND e.event_date >= i.created_at
        """
        val_threshold = con.execute(q_threshold).fetchone()[0]
        
        # 2. Median days from Created to Sent to Parliament
        q_parliament = """
        SELECT median(date_diff('day', CAST(i.created_at AS DATE), CAST(e.event_date AS DATE)))
        FROM initiatives i
        JOIN initiative_events e ON i.id = e.initiative_id
        WHERE e.event_type = 'sent-to-parliament' AND i.created_at IS NOT NULL AND e.event_date >= i.created_at
        """
        val_parliament = con.execute(q_parliament).fetchone()[0]

        # 3. Median days in Parliament before completion (done)
        q_done = """
        SELECT median(date_diff('day', CAST(e1.event_date AS DATE), CAST(COALESCE(e2.event_date, i.updated_at) AS DATE)))
        FROM initiatives i
        JOIN initiative_events e1 ON i.id = e1.initiative_id AND e1.event_type = 'sent-to-parliament'
        LEFT JOIN initiative_events e2 ON i.id = e2.initiative_id AND e2.event_type IN ('parliament-finished', 'finished-in-government')
        WHERE i.phase = 'done' AND COALESCE(e2.event_date, i.updated_at) >= e1.event_date
        """
        val_done = con.execute(q_done).fetchone()[0]

        # 4. Stalled statistics
        q_stalled = """
        SELECT 
            COUNT(*) as total_in_progress,
            SUM(CASE WHEN date_diff('month', CAST(coalesce(created_at, ingested_at) AS DATE), CURRENT_DATE()) >= 12 THEN 1 ELSE 0 END) as stalled_count
        FROM initiatives
        WHERE phase IN ('parliament', 'government')
        """
        res_stalled = con.execute(q_stalled).fetchone()
        total_in_progress = res_stalled[0] or 0
        stalled_count = res_stalled[1] or 0

        # 5. Yearly Activity Pulse
        q_pulse = """
        SELECT 
            strftime(event_date, '%Y') as year,
            count(*) as count
        FROM initiative_events
        WHERE event_date IS NOT NULL
        GROUP BY year
        ORDER BY year ASC
        """
        res_pulse = con.execute(q_pulse)
        try:
            yearly_pulse = res_pulse.df().to_dict(orient='records')
        except Exception:
            columns = [col[0] for col in res_pulse.description]
            yearly_pulse = [dict(zip(columns, row)) for row in res_pulse.fetchall()]

        return {
            "median_days_to_threshold": round(val_threshold) if val_threshold is not None else None,
            "median_days_to_parliament": round(val_parliament) if val_parliament is not None else None,
            "median_days_in_parliament": round(val_done) if val_done is not None else None,
            "total_in_progress": total_in_progress,
            "stalled_count": stalled_count,
            "stalled_ratio": round((stalled_count / total_in_progress) * 100, 1) if total_in_progress > 0 else 0.0,
            "yearly_pulse": yearly_pulse
        }
    finally:
        con.close()

