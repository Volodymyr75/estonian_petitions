import duckdb
import os
import json
import datetime

def json_serial(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

with open('.env') as f:
    for line in f:
        if line.startswith('MOTHERDUCK_TOKEN='):
            os.environ['MOTHERDUCK_TOKEN'] = line.strip().split('=', 1)[1]

con = duckdb.connect("md:")
con.execute("USE estonia_petitions")

res = {}
try:
    res['max_created_at'] = con.execute("SELECT max(created_at) FROM initiatives").fetchone()[0]
    res['max_updated_at'] = con.execute("SELECT max(updated_at) FROM initiatives").fetchone()[0]
    res['recent_count'] = con.execute("SELECT count(*) FROM initiatives WHERE created_at >= current_date() - interval 30 day").fetchone()[0]
    res['max_snapshot'] = con.execute("SELECT max(snapshot_date) FROM initiative_snapshots").fetchone()[0]
    res['latest_event'] = con.execute("SELECT event_title, actor, event_date FROM initiative_events ORDER BY event_date DESC LIMIT 1").fetchone()
    res['latest_initiative'] = con.execute("SELECT title, created_at FROM initiatives WHERE created_at IS NOT NULL ORDER BY created_at DESC LIMIT 1").fetchone()
except Exception as e:
    res['error'] = str(e)

print(json.dumps(res, default=json_serial, indent=2))
