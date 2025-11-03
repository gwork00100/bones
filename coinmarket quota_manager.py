import requests

url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
headers = {
    "X-CMC_PRO_API_KEY": "e52fa721e06743a7aca1697a6c928b08",  # Replace with your key
    "Accepts": "application/json"
}

params = {
    "start": "1",
    "limit": "10",
    "convert": "USD"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
print(data)
