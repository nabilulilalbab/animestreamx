import requests
import json
import sys

BASE_URL = "https://streamex.sh/api/hianime"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_anime_direct(query):
    # 1. Search Anime
    print(f"Searching for: {query}...")
    search_res = requests.get(f"{BASE_URL}/search?query={query}", headers=HEADERS).json()
    
    if not search_res.get('results'):
        print("No results found.")
        return
    
    # Pick first result
    anime = search_res['results'][0]
    anime_id = anime['id']
    print(f"Found: {anime['title']} (ID: {anime_id})")
    
    # 2. Get Details (for AniList ID)
    info = requests.get(f"{BASE_URL}/info/{anime_id}", headers=HEADERS).json()
    anilist_id = info.get('anilistId')
    
    if not anilist_id:
        print("Could not find AniList ID for streaming.")
        return

    # 3. Get Episodes
    episodes_data = requests.get(f"{BASE_URL}/episodes/{anime_id}", headers=HEADERS).json()
    episodes = episodes_data.get('episodes', [])
    
    print(f"Total episodes found: {len(episodes)}")
    
    # 4. Format Results
    result = {
        "title": info['title'],
        "anilistId": anilist_id,
        "poster": info['poster'],
        "description": info.get('description', ''),
        "genres": info.get('genres', []),
        "episodes": []
    }
    
    for ep in episodes:
        ep_no = ep['episode_no']
        result['episodes'].append({
            "no": ep_no,
            "title": ep['title'],
            "link": f"https://player.videasy.net/anime/{anilist_id}/{ep_no}"
        })
        
    return result

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Naruto"
    data = scrape_anime_direct(query)
    if data:
        filename = f"{data['title'].replace(' ', '_').lower()}_full.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Success! Data saved to {filename}")
        print(f"Sample Link (Ep 1): {data['episodes'][0]['link']}")
