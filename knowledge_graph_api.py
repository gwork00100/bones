import requests

GOOGLE_API_KEY = "AIzaSyC9-MRuxiacZpVGYBsUS_LKFdvBjfzqZO8"  # Replace with your API key

def search_knowledge_graph(query, limit=5):
    url = "https://kgsearch.googleapis.com/v1/entities:search"
    params = {
        'query': query,
        'limit': limit,
        'indent': True,
        'key': GOOGLE_API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Knowledge Graph API error:", response.text)
        return []
    results = response.json()
    return results.get('itemListElement', [])

# Example usage:
if __name__ == "__main__":
    results = search_knowledge_graph("ChatGPT")
    for item in results:
        entity = item.get('result', {})
        print(entity.get('name'), "-", entity.get('description'))
