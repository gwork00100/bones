import os
import requests

# Get SerpApi API key from environment variable
SERPAPI_API_KEY = os.getenv("8ec4704eb9779b062f91570b385aa3256a525c0ceecfe9ecac4b4e22c3602688")

if not SERPAPI_API_KEY:
    raise ValueError("Missing SerpApi API key! Please set it as an environment variable.")

# SerpApi Google Search API endpoint
url = "https://serpapi.com/search.json"

# Query parameters for search (e.g., search "cordless drill stores")
params = {
    "q": "cordless drill store",   # search query
    "api_key": SERPAPI_API_KEY,
    "engine": "google",            # specify search engine
    "num": 5                      # number of results to return
}

# Send GET request to SerpApi
response = requests.get(url, params=params)
data = response.json()

# Print the title and link of each organic search result
for result in data.get("organic_results", []):
    title = result.get("title", "No title")
    link = result.get("link", "No link")
    print(f"{title} - {link}")
