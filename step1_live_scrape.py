import requests
import json
import time

BASE_URL = "https://streamex.sh/api/hianime"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

def get_anime_list(category, pages=1):
    all_results = []
    for page in range(1, pages + 1):
        print(f"Fetching {category} page {page}...")
        try:
            url = f"{BASE_URL}/{category}?page={page}"
            res = requests.get(url, headers=HEADERS)
            data = res.json()
            if 'results' in data:
                all_results.extend(data['results'])
            time.sleep(1) # Delay kecil biar sopan
        except Exception as e:
            print(f"Error on page {page}: {e}")
    return all_results

def get_detailed_data(anime_id):
    print(f"Getting details for: {anime_id}...")
    try:
        # 1. Info (Meta & AniList ID)
        info = requests.get(f"{BASE_URL}/info/{anime_id}", headers=HEADERS).json()
        # 2. Episodes
        eps = requests.get(f"{BASE_URL}/episodes/{anime_id}", headers=HEADERS).json()
        
        info['episodes_list'] = eps.get('episodes', [])
        return info
    except Exception as e:
        print(f"Error getting details: {e}")
        return None

if __name__ == "__main__":
    # Test ambil 1 halaman saja dulu untuk pembuktian cepat
    popular = get_anime_list("most-popular", pages=1)
    
    full_db = []
    for item in popular[:10]: # Kita ambil 10 pertama untuk testing step ini
        detail = get_detailed_data(item['id'])
        if detail:
            full_db.append(detail)
    
    with open('live_anime_db.json', 'w') as f:
        json.dump(full_db, f, indent=4)
    
    print(f"\nSukses! {len(full_db)} data anime lengkap berhasil diambil.")
