import requests
import json

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

def test_sources_with_title():
    url = "https://api.videasy.net/hianime/sources-with-title"
    params = {
        "title": "Naruto",
        "year": "2002",
        "episodeId": "1",
        "dub": "false"
    }
    print(f"GET {url}")
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Keys in response: {list(data.keys())}")
        if 'details' in data:
            details = data['details']
            print(f"Details keys: {list(details.keys())}")
            print(f"Episodes count: {len(details.get('episodes', []))}")
        if 'mediaSources' in data:
            media = data['mediaSources']
            print(f"MediaSources keys: {list(media.keys())}")
            if 'sources' in media:
                sources = media['sources']
                print(f"Number of sources: {len(sources)}")
                for src in sources[:3]:
                    print(f"  - {src.get('name')}: {src.get('url')}")
            if 'subtitles' in media:
                print(f"Subtitles count: {len(media['subtitles'])}")
        # Save full response
        with open('sources_response.json', 'w') as f:
            json.dump(data, f, indent=2)
        print("Full response saved to sources_response.json")
    else:
        print(f"Response text: {resp.text[:500]}")

def test_tracking():
    # Try to find tracking endpoint
    url = "https://users.videasy.net/api/track"
    print(f"\nPOST {url}")
    # We don't know the payload, maybe we can guess
    payload = {
        "event": "play",
        "video_id": "test",
        "timestamp": 1234567890
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

def test_provider_api():
    # Test provider API like cinemaos.tech/api/providerv2
    url = "https://cinemaos.tech/api/providerv2"
    print(f"\nGET {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response preview: {resp.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

def test_stream_proxy():
    # Test proxy endpoint streams.smashystream.top/proxy/m3u8
    # Need encoded URL
    import base64
    # Example: encode a sample m3u8 URL
    sample_url = "https://example.com/stream.m3u8"
    encoded = base64.b64encode(sample_url.encode()).decode()
    url = f"https://streams.smashystream.top/proxy/m3u8/{encoded}/%7B%7D"
    print(f"\nGET {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Headers: {dict(resp.headers)}")
        print(f"Response preview: {resp.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_sources_with_title()
    test_tracking()
    test_provider_api()
    test_stream_proxy()