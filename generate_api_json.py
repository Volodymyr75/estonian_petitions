import os
import json
import duckdb
import numpy as np
from pathlib import Path

# Load .env file and default to MotherDuck if token is present
env_path = Path(".env")
if env_path.exists():
    with open(env_path, "r") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                os.environ[key] = val

if "MOTHERDUCK_TOKEN" in os.environ and not os.environ.get("DB_PATH"):
    os.environ["DB_PATH"] = "md:estonia_petitions"


from services.analytics import (
    get_overview_kpis,
    get_trending_initiatives,
    get_recent_summary,
    get_phase_distribution,
    get_approaching_deadline_initiatives,
    get_stalled_and_recent_successes,
    get_process_metrics,
    get_db_connection
)
from services.initiatives import get_initiative_timeline
from services.institutions import (
    get_institutional_overview,
    get_mapped_initiatives,
    get_petition_details_and_votings
)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        return super(NumpyEncoder, self).default(obj)

def clean_nan(obj):
    if obj is None:
        return None
    
    # Check class name to handle pandas NA, NaT and numpy/pandas floats safely
    class_name = obj.__class__.__name__
    if class_name in ('NAType', 'NaTType'):
        return None
        
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [clean_nan(x) for x in obj]
    elif isinstance(obj, (float, np.floating)):
        if obj != obj or obj == float('inf') or obj == float('-inf'):
            return None
        return float(obj)
    elif isinstance(obj, (int, np.integer)):
        return int(obj)
    
    # General fallback for any other nan-like values
    try:
        if obj != obj:
            return None
    except Exception:
        pass
        
    return obj

def write_json(data, filepath):
    cleaned = clean_nan(data)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, cls=NumpyEncoder)

def generate_static_json():
    print("Generating static JSON API data...")
    
    # Ensure public/api_data directory exists
    output_dir = Path("public/api_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. KPIs
    try:
        kpis = get_overview_kpis()
        write_json(kpis, output_dir / "kpis.json")
        print("✅ kpis.json generated")
    except Exception as e:
        print(f"❌ Error generating kpis: {e}")

    # 2. Trending
    try:
        trending = get_trending_initiatives(limit=5)
        write_json(trending, output_dir / "trending.json")
        print("✅ trending.json generated")
    except Exception as e:
        print(f"❌ Error generating trending: {e}")

    # 3. Summary
    try:
        summary = get_recent_summary()
        write_json(summary, output_dir / "summary.json")
        print("✅ summary.json generated")
    except Exception as e:
        print(f"❌ Error generating summary: {e}")

    # 4. Outcomes (Stalled vs Recent Successes)
    try:
        outcomes = get_stalled_and_recent_successes(limit_stalled=5, limit_recent=5)
        write_json(outcomes, output_dir / "outcomes.json")
        print("✅ outcomes.json generated")
    except Exception as e:
        print(f"❌ Error generating outcomes: {e}")
        
    # 5. Deadline
    try:
        deadline = get_approaching_deadline_initiatives(limit=5)
        write_json(deadline, output_dir / "deadline.json")
        print("✅ deadline.json generated")
    except Exception as e:
        print(f"❌ Error generating deadline: {e}")
        
    # 6. Phases
    try:
        phases = get_phase_distribution()
        write_json(phases, output_dir / "phases.json")
        print("✅ phases.json generated")
    except Exception as e:
        print(f"❌ Error generating phases: {e}")
    
    # 7. Process Metrics
    try:
        process_metrics = get_process_metrics()
        write_json(process_metrics, output_dir / "process_metrics.json")
        print("✅ process_metrics.json generated")
    except Exception as e:
        print(f"❌ Error generating process_metrics: {e}")

    # 8. Top Timelines
    try:
        con = get_db_connection()
        top_query = """
        SELECT DISTINCT i.id, i.title, i.signatures_count
        FROM initiatives i
        JOIN initiative_events e ON i.id = e.initiative_id
        ORDER BY i.signatures_count DESC
        LIMIT 30
        """
        res = con.execute(top_query)
        try:
            top_inits = res.df().to_dict(orient='records')
        except Exception:
            columns = [col[0] for col in res.description]
            top_inits = [dict(zip(columns, row)) for row in res.fetchall()]
        con.close()

        timelines = {}
        for r in top_inits:
            init_id = r['id']
            timelines[init_id] = {
                "title": r['title'],
                "signatures_count": r['signatures_count'],
                "events": get_initiative_timeline(init_id)
            }
            
        write_json(timelines, output_dir / "top_timelines.json")
        print("✅ top_timelines.json generated")
    except Exception as e:
        print(f"❌ Error generating top_timelines: {e}")

    # 9. Initiatives List (for Autocomplete Search)
    try:
        con = get_db_connection()
        list_query = "SELECT id, title, phase FROM initiatives ORDER BY signatures_count DESC"
        res = con.execute(list_query)
        try:
            inits_list = res.df().to_dict(orient='records')
        except Exception:
            columns = [col[0] for col in res.description]
            inits_list = [dict(zip(columns, row)) for row in res.fetchall()]
        con.close()

        write_json(inits_list, output_dir / "initiatives_list.json")
        print("✅ initiatives_list.json generated")
    except Exception as e:
        print(f"❌ Error generating initiatives_list: {e}")
        
    # 10. Institutions
    try:
        inst_overview = get_institutional_overview()
        inst_mapped = get_mapped_initiatives()
        
        write_json({
            "overview": inst_overview,
            "petitions": inst_mapped
        }, output_dir / "institutions.json")
        print("✅ institutions.json generated")
        
        # 11. Institutions Details
        inst_details = {}
        for pet in inst_mapped:
            init_id = pet.get('initiative_id')
            if init_id:
                d = get_petition_details_and_votings(init_id)
                if d:
                    inst_details[init_id] = d
                    
        write_json(inst_details, output_dir / "institutions_details.json")
        print("✅ institutions_details.json generated")
    except Exception as e:
        print(f"❌ Error generating institutions data: {e}")

    print("All JSON files generated successfully!")

if __name__ == "__main__":
    generate_static_json()
