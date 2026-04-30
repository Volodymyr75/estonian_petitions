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

# Check ingested_at dates
res['ingested_at_stats'] = con.execute("SELECT min(ingested_at), max(ingested_at) FROM initiatives").fetchone()
res['created_at_stats'] = con.execute("SELECT count(created_at), min(created_at), max(created_at) FROM initiatives").fetchone()

# Check snapshots for top initiatives
q_top = """
SELECT i.title, list(s.signatures_count ORDER BY s.snapshot_date ASC) as history, list(s.snapshot_date ORDER BY s.snapshot_date ASC) as dates
FROM initiatives i
JOIN initiative_snapshots s ON s.initiative_id = i.id
WHERE i.title LIKE '%abielu määratlus%' OR i.title LIKE '%Kersti Kaljulaid%'
GROUP BY i.title
"""
res['top_history'] = con.execute(q_top).fetchall()

# Check distinct signature values for the top one
q_distinct = """
SELECT count(distinct s.signatures_count) 
FROM initiative_snapshots s
JOIN initiatives i ON s.initiative_id = i.id
WHERE i.title LIKE '%abielu määratlus%'
"""
res['distinct_votes'] = con.execute(q_distinct).fetchone()[0]

print(json.dumps(res, default=json_serial, indent=2))
