import requests

API_KEY = "AIzaSyDz7HXgh4t8C-7Tw_DH1d6zaMe3LlZdwxY"
CSE_ID = "30898967c7dd54c74"
query = "ChatGPT"

url = "https://www.googleapis.com/customsearch/v1"
params = {
    "key": API_KEY,
    "cx": CSE_ID,
    "q": query
}

res = requests.get(url, params=params)
print(f"Status code: {res.status_code}")
print(res.json())
