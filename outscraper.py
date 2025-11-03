import os
import requests

# Get Outscraper API key from environment variable
OUTSCRAPER_API_KEY = os.getenv("ZjhkMWNhZjRiYTVjNGUzMGEwMDM2ZjgxN2QxN2UyY2J8MGU1ZWU1NTAyZg")

if not OUTSCRAPER_API_KEY:
    raise ValueError("Missing Outscraper API key! Please set it as an environment variable.")

# Example endpoint for Outscraper Google Maps scraper (adjust if you use different API)
url = "https://api.outscraper.com/google-maps/search"

# Query parameters - example: searching for cordless drill stores or products
payload = {
    "query": "cordless drill store",  # adjust search query as needed
    "limit": 5
}

# Headers including API key for authorization
headers = {
    "X-API-KEY": OUTSCRAPER_API_KEY,
    "Content-Type": "application/json"
}

# Send POST request to Outscraper API
response = requests.post(url, json=payload, headers=headers)

# Parse JSON response
data = response.json()

# Print some results (adjust keys based on API response)
for item in data.get("results", []):
    print(item.get("title", "No title"), "-", item.get("address", "No address"))
