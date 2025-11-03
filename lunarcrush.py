import requests
import sseclient

# Your LunarCrush MCP Server URL with API key
url = "https://lunarcrush.ai/sse?key=xa9p72r7w9a3k5q3z3uuv6srf5mh2abtkyjst1p3c"

def listen_lunarcrush():
    # Connect to the streaming endpoint
    response = requests.get(url, stream=True)
    client = sseclient.SSEClient(response)

    for event in client.events():
        # Each event data is JSON string
        print("New event received:")
        print(event.data)
        print("-" * 40)

if __name__ == "__main__":
    listen_lunarcrush()
