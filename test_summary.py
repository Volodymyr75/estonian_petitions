import os
import duckdb
from datetime import datetime, timedelta

with open('.env') as f:
    for line in f:
        if line.startswith('MOTHERDUCK_TOKEN='):
            os.environ['MOTHERDUCK_TOKEN'] = line.strip().split('=', 1)[1]

con = duckdb.connect("md:")
con.execute("USE estonia_petitions")

try:
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    query = """
    SELECT 
        COUNT(*) as total_initiatives,
        SUM(CASE WHEN created_at >= ? THEN 1 ELSE 0 END) as new_last_30_days,
        SUM(CASE WHEN signatures_count >= 1000 OR phase IN ('parliament', 'government', 'done') THEN 1 ELSE 0 END) as threshold_passed,
        SUM(signatures_count) as total_signatures
    FROM initiatives
    """
    res = con.execute(query, [thirty_days_ago])
    print(res.df().to_dict(orient='records'))
except Exception as e:
    print("ERROR:", e)
