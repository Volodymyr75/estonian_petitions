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

    # 4. Outcomes (Stalled vs Recent Successes)
    try:
        outcomes = get_stalled_and_recent_successes(limit_stalled=5, limit_recent=5)
        with open(output_dir / "outcomes.json", "w", encoding="utf-8") as f:
            json.dump(outcomes, f, ensure_ascii=False, cls=NumpyEncoder)
        print("✅ outcomes.json generated")
    except Exception as e:
        print(f"❌ Error generating outcomes: {e}")
        
    # 5. Deadline
    try:
        deadline = get_approaching_deadline_initiatives(limit=5)
        with open(output_dir / "deadline.json", "w", encoding="utf-8") as f:
            json.dump(deadline, f, ensure_ascii=False, cls=NumpyEncoder)
        print("✅ deadline.json generated")
    except Exception as e:
        print(f"❌ Error generating deadline: {e}")
        
    # 5. Phases
    try:
        phases = get_phase_distribution()
        with open(output_dir / "phases.json", "w", encoding="utf-8") as f:
            json.dump(phases, f, ensure_ascii=False, cls=NumpyEncoder)
        print("✅ phases.json generated")
    except Exception as e:
        print(f"❌ Error generating phases: {e}")
    
    # 6. Process Metrics
    try:
        process_metrics = get_process_metrics()
        with open(output_dir / "process_metrics.json", "w", encoding="utf-8") as f:
            json.dump(process_metrics, f, ensure_ascii=False, cls=NumpyEncoder)
        print("✅ process_metrics.json generated")
    except Exception as e:
        print(f"❌ Error generating process_metrics: {e}")

    # 7. Top Timelines
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
            
        with open(output_dir / "top_timelines.json", "w", encoding="utf-8") as f:
            json.dump(timelines, f, ensure_ascii=False, cls=NumpyEncoder)
        print("✅ top_timelines.json generated")
    except Exception as e:
        print(f"❌ Error generating top_timelines: {e}")

    # 8. Initiatives List (for Autocomplete Search)
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

        with open(output_dir / "initiatives_list.json", "w", encoding="utf-8") as f:
            json.dump(inits_list, f, ensure_ascii=False, cls=NumpyEncoder)
        print("✅ initiatives_list.json generated")
    except Exception as e:
        print(f"❌ Error generating initiatives_list: {e}")
        
    # 9. Institutions
    try:
        inst_overview = get_institutional_overview()
        inst_mapped = get_mapped_initiatives()
        
        with open(output_dir / "institutions.json", "w", encoding="utf-8") as f:
            json.dump({
                "overview": inst_overview,
                "petitions": inst_mapped
            }, f, ensure_ascii=False, cls=NumpyEncoder)
        print("✅ institutions.json generated")
        
        # 10. Institutions Details
        inst_details = {}
        for pet in inst_mapped:
            init_id = pet.get('initiative_id')
            if init_id:
                d = get_petition_details_and_votings(init_id)
                if d:
                    inst_details[init_id] = d
                    
        with open(output_dir / "institutions_details.json", "w", encoding="utf-8") as f:
            json.dump(inst_details, f, ensure_ascii=False, cls=NumpyEncoder)
        print("✅ institutions_details.json generated")
    except Exception as e:
        print(f"❌ Error generating institutions data: {e}")

    print("All JSON files generated successfully!")

if __name__ == "__main__":
    generate_static_json()
