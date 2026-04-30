from services.analytics import get_trending_initiatives
import os
import json

with open('.env') as f:
    for line in f:
        if line.startswith('MOTHERDUCK_TOKEN='):
            os.environ['MOTHERDUCK_TOKEN'] = line.strip().split('=', 1)[1]
os.environ['DB_PATH'] = 'md:'
from services.analytics import get_trending_initiatives

res = get_trending_initiatives(limit=5)
for r in res:
    print(r['title'], "Velocity:", r['velocity'], "Signatures:", r['signatures_count'])
