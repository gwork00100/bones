import argparse
import json
from google_search_fetcher import fetch_from_google  # real fetching logic here

def load_api_keys(path="config/api_keys.json"):
    with open(path, "r") as f:
        return json.load(f)

API_KEYS = load_api_keys()

def fetch_from_news():
    keys = API_KEYS.get("news_api", [])
    print(f"Fetching News data with keys: {keys}")
    # TODO: Add real fetching logic here

def run(source):
    if source == "google_search":
        fetch_from_google()
    elif source == "news_api":
        fetch_from_news()
    else:
        print(f"Unknown source: {source}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch trends from various sources")
    parser.add_argument("--source", required=True, help="Source to fetch from (google_search, news_api)")
    args = parser.parse_args()
    run(args.source)
