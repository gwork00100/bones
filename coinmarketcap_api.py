import requests

url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
headers = {
    "X-CMC_PRO_API_KEY": "YOUR_API_KEY",  # Replace with your actual key
    "Accepts": "application/json"
}

params = {
    "start": "1",
    "limit": "10",  # Get top 10 cryptocurrencies
    "convert": "USD"
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
print(data)
