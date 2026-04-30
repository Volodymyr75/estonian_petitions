import duckdb
import os

with open('.env') as f:
    for line in f:
        if line.startswith('MOTHERDUCK_TOKEN='):
            os.environ['MOTHERDUCK_TOKEN'] = line.strip().split('=', 1)[1]

con = duckdb.connect("md:")
con.execute("USE estonia_petitions")

# Update created_at with the earliest event date
query = """
UPDATE initiatives 
SET created_at = (
    SELECT min(event_date) 
    FROM initiative_events 
    WHERE initiative_id = initiatives.id
)
WHERE created_at IS NULL;
"""
con.execute(query)
print("Updated created_at in Motherduck!")
