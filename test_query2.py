import duckdb
query = """
SELECT id, title, phase, DATE_DIFF('day', CAST(updated_at AS DATE), CURRENT_DATE()) as days_stalled
FROM initiatives
WHERE phase NOT IN ('done', 'rejected', 'archived')
ORDER BY updated_at ASC
LIMIT 3
"""
res = duckdb.connect('petitions.duckdb', read_only=True).execute(query).fetchall()
print(res)
