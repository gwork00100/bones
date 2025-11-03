import os
import pandas as pd
from pytrends.request import TrendReq
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# ------------------------------
# LOAD ENVIRONMENT VARIABLES
# ------------------------------
load_dotenv()  # must be first

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
TREND_KEYWORDS = os.getenv("TREND_KEYWORDS", "python,ai").split(",")

# Validate Supabase credentials
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "❌ SUPABASE_URL or SUPABASE_KEY not set. "
        "Check your .env file and ensure it's in the same folder as this script."
    )

pd.set_option('future.no_silent_downcasting', True)  # suppress pandas warnings

# ------------------------------
# FUNCTIONS
# ------------------------------
def fetch_google_trends(keywords):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(keywords, timeframe='now 1-d', geo='')
    df = pytrends.interest_over_time()
    if df.empty:
        return pd.DataFrame()
    df.reset_index(inplace=True)
    df['timestamp'] = df['date'].apply(lambda x: x.isoformat())
    records = []
    for _, row in df.iterrows():
        for kw in keywords:
            records.append({
                "keyword": kw,
                "value": int(row[kw]),
                "is_partial": bool(row["isPartial"]),
                "timestamp": row["timestamp"]
            })
    return pd.DataFrame(records)

def fetch_ollama_trends():
    if not OLLAMA_API_KEY:
        print("⚠️ OLLAMA_API_KEY not set. Skipping Ollama trends.")
        return pd.DataFrame()
    headers = {"Authorization": f"Bearer {OLLAMA_API_KEY}"}
    try:
        resp = requests.get("https://api.ollama.com/v1/trends", headers=headers)
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data.get('trends', []))
        if not df.empty:
            df['timestamp'] = datetime.now(timezone.utc).isoformat()
        return df
    except requests.RequestException as e:
        print(f"⚠️ Failed to fetch Ollama trends: {e}")
        return pd.DataFrame()

def save_to_supabase(df, table_name="trends"):
    if df.empty:
        print("⚠️ No data to save")
        return
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    records = df.astype(str).to_dict(orient="records")
    try:
        response = requests.post(url, headers=headers, json=records)
        if response.status_code not in [200, 201]:
            print("❌ Error saving records:", response.text)
        else:
            print(f"✅ Saved {len(records)} records to {table_name}")
    except requests.RequestException as e:
        print(f"❌ Failed to save to Supabase: {e}")

# ------------------------------
# MAIN
# ------------------------------
if __name__ == "__main__":
    print("🔹 Fetching Google Trends...")
    google_trends = fetch_google_trends(TREND_KEYWORDS)
    if not google_trends.empty:
        print(google_trends.head())
        save_to_supabase(google_trends)

    print("🔹 Fetching Ollama Trends...")
    ollama_trends = fetch_ollama_trends()
    if not ollama_trends.empty:
        print(ollama_trends.head())
        save_to_supabase(ollama_trends)

    print("✅ Trend ingestion completed.")
