import requests
from supabase import create_client
from datetime import datetime
import random
import time

# --- CONFIGURATION ---

GOOGLE_API_KEYS = [
    "AIzaSyDz7HXgh4t8C-7Tw_DH1d6zaMe3LlZdwxY",
    "AIzaSyXXX_ANOTHER_API_KEY_123"  # Add more valid keys here
]

CUSTOM_SEARCH_ENGINE_ID = "30898967c7dd54c74"

SUPABASE_URL = "https://ajkemrtlmbuvyjkrioze.supabase.co"
SUPABASE_KEY = "sb_secret_84QbW2noWzcABMsv6XWJWw_vv6ZTKbF"
TABLE_NAME = "trends"

# --- INITIALIZATION ---

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- FUNCTIONS ---

def get_random_api_key():
    if not GOOGLE_API_KEYS:
        raise ValueError("[❌] No Google API keys configured!")
    return random.choice(GOOGLE_API_KEYS)

def fetch_search_results(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": get_random_api_key(),
        "cx": CUSTOM_SEARCH_ENGINE_ID,
        "q": query
    }
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"[❌] Google API error for '{query}': {response.text}")
        return []

    items = response.json().get("items", [])
    print(f"[✅] Fetched {len(items)} results for: '{query}'")
    return items

def save_results_to_supabase(items, keyword):
    for item in items:
        data = {
            "title": item.get("title"),
            "link": item.get("link"),
            "keyword": keyword,
            "interest": None,
            "fetched_at": datetime.utcnow().isoformat()
        }

        response = supabase.table(TABLE_NAME).insert(data).execute()

        # response object can differ, so check both possible ways:
        if (hasattr(response, 'status_code') and response.status_code >= 300) or response.get("error"):
            print(f"[❌] Insert error for '{data['title']}': {response.get('error')}")
        else:
            print(f"[✅] Inserted: {data['title']}")

def fetch_keywords_from_source():
    # Placeholder for dynamic keyword fetching (Google Trends, Twitter, etc.)
    return ["OpenAI", "Ethereum", "ChatGPT", "NVIDIA", "Midjourney", "LLM fine-tuning"]

# --- MAIN EXECUTION ---

if __name__ == "__main__":
    keywords = fetch_keywords_from_source()

    for keyword in keywords:
        print(f"\n🔍 Searching: {keyword}")
        try:
            results = fetch_search_results(keyword)
            if results:
                save_results_to_supabase(results, keyword)
            else:
                print(f"[⚠️] No results for: {keyword}")
        except Exception as e:
            print(f"[❌] Error processing '{keyword}': {e}")

        time.sleep(2)  # polite delay to avoid rate limits
