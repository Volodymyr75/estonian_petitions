import os
import sys
from datetime import datetime

# Fix for DuckDB in serverless/container environments (GitHub Actions/Vercel)
# DuckDB needs a writable home directory for extensions and configuration.
if os.environ.get("GITHUB_ACTIONS") == "true" or not os.environ.get("HOME"):
    os.environ["HOME"] = "/tmp"

import duckdb

# Add project root to path for direct script execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from etl.clients.rahvaalgatus import RahvaalgatusClient

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), 'petitions.duckdb'))

def init_db(con):
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    con.execute(schema_sql)

def parse_datetime(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except Exception:
        return None

def sync_initiatives():
    client = RahvaalgatusClient()
    print("Fetching initiatives from Rahvaalgatus API...")
    initiatives = client.get_initiatives()
    
    con = duckdb.connect(DB_PATH)
    init_db(con)
    
    today = datetime.now().date().isoformat()
    now = datetime.now()
    
    upsert_query = """
    INSERT INTO initiatives (
        id, slug, title, target_type, target_name, phase, status, 
        deadline_at, signatures_count, source, updated_at, ingested_at
    ) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title,
        phase = EXCLUDED.phase,
        status = EXCLUDED.status,
        deadline_at = EXCLUDED.deadline_at,
        signatures_count = EXCLUDED.signatures_count,
        updated_at = EXCLUDED.updated_at
    """
    
    snapshot_query = """
    INSERT INTO initiative_snapshots (initiative_id, snapshot_date, signatures_count, phase, status, source)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT (initiative_id, snapshot_date) DO UPDATE SET
        signatures_count = EXCLUDED.signatures_count,
        phase = EXCLUDED.phase,
        status = EXCLUDED.status;
    """

    for item in initiatives:
        init_id = item.get('id')
        title = item.get('title')
        target = item.get('for')
        phase = item.get('phase')
        sig_count = item.get('signatureCount') or 0
        deadline = item.get('signingEndsAt')
        
        slug = item.get('slug', '')
        if not slug and title:
            slug = title.lower().replace(' ', '-').replace('/', '-')[:50]
            
        status = phase
        deadline_parsed = parse_datetime(deadline)

        con.execute(upsert_query, (
            init_id, slug, title, 'government', target, phase, status,
            deadline_parsed, sig_count, 'rahvaalgatus', now, now
        ))
        
        con.execute(snapshot_query, (
            init_id, today, sig_count, phase, status, 'rahvaalgatus'
        ))

    print(f"Synced {len(initiatives)} initiatives.")

    print("Fetching events from Rahvaalgatus API...")
    events = client.get_events()
    
    event_insert_query = """
    INSERT INTO initiative_events (event_id, initiative_id, event_type, event_title, event_date, actor, source, ingested_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT (event_id) DO NOTHING;
    """
    
    for event in events:
        eid = event.get('id', 'unknown')
        init_id = event.get('initiativeId')
        if not init_id: continue
        unique_event_id = f"{eid}_{init_id}"
        
        title = event.get('title')
        occurred = parse_datetime(event.get('occurredAt'))
        
        con.execute(event_insert_query, (
            unique_event_id, init_id, eid, title, occurred, 'rahvaalgatus', 'rahvaalgatus', now
        ))
        
    print(f"Synced {len(events)} events.")
    con.close()

if __name__ == "__main__":
    try:
        print(f"Starting sync at {datetime.now()}")
        if DB_PATH.startswith("md:"):
            print("Connecting to MotherDuck cloud database...")
        else:
            print(f"Connecting to local database: {DB_PATH}")
            
        sync_initiatives()
        print("Sync completed successfully.")
    except Exception as e:
        print(f"\nERROR DURING SYNC: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
