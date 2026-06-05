import os
import duckdb

with open('.env') as f:
    for line in f:
        if line.startswith('MOTHERDUCK_TOKEN='):
            os.environ['MOTHERDUCK_TOKEN'] = line.strip().split('=', 1)[1]
os.environ['DB_PATH'] = 'md:'

from services.analytics import get_overview_kpis, get_trending_initiatives, get_stalled_initiatives, get_recent_summary

print("Testing get_overview_kpis...")
try:
    print(get_overview_kpis())
except Exception as e:
    print("FAILED:", e)

print("Testing get_trending_initiatives...")
try:
    print(len(get_trending_initiatives()))
except Exception as e:
    print("FAILED:", e)

print("Testing get_stalled_initiatives...")
try:
    print(len(get_stalled_initiatives()))
except Exception as e:
    print("FAILED:", e)

print("Testing get_recent_summary...")
try:
    print(get_recent_summary())
except Exception as e:
    print("FAILED:", e)
