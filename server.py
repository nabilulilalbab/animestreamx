from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Referer": "https://streamex.sh/",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Sec-Ch-Ua-Platform": "\"Linux\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}

STREAMEX_BASE = "https://streamex.sh/api"

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('query')
    page = request.args.get('page', '1')
    if not query:
        return jsonify([])
    
    # Using multi search as requested (covers TV and Movies)
    url = f"{STREAMEX_BASE}/tmdb/search/multi?query={query}&page={page}"
    
    try:
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        
        results = []
        for item in data.get('results', []):
            # Skip persons, only want visual content
            if item.get('media_type') == 'person':
                continue
                
            results.append({
                "id": str(item['id']),
                "title": item.get('name') or item.get('title'),
                "poster": f"https://image.tmdb.org/t/p/w342{item['poster_path']}" if item.get('poster_path') else None,
                "type": item.get('media_type', 'tv'),
                "overview": item.get('overview')
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/list/<category>', methods=['GET'])
def get_list(category):
    page = request.args.get('page', '1')
    if category == 'anime':
        url = f"{STREAMEX_BASE}/hianime/most-popular?page={page}"
    else: # tv or movie
        url = f"{STREAMEX_BASE}/tmdb/{category}/popular?page={page}"
    
    try:
        res = requests.get(url, headers=HEADERS)
        data = res.json()
        
        # Normalize data format
        results = []
        if category == 'anime':
            results = data.get('results', [])
        else:
            # TMDB format conversion
            for item in data.get('results', []):
                results.append({
                    "id": str(item['id']),
                    "title": item.get('name') or item.get('title'),
                    "poster": f"https://image.tmdb.org/t/p/w342{item['poster_path']}" if item.get('poster_path') else None,
                    "type": category
                })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/detail/<category>/<item_id>', methods=['GET'])
def get_detail(category, item_id):
    try:
        if category == 'anime':
            info = requests.get(f"{STREAMEX_BASE}/hianime/info/{item_id}", headers=HEADERS).json()
            eps = requests.get(f"{STREAMEX_BASE}/hianime/episodes/{item_id}", headers=HEADERS).json()
            return jsonify({
                "title": info['title'],
                "poster": info['poster'],
                "description": info.get('description'),
                "anilistId": info.get('anilistId'),
                "episodes": eps.get('episodes', []),
                "type": "anime"
            })
        else:
            # TV Show detail
            info = requests.get(f"{STREAMEX_BASE}/tmdb/tv/{item_id}", headers=HEADERS).json()
            # Default to season 1 for now
            season = request.args.get('season', '1')
            eps = requests.get(f"{STREAMEX_BASE}/tmdb/tv/{item_id}/season/{season}", headers=HEADERS).json()
            return jsonify({
                "title": info.get('name'),
                "poster": f"https://image.tmdb.org/t/p/w500{info['poster_path']}",
                "description": info.get('overview'),
                "tmdbId": str(info['id']),
                "seasons_count": info.get('number_of_seasons', 1),
                "episodes": eps.get('episodes', []),
                "type": "tv"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
