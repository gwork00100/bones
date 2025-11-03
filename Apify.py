import os
import requests

# Get the token from environment
APIFY_TOKEN = os.getenv(" apify_api_CTk6K4sc7a4KBbxto09EmUD9Y3RoOX4qiOQz")

if not APIFY_TOKEN:
    raise ValueError("Missing Apify API token! Please set it as an environment variable.")

url = f"https://api.apify.com/v2/acts/lukaskrivka~home-depot-scraper/run-sync-get-dataset-items?token={APIFY_TOKEN}"
params = {"search": "cordless drill", "maxItems": 5}

response = requests.get(url, params=params)
data = response.json()

for item in data:
    print(item["title"], "-", item["price"])
