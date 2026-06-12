import os

# Fix for Vercel/Lambda where HOME might be empty or read-only
if os.environ.get("VERCEL") == "1" or not os.environ.get("HOME"):
    os.environ["HOME"] = "/tmp"

import duckdb
from datetime import datetime

try:
    import pandas as pd
except ImportError:
    pass

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), 'petitions.duckdb'))

def get_db_connection():
    if DB_PATH.startswith("md:"):
        return duckdb.connect(DB_PATH)
    return duckdb.connect(DB_PATH, read_only=True)

def json_serial(obj):
    if isinstance(obj, (datetime, datetime.date)):
        return obj.isoformat()
    return obj

def get_institutional_overview():
    """Retrieve summary KPIs for the institutional dashboard layer."""
    con = get_db_connection()
    try:
        # 1. KPI counts
        kpis = con.execute("""
            SELECT 
                COUNT(*) as total_petitions,
                SUM(CASE WHEN current_status = 'Menetlus lõpetatud' THEN 1 ELSE 0 END) as completed_petitions,
                SUM(CASE WHEN current_status != 'Menetlus lõpetatud' THEN 1 ELSE 0 END) as active_petitions,
                SUM(CASE WHEN has_draft = TRUE THEN 1 ELSE 0 END) as petitions_with_drafts
            FROM riigikogu_petitions
        """).fetchone()
        
        # 2. Status distribution
        status_res = con.execute("""
            SELECT current_status, COUNT(*) as count
            FROM riigikogu_petitions
            WHERE current_status IS NOT NULL
            GROUP BY current_status
            ORDER BY count DESC
        """).fetchall()
        status_dist = [{"status": row[0], "count": row[1]} for row in status_res]

        # 3. Decision outcomes
        decision_res = con.execute("""
            SELECT last_committee_decision, COUNT(*) as count
            FROM riigikogu_petitions
            WHERE last_committee_decision IS NOT NULL
            GROUP BY last_committee_decision
            ORDER BY count DESC
        """).fetchall()
        decision_dist = [{"decision": row[0], "count": row[1]} for row in decision_res]
        
        # 4. Committee breakdown
        committee_res = con.execute("""
            SELECT responsible_committee, COUNT(*) as count
            FROM riigikogu_petitions
            WHERE responsible_committee IS NOT NULL
            GROUP BY responsible_committee
            ORDER BY count DESC
        """).fetchall()
        committee_dist = [{"committee": row[0], "count": row[1]} for row in committee_res]

        return {
            "total_petitions": kpis[0] or 0,
            "completed_petitions": kpis[1] or 0,
            "active_petitions": kpis[2] or 0,
            "petitions_with_drafts": kpis[3] or 0,
            "status_distribution": status_dist,
            "decision_distribution": decision_dist,
            "committee_distribution": committee_dist
        }
    finally:
        con.close()

def get_mapped_initiatives():
    """Retrieve all civic initiatives that have reached parliament."""
    con = get_db_connection()
    try:
        query = """
        SELECT 
            rp.riigikogu_uuid,
            rp.initiative_id,
            COALESCE(i.title, rp.title) as title,
            COALESCE(i.slug, '') as slug,
            rp.reference,
            rp.sender,
            rp.submitting_date,
            rp.responsible_committee,
            rp.current_status,
            rp.current_status_date,
            rp.last_committee_decision,
            rp.has_draft,
            rp.draft_uuid,
            rp.draft_title,
            rp.draft_status,
            COALESCE(i.signatures_count, 0) as signatures_count
        FROM riigikogu_petitions rp
        LEFT JOIN initiatives i ON i.id = rp.initiative_id
        ORDER BY rp.submitting_date DESC
        """
        res = con.execute(query)
        try:
            records = res.df().to_dict(orient='records')
        except Exception:
            columns = [col[0] for col in res.description]
            records = [dict(zip(columns, row)) for row in res.fetchall()]
            
        for r in records:
            for key in ['submitting_date', 'current_status_date']:
                if key in r and hasattr(r[key], 'isoformat') and r[key] is not None:
                    r[key] = r[key].isoformat()
                    
        return records
    finally:
        con.close()

def get_petition_details_and_votings(initiative_id: str):
    """Retrieve timeline events, related draft details, and votings for a petition."""
    con = get_db_connection()
    try:
        # Get petition details
        pet_res = con.execute("""
            SELECT riigikogu_uuid, title, reference, submitting_date, responsible_committee, 
                   current_status, last_committee_decision, has_draft, draft_uuid, draft_title, draft_status
            FROM riigikogu_petitions
            WHERE initiative_id = ?
        """, [initiative_id]).fetchone()
        
        if not pet_res:
            return None
            
        columns = ['riigikogu_uuid', 'title', 'reference', 'submitting_date', 'responsible_committee',
                   'current_status', 'last_committee_decision', 'has_draft', 'draft_uuid', 'draft_title', 'draft_status']
        petition = dict(zip(columns, pet_res))
        
        for k in ['submitting_date']:
            if petition[k] and hasattr(petition[k], 'isoformat'):
                petition[k] = petition[k].isoformat()
                
        # Get petition status timeline
        timeline_res = con.execute("""
            SELECT status_date, status_code, status_value, committee_decision_value
            FROM riigikogu_petition_statuses
            WHERE riigikogu_uuid = ?
            ORDER BY status_date ASC
        """, [petition['riigikogu_uuid']]).fetchall()
        
        timeline = []
        for row in timeline_res:
            timeline.append({
                "date": row[0].isoformat() if hasattr(row[0], 'isoformat') else row[0],
                "status_code": row[1],
                "status_value": row[2],
                "committee_decision": row[3]
            })
            
        # Get votings
        votings = []
        if petition['has_draft'] and petition['draft_uuid']:
            voting_rows = con.execute("""
                SELECT voting_id, description, session_date, result, in_favor, against, neutral, abstained, present, absent
                FROM riigikogu_votings
                WHERE draft_uuid = ?
                ORDER BY session_date ASC
            """, [petition['draft_uuid']]).fetchall()
            
            for v_row in voting_rows:
                v_id = v_row[0]
                voting_obj = {
                    "voting_id": v_id,
                    "description": v_row[1],
                    "session_date": v_row[2].isoformat() if hasattr(v_row[2], 'isoformat') else v_row[2],
                    "result": v_row[3],
                    "in_favor": v_row[4],
                    "against": v_row[5],
                    "neutral": v_row[6],
                    "abstained": v_row[7],
                    "present": v_row[8],
                    "absent": v_row[9],
                    "factions": {}
                }
                
                # Fetch faction support
                faction_rows = con.execute("""
                    SELECT faction, vote_value, COUNT(*) as count
                    FROM riigikogu_voting_details
                    WHERE voting_id = ?
                    GROUP BY faction, vote_value
                """, [v_id]).fetchall()
                
                for f_row in faction_rows:
                    faction = f_row[0] or "Fraktsioonita"
                    vote_value = f_row[1]
                    count = f_row[2]
                    
                    if faction not in voting_obj['factions']:
                        voting_obj['factions'][faction] = {
                            "poolt": 0, "vastu": 0, "erapooletu": 0, "puudub": 0
                        }
                    
                    # Map Estonian API decision values to standard keys
                    key = "poolt"
                    if vote_value == "poolt" or vote_value == "POOLT":
                        key = "poolt"
                    elif vote_value == "vastu" or vote_value == "VASTU":
                        key = "vastu"
                    elif vote_value == "erapooletu" or vote_value == "ERAPOOLETU":
                        key = "erapooletu"
                    else:
                        key = "puudub"
                        
                    voting_obj['factions'][faction][key] += count
                    
                votings.append(voting_obj)
                
        return {
            "petition": petition,
            "timeline": timeline,
            "votings": votings
        }
    finally:
        con.close()
