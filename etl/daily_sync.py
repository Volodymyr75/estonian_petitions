import os
import sys
import time
from datetime import datetime

# Fix for DuckDB in serverless/container environments (GitHub Actions/Vercel)
# DuckDB needs a writable home directory for extensions and configuration.
if os.environ.get("GITHUB_ACTIONS") == "true" or not os.environ.get("HOME"):
    os.environ["HOME"] = "/tmp"

import duckdb

# Add project root to path for direct script execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from etl.clients.rahvaalgatus import RahvaalgatusClient
from etl.clients.riigikogu import RiigikoguClient

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), 'petitions.duckdb'))

def init_db(con):
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    con.execute(schema_sql)

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
    except Exception:
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        except Exception:
            return None

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
    
    delete_initiative_query = "DELETE FROM initiatives WHERE id = ?"
    insert_initiative_query = """
    INSERT INTO initiatives (
        id, slug, title, target_type, target_name, phase, status, 
        deadline_at, signatures_count, source, updated_at, ingested_at
    ) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    delete_snapshot_query = "DELETE FROM initiative_snapshots WHERE initiative_id = ? AND snapshot_date = ?"
    insert_snapshot_query = """
    INSERT INTO initiative_snapshots (initiative_id, snapshot_date, signatures_count, phase, status, source)
    VALUES (?, ?, ?, ?, ?, ?)
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

        # MotherDuck-compatible upsert: DELETE then INSERT
        con.execute(delete_initiative_query, [init_id])
        con.execute(insert_initiative_query, (
            init_id, slug, title, 'government', target, phase, status,
            deadline_parsed, sig_count, 'rahvaalgatus', now, now
        ))
        
        # Daily snapshot: DELETE then INSERT
        con.execute(delete_snapshot_query, [init_id, today])
        con.execute(insert_snapshot_query, (
            init_id, today, sig_count, phase, status, 'rahvaalgatus'
        ))

    print(f"Synced {len(initiatives)} initiatives.")

    print("Fetching events from Rahvaalgatus API...")
    events = client.get_events()
    
    delete_event_query = "DELETE FROM initiative_events WHERE event_id = ?"
    insert_event_query = """
    INSERT INTO initiative_events (event_id, initiative_id, event_type, event_title, event_date, actor, source, ingested_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    for event in events:
        eid = event.get('id', 'unknown')
        init_id = event.get('initiativeId')
        if not init_id: continue
        unique_event_id = f"{eid}_{init_id}"
        
        title = event.get('title')
        occurred = parse_datetime(event.get('occurredAt'))
        
        # Only insert if not already present (events are immutable)
        existing = con.execute("SELECT 1 FROM initiative_events WHERE event_id = ?", [unique_event_id]).fetchone()
        if not existing:
            con.execute(insert_event_query, (
                unique_event_id, init_id, eid, title, occurred, 'rahvaalgatus', 'rahvaalgatus', now
            ))
        
    print(f"Synced {len(events)} events.")
    
    print("Updating created_at for initiatives based on earliest events...")
    con.execute("""
        UPDATE initiatives 
        SET created_at = (
            SELECT min(event_date) 
            FROM initiative_events 
            WHERE initiative_id = initiatives.id
        )
        WHERE created_at IS NULL;
    """)
    
    con.close()

def sync_riigikogu():
    client = RiigikoguClient()
    con = duckdb.connect(DB_PATH)
    init_db(con) # ensure tables exist
    
    print("Fetching collective addresses from Riigikogu...")
    petitions = client.get_collective_addresses()
    print(f"Fetched {len(petitions)} collective addresses.")
    
    now = datetime.now()
    
    # Pre-compiled queries
    delete_petition = "DELETE FROM riigikogu_petitions WHERE riigikogu_uuid = ?"
    insert_petition = """
    INSERT INTO riigikogu_petitions (
        riigikogu_uuid, initiative_id, reference, title, sender, submitting_date,
        compliance_deadline, responsible_committee, current_status, current_status_date,
        last_committee_decision, has_draft, draft_uuid, draft_title, draft_status, ingested_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    delete_statuses = "DELETE FROM riigikogu_petition_statuses WHERE riigikogu_uuid = ?"
    insert_status = """
    INSERT INTO riigikogu_petition_statuses (
        status_id, riigikogu_uuid, status_date, status_code, status_value,
        committee_decision_code, committee_decision_value, ingested_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    delete_voting = "DELETE FROM riigikogu_votings WHERE voting_id = ?"
    insert_voting = """
    INSERT INTO riigikogu_votings (
        voting_id, initiative_id, draft_uuid, title, description, session_date, result,
        in_favor, against, neutral, abstained, present, absent, source, updated_at, ingested_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    delete_voting_details = "DELETE FROM riigikogu_voting_details WHERE voting_id = ?"
    insert_voting_detail = """
    INSERT INTO riigikogu_voting_details (
        voting_id, member_name, faction, vote_value, source, ingested_at
    ) VALUES (?, ?, ?, ?, ?, ?)
    """

    for pet in petitions:
        uuid = pet.get('uuid')
        init_id = pet.get('senderReference') # Rahvaalgatus UUID
        ref = pet.get('reference')
        title = pet.get('title')
        sender = pet.get('sender')
        submitting_date = parse_date(pet.get('submittingDate'))
        deadline = parse_date(pet.get('complianceDeadline'))
        
        # Responsible committee
        committees = pet.get('responsibleCommittee') or []
        active_committee = next((c.get('name') for c in committees if c.get('active')), None)
        if not active_committee and committees:
            active_committee = committees[0].get('name')
            
        # Parse status timeline
        statuses = pet.get('statuses') or []
        statuses_sorted = sorted(statuses, key=lambda s: s.get('date') or '')
        
        current_status = None
        current_status_date = None
        last_committee_decision = None
        
        if statuses_sorted:
            last_status = statuses_sorted[-1]
            current_status = last_status.get('status', {}).get('value')
            current_status_date = parse_date(last_status.get('date'))
            
            # Find the last committee decision
            for s in reversed(statuses_sorted):
                dec = s.get('committeeDecision')
                if dec:
                    last_committee_decision = dec.get('value')
                    break
        
        # Check for related draft
        has_draft = False
        draft_uuid = None
        draft_title = None
        draft_status = None
        
        volumes = pet.get('relatedVolumes') or []
        for vol in volumes:
            if vol.get('draft') or vol.get('volumeType') == 'eelnou':
                has_draft = True
                draft_uuid = vol.get('uuid')
                draft_title = vol.get('title')
                break
                
        if has_draft and draft_uuid:
            print(f"Fetching details for draft: {draft_title} ({draft_uuid})...")
            try:
                time.sleep(1.0) # Be nice to the API
                draft_details = client.get_draft_details(draft_uuid)
                draft_status = draft_details.get('activeDraftStatus')
                
                # Parse readings and votings
                readings = draft_details.get('readings') or []
                for reading in readings:
                    events = reading.get('proceedingEvents') or []
                    for event in events:
                        votings = event.get('votings') or []
                        for voting in votings:
                            voting_uuid = voting.get('uuid')
                            voting_desc = voting.get('description')
                            
                            print(f"  Fetching voting details for: {voting_desc} ({voting_uuid})...")
                            time.sleep(1.0) # Be nice to the API
                            vote_details = client.get_voting_details(voting_uuid)
                            
                            # Parse voting counts
                            in_favor = vote_details.get('inFavor') or 0
                            against = vote_details.get('against') or 0
                            neutral = vote_details.get('neutral') or 0
                            abstained = vote_details.get('abstained') or 0
                            present = vote_details.get('present') or 0
                            absent = vote_details.get('absent') or 0
                            vote_date = parse_datetime(vote_details.get('startDateTime'))
                            
                            # Determine result
                            result = 'PASSED' if in_favor > against else 'FAILED'
                            
                            # Upsert voting
                            con.execute(delete_voting, [voting_uuid])
                            con.execute(insert_voting, (
                                voting_uuid, init_id, draft_uuid, draft_title, voting_desc,
                                vote_date, result, in_favor, against, neutral, abstained, present, absent,
                                'riigikogu', now, now
                            ))
                            
                            # Upsert voting details (voters)
                            con.execute(delete_voting_details, [voting_uuid])
                            voters = vote_details.get('voters') or []
                            for voter in voters:
                                member_name = voter.get('fullName')
                                faction = voter.get('faction', {}).get('name')
                                vote_value = voter.get('decision', {}).get('value')
                                con.execute(insert_voting_detail, (
                                    voting_uuid, member_name, faction, vote_value, 'riigikogu', now
                                ))
                                
            except Exception as e:
                print(f"  Error fetching draft/voting details for {draft_uuid}: {e}")
                
        # Upsert petition
        con.execute(delete_petition, [uuid])
        con.execute(insert_petition, (
            uuid, init_id, ref, title, sender, submitting_date, deadline, active_committee,
            current_status, current_status_date, last_committee_decision, has_draft,
            draft_uuid, draft_title, draft_status, now
        ))
        
        # Upsert status timeline
        con.execute(delete_statuses, [uuid])
        for idx, s in enumerate(statuses):
            s_date = parse_date(s.get('date'))
            s_code = s.get('status', {}).get('code')
            s_value = s.get('status', {}).get('value')
            dec_code = s.get('committeeDecision', {}).get('code') if s.get('committeeDecision') else None
            dec_value = s.get('committeeDecision', {}).get('value') if s.get('committeeDecision') else None
            
            status_id = f"{uuid}_{s_code or 'UNKNOWN'}_{idx}"
            con.execute(insert_status, (
                status_id, uuid, s_date, s_code, s_value, dec_code, dec_value, now
            ))
            
    con.close()
    print(f"Synced {len(petitions)} Riigikogu collective addresses.")

if __name__ == "__main__":
    try:
        print(f"Starting sync at {datetime.now()}")
        if DB_PATH.startswith("md:"):
            print("Connecting to MotherDuck cloud database...")
        else:
            print(f"Connecting to local database: {DB_PATH}")
            
        print("--- Syncing Rahvaalgatus ---")
        sync_initiatives()
        print("--- Syncing Riigikogu ---")
        try:
            sync_riigikogu()
        except Exception as riigikogu_err:
            print(f"\n⚠️ WARNING: Riigikogu sync failed, but continuing with Rahvaalgatus data. Error: {riigikogu_err}")
            import traceback
            traceback.print_exc()
        print("Sync completed successfully.")
    except Exception as e:
        print(f"\nERROR DURING SYNC: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
