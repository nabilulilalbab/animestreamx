import requests
import time

# Konfigurasi API
API_BASE = "http://localhost:5000/api"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Referer": "https://streamex.sh/",
}

# Daftar anime untuk diuji (dengan slug yang valid)
ANIME_LIST = [
    {"id": "naruto", "name": "Naruto"},
    {"id": "demon-slayer-kimetsu-no-yaiba", "name": "Demon Slayer"},
    {"id": "jujutsu-kaisen-tv", "name": "Jujutsu Kaisen"},
    {"id": "one-piece", "name": "One Piece"},
    {"id": "shingeki-no-kyojin", "name": "Attack on Titan"},
]

def test_endpoint(url, params=None):
    try:
        start = time.time()
        resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
        elapsed = int((time.time() - start) * 1000)
        
        return {
            'status': resp.status_code,
            'time': elapsed,
            'data': resp.json() if resp.status_code == 200 else None
        }
    except Exception as e:
        return {'error': str(e)}

def test_health():
    print("\n[TEST] Provider Health Check")
    result = test_endpoint(f"{API_BASE}/providers/health")
    if 'error' in result:
        print(f"  ERROR: {result['error']}")
    else:
        print(f"  Status: {result['status']}, Time: {result['time']}ms")
        print(f"  Provider Count: {len(result['data'])}")


def test_anime_detail(anime):
    print(f"\n[TEST] Anime Detail: {anime['name']}")
    result = test_endpoint(f"{API_BASE}/detail/anime/{anime['id']}")
    
    if 'error' in result:
        print(f"  ERROR: {result['error']}")
        return
        
    print(f"  Status: {result['status']}, Time: {result['time']}ms")
    
    if result['status'] != 200:
        print(f"  ERROR: Unexpected status")
        return
        
    data = result['data']
    print(f"  Title: {data.get('title')}")
    print(f"  Episode Count: {len(data.get('episodes', []))}")
    
    # Uji sumber streaming untuk episode pertama
    if data.get('episodes'):
        first_ep = data['episodes'][0]
        print(f"  Testing sources for Episode {first_ep.get('episode_no')}")
        
        for source in first_ep.get('sources', [])[:5]:  # Batasi ke 5 provider pertama
            provider = source.get('provider', 'unknown')
            url = source.get('url', '')
            
            print(f"    Provider: {provider}")
            print(f"      URL: {url[:80]}..." if len(url) > 80 else f"      URL: {url}")
            
            # Uji akses URL streaming
            try:
                resp = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=10)
                print(f"      Status: {resp.status_code}, Content-Type: {resp.headers.get('Content-Type')}")
            except Exception as e:
                print(f"      ERROR: {str(e)}")


def main():
    print("Starting API Endpoint Tests")
    print("="*60)
    
    # 1. Test kesehatan provider
    test_health()
    
    # 2. Test detail untuk 5 anime
    for anime in ANIME_LIST:
        test_anime_detail(anime)
        time.sleep(1)
    
    print("\nTesting completed!")

if __name__ == "__main__":
    main()