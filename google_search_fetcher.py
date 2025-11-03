# google_search_fetcher.py

import requests
import random
import time
from datetime import datetime
from supabase import create_client
from load_keys import load_api_keys

# === Configuration ===

API_KEYS = load_api_keys()
SUPABASE_URL = "https://ajkemrtlmbuvyjkrioze.supabase.co"
SUPABASE_KEY = "sb_secret_84QbW2noWzcABMsv6XWJWw_vv6ZTKbF"
CUSTOM_SEARCH_ENGINE_ID = "30898967c7dd54c74"
TABLE_NAME = "google_trends"  # New table to avoid clashing with existing trends table

# Blood endpoint
BLOOD_URL = "https://media-funnel-back.onrender.com/daily-trends"

# === Initialize Supabase Client ===

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Helper Functions ===

def get_random_api_key():
    keys = API_KEYS.get("google_search", [])
    if not keys:
        raise ValueError("[❌] No API keys found under 'google_search'.")
    return random.choice(keys)

def fetch_search_results(query):
    print(f"[🔎] Fetching search results for '{query}'...")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": get_random_api_key(),
        "cx": CUSTOM_SEARCH_ENGINE_ID,
        "q": query
    }
    response = requests.get(url, params=params)

    print(f"[📡] HTTP Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"[❌] API ERROR: {response.text}")
        return []

    items = response.json().get("items", [])
    print(f"[✅] Got {len(items)} results for '{query}'")
    return items

def check_duplicate(link, keyword):
    resp = supabase.table(TABLE_NAME).select("id").eq("link", link).eq("keyword", keyword).execute()
    return bool(resp.data) if resp and hasattr(resp, "data") else False

def save_results_to_supabase(items, keyword):
    print(f"[💾] Saving results to Supabase for keyword: '{keyword}'")
    saved_items = []
    for item in items:
        link = item.get("link")
        if check_duplicate(link, keyword):
            print(f"[⚠️] Skipping duplicate: {link}")
            continue

        data = {
            "title": item.get("title"),
            "link": link,
            "keyword": keyword,
            "interest": None,
            "fetched_at": datetime.utcnow().isoformat()
        }
        response = supabase.table(TABLE_NAME).insert(data).execute()

        if response.get("error"):
            print(f"[❌] DB INSERT ERROR for '{data['title']}':", response["error"])
        else:
            print(f"[✅] Saved to DB: {data['title']}")
            saved_items.append(data)
    return saved_items

def send_to_blood(keyword, items):
    if not items:
        return
    payload = {
        "query": keyword,
        "source": "google",
        "timestamp": datetime.utcnow().isoformat(),
        "results": [
            {"title": item["title"], "link": item["link"]} for item in items
        ]
    }
    
    try:
        response = requests.post(BLOOD_URL, json=payload)
        if response.status_code == 200:
            print(f"[❤️] Successfully sent {len(items)} results to blood")
        else:
            print(f"[❌] Failed to send to blood: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"[❌] Error sending to blood: {e}")

# === Main Function ===

def fetch_from_google():
    keywords = [
        "OpenAI", "Ethereum", "ChatGPT",
        "NVIDIA", "Midjourney", "LLM fine-tuning"
    ]

    for keyword in keywords:
        print(f"\n🔍 Searching: {keyword}")
        try:
            results = fetch_search_results(keyword)
            saved_items = save_results_to_supabase(results, keyword)
            send_to_blood(keyword, saved_items)  # <-- send to blood after saving
        except Exception as e:
            print(f"[❌] Error processing '{keyword}': {e}")
        
        time.sleep(2)  # Be respectful of rate limits

if __name__ == "__main__":
    fetch_from_google()
