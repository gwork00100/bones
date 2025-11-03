import os
import time
import requests
from datetime import datetime

# === Configuration ===
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CUSTOM_SEARCH_ENGINE_ID = os.getenv("CSE_ID")
BLOOD_API_URL = os.getenv("BLOOD_API_URL", "https://media-funnel-back.onrender.com/daily-trends")

# Keywords to fetch
KEYWORDS = [
    "OpenAI", "ChatGPT", "Ethereum",
    "NVIDIA", "Midjourney", "LLM fine-tuning"
]

# Rate limit delay (seconds)
DELAY_BETWEEN_REQUESTS = 2

# === Helper Functions ===
def fetch_google_results(query):
    """Fetch search results for a query from Google Custom Search."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_API_KEY,
        'cx': CUSTOM_SEARCH_ENGINE_ID,
        'q': query
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        items = results.get('items', [])
        return items
    except requests.exceptions.RequestException as e:
        print(f"[❌] Request failed for '{query}': {e}")
        return []

def post_to_blood(item, keyword):
    """Send a single search result to blood API."""
    payload = {
        "title": item.get("title"),
        "link": item.get("link"),
        "keyword": keyword,
        "fetched_at": datetime.utcnow().isoformat()
    }

    try:
        response = requests.post(BLOOD_API_URL, json=payload)
        if response.status_code == 200:
            print(f"[✅] Sent to blood: {item.get('title')}")
        else:
            print(f"[⚠️] Blood API returned {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[❌] Failed to send to blood: {e}")

# === Main Loop ===
def main():
    for keyword in KEYWORDS:
        print(f"\n🔍 Fetching results for: {keyword}")
        items = fetch_google_results(keyword)

        if not items:
            print(f"[⚠️] No results for: {keyword}")
            continue

        for item in items:
            post_to_blood(item, keyword)

        time.sleep(DELAY_BETWEEN_REQUESTS)

if __name__ == "__main__":
    main()
