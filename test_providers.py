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

# Provider patterns from JS mapping (TV)
providers = [
    ("streamx", "https://embed.wplay.me/embed/tv/{id}/{s}/{e}"),
    ("mapi", "https://www.zxcstream.xyz/embed/tv/{id}/{s}/{e}"),
    ("cinemaos", "https://cinemaos.tech/player/{id}/{s}/{e}"),
    ("rive", "https://watch.rivestream.app/embed?type=tv&id={id}&season={s}&episode={e}"),
    ("videasy", "https://player.videasy.net/tv/{id}/{s}/{e}"),
    ("vidpro", "https://vidlink.pro/tv/{id}/{s}/{e}"),
    ("vidking", "https://vidking.net/embed/tv/{id}/{s}/{e}"),
]

# Test with dummy IDs
test_id = "123"
season = "1"
episode = "1"

for name, pattern in providers:
    url = pattern.replace("{id}", test_id).replace("{s}", season).replace("{e}", episode)
    print(f"\nTesting {name}: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=False)
        print(f"  Status: {resp.status_code}")
        print(f"  Location: {resp.headers.get('Location', 'N/A')}")
        if resp.status_code == 200:
            # check if it's HTML or JSON
            content_type = resp.headers.get('Content-Type', '')
            if 'json' in content_type:
                print(f"  JSON response preview: {resp.text[:200]}")
            else:
                print(f"  HTML response length: {len(resp.text)}")
    except Exception as e:
        print(f"  Error: {e}")

# Test anime providers
anime_providers = [
    ("vidcc-sub", "https://vidsrc.cc/v2/embed/anime/ani{id}/{ep}/sub"),
    ("vidcc-dub", "https://vidsrc.cc/v2/embed/anime/ani{id}/{ep}/dub"),
    ("pahe-sub", "https://vidnest.fun/animepahe/{id}/{ep}/sub"),
    ("videasy-sub", "https://player.videasy.net/anime/{id}/{ep}"),
    ("videasy-dub", "https://player.videasy.net/anime/{id}/{ep}?dub=true"),
]

print("\n=== Anime Providers ===")
for name, pattern in anime_providers:
    url = pattern.replace("{id}", "20").replace("{ep}", "1")
    print(f"\nTesting {name}: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=False)
        print(f"  Status: {resp.status_code}")
        print(f"  Location: {resp.headers.get('Location', 'N/A')}")
        if resp.status_code == 200:
            content_type = resp.headers.get('Content-Type', '')
            if 'json' in content_type:
                print(f"  JSON response preview: {resp.text[:200]}")
            else:
                print(f"  HTML response length: {len(resp.text)}")
    except Exception as e:
        print(f"  Error: {e}")