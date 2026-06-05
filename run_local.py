import os
with open('.env') as f:
    for line in f:
        if line.startswith('MOTHERDUCK_TOKEN='):
            os.environ['MOTHERDUCK_TOKEN'] = line.strip().split('=', 1)[1]
os.environ['DB_PATH'] = 'md:'

from api.index import app
from fastapi.testclient import TestClient

client = TestClient(app)

endpoints = ['/api/summary', '/api/trending', '/api/stalled', '/api/kpis', '/api/phases']
for e in endpoints:
    print(f"Testing {e}...")
    try:
        response = client.get(e)
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            print(response.text)
    except Exception as ex:
        print(f"Exception on {e}: {ex}")

