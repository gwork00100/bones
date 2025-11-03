from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

def get_trending_coins():
    try:
        data = cg.search_trending()
        return [item['item']['name'].lower() for item in data['coins']]
    except Exception as e:
        print(f"[Coingecko Error] {e}")
        return []

def get_market_snapshot():
    return cg.get_coins_markets(vs_currency='usd')
