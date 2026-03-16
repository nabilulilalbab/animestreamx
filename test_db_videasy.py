import requests
import json

BASE = "https://db.videasy.net/3"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Referer": "https://streamex.sh/",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Sec-Ch-Ua-Platform": "\"Linux\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}

print(f"Testing GET {BASE}")
try:
    resp = requests.get(BASE, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    print(f"Headers: {dict(resp.headers)}")
    if resp.text:
        print(f"Response preview: {resp.text[:500]}")
        try:
            json_data = resp.json()
            print(f"JSON parsed: {json.dumps(json_data, indent=2)[:500]}")
        except:
            print("Response is not JSON")
except Exception as e:
    print(f"Error: {e}")

# Try a known endpoint from the JS file: /hianime/sources-with-title
# We need sample parameters
print("\n--- Testing /hianime/sources-with-title ---")
params = {
    "title": "Naruto",
    "year": "2002",
    "episodeId": "1",
    "dub": "false"
}
url = "https://api.videasy.net/hianime/sources-with-title"
try:
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    if resp.text:
        print(f"Response preview: {resp.text[:1000]}")
except Exception as e:
    print(f"Error: {e}")