import os
import requests
from datetime import datetime, timezone

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def log_heartbeat(status, details, retries=0):
    """Logs a heartbeat to Supabase and prints to console."""
    timestamp = datetime.now(timezone.utc).isoformat()
    
    print(f"[{timestamp}] {status.upper()}: {details} (retries: {retries})")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("⚠️ Supabase not configured. Skipping persistent heartbeat.")
        return

    url = f"{SUPABASE_URL}/rest/v1/heartbeat_logs"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    payload = [{
        "timestamp": timestamp,
        "status": status,
        "details": details,
        "retries": retries
    }]
    try:
        resp = requests.post(url, headers=headers, json=payload)
        if resp.status_code not in [200, 201]:
            print(f"❌ Failed to save heartbeat: {resp.text}")
    except Exception as e:
        print(f"❌ Exception saving heartbeat: {e}")
