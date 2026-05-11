import os
import json
import duckdb
import numpy as np
from pathlib import Path

from services.analytics import (
    get_overview_kpis,
    get_trending_initiatives,
    get_recent_summary,
    get_stalled_initiatives
)

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def generate_static_json():
    print("Generating static JSON API data...")
    
    # Ensure public/api_data directory exists
    output_dir = Path("public/api_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. KPIs
    try:
        kpis = get_overview_kpis()
        with open(output_dir / "kpis.json", "w", encoding="utf-8") as f:
            json.dump(kpis, f, ensure_ascii=False, cls=NumpyEncoder)
        print("✅ kpis.json generated")
    except Exception as e:
        print(f"❌ Error generating kpis: {e}")

    # 2. Trending
    try:
        trending = get_trending_initiatives(limit=5)
        with open(output_dir / "trending.json", "w", encoding="utf-8") as f:
            json.dump(trending, f, ensure_ascii=False, cls=NumpyEncoder)
        print("✅ trending.json generated")
    except Exception as e:
        print(f"❌ Error generating trending: {e}")

    # 3. Summary
    try:
        summary = get_recent_summary()
        with open(output_dir / "summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, cls=NumpyEncoder)
        print("✅ summary.json generated")
    except Exception as e:
        print(f"❌ Error generating summary: {e}")

    # 4. Stalled
    try:
        stalled = get_stalled_initiatives(limit=10)
        with open(output_dir / "stalled.json", "w", encoding="utf-8") as f:
            json.dump(stalled, f, ensure_ascii=False, cls=NumpyEncoder)
        print("✅ stalled.json generated")
    except Exception as e:
        print(f"❌ Error generating stalled: {e}")
        
    # We create an empty phases.json just in case something breaks, though we'll remove it from frontend
    with open(output_dir / "phases.json", "w", encoding="utf-8") as f:
        json.dump([], f)
    
    print("All JSON files generated successfully!")

if __name__ == "__main__":
    generate_static_json()
