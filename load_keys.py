import json

def load_api_keys(path="config/api_keys.json"):
    with open(path, "r") as f:
        return json.load(f)

API_KEYS = load_api_keys()

print(API_KEYS["google_search"])
