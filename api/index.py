import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.analytics import get_overview_kpis, get_trending_initiatives
from services.initiatives import get_active_initiatives, get_initiative_timeline

app = FastAPI(title="Estonian Civic Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/kpis")
def get_kpis():
    return get_overview_kpis()

@app.get("/api/trending")
def get_trending(limit: int = 5):
    return get_trending_initiatives(limit=limit)

@app.get("/api/initiatives/active")
def get_active():
    return get_active_initiatives()

@app.get("/api/initiatives/{initiative_id}/timeline")
def get_timeline(initiative_id: str):
    return get_initiative_timeline(initiative_id)
