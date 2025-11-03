# heartbeat_logger.py

import os
from datetime import datetime, timezone
from supabase import create_client
import requests

# Load Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client if credentials are available
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def log_heartbeat(status, details, retries=0):
    """
    Logs a heartbeat to Supabase (if configured) and prints to console.
    
    Args:
        status (str): Status of the heartbeat (e.g., 'ok', 'error').
        details (str): Any additional information about the heartbeat.
        retries (int): Number of retry attempts (default 0).
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"[{timestamp}] {status.upper()}: {details} (retries: {retries})")

    if not supabase:
        print("⚠️ Supabase not configured. Skipping persistent heartbeat.")
        return

    try:
        # Save heartbeat to Supabase table 'heartbeat_logs'
        supabase.table("heartbeat_logs").insert({
            "timestamp": timestamp,
            "status": status,
            "details": details,
            "retries": retries
        }).execute()
    except Exception as e:
        print(f"❌ Exception saving heartbeat: {e}")
