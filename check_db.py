import duckdb
import os
import json
import datetime

def json_serial(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

DB_PATH = os.path.join(os.path.dirname(__file__), 'petitions.duckdb')
con = duckdb.connect(DB_PATH, read_only=True)

res = {}

# Max created_at
max_created = con.execute("SELECT max(created_at) FROM initiatives").fetchone()
res['max_created_at'] = max_created[0]

# Count in last 30 days
recent_count = con.execute("SELECT count(*) FROM initiatives WHERE created_at >= current_date() - interval 30 day").fetchone()
res['new_in_last_30_days'] = recent_count[0]

# Max snapshot_date
max_snapshot = con.execute("SELECT max(snapshot_date) FROM initiative_snapshots").fetchone()
res['max_snapshot_date'] = max_snapshot[0]

# Latest event
latest_event = con.execute("SELECT event_title, actor, event_date FROM initiative_events ORDER BY event_date DESC LIMIT 1").fetchone()
res['latest_event'] = latest_event

# Table counts
res['initiative_count'] = con.execute("SELECT count(*) FROM initiatives").fetchone()[0]
res['snapshot_count'] = con.execute("SELECT count(*) FROM initiative_snapshots").fetchone()[0]

print(json.dumps(res, default=json_serial, indent=2))
