import duckdb
query = """
SELECT 
    i.id,
    i.title,
    i.signatures_count as current_signatures,
    (
        SELECT list(signatures_count) 
        FROM (
            SELECT signatures_count 
            FROM initiative_snapshots s 
            WHERE s.initiative_id = i.id 
            ORDER BY snapshot_date ASC
        )
    ) as history
FROM initiatives i
WHERE i.phase = 'sign'
ORDER BY i.signatures_count DESC
LIMIT 2
"""
res = duckdb.connect('petitions.duckdb', read_only=True).execute(query).fetchall()
print(res)
