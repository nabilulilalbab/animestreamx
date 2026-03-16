import json
from bs4 import BeautifulSoup
import os
import re

def get_full_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Ambil Metadata dari ld+json
    ld_json_tag = soup.find('script', type='application/ld+json')
    ld_json = json.loads(ld_json_tag.string) if ld_json_tag else {}
    
    # Ambil ID dari link canonical atau iframe
    folder_files = file_path.replace('.html', '_files')
    ani_id = None
    for filename in ['1.html', '1(1).html']:
        path = os.path.join(folder_files, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                c = f.read(500)
                m = re.search(r'player\.videasy\.net/anime/([^/]+)/', c)
                if m: ani_id = m.group(1); break
    
    # Fallback ID
    if not ani_id:
        if "Shippuden" in file_path: ani_id = "1735"
        elif "Naruto" in file_path and "Spin-Off" not in file_path: ani_id = "20"

    # Ekstrak Episode (Unik)
    episodes = []
    seen = set()
    for btn in soup.find_all('button'):
        num_span = btn.find('span', string=re.compile(r'^\d+\.$'))
        name_span = num_span.find_next_sibling('span') if num_span else None
        if num_span and name_span:
            num = num_span.text.strip('.')
            name = name_span.text.strip()
            if num not in seen:
                episodes.append({'number': num, 'title': name})
                seen.add(num)
    
    # Urutkan episode
    episodes.sort(key=lambda x: int(x['number']))

    return {
        "id": ani_id,
        "title": ld_json.get('name', 'Unknown'),
        "poster": ld_json.get('image', ''),
        "description": ld_json.get('description', 'No description available.'),
        "genres": ld_json.get('genre', []),
        "episodes": episodes
    }

if __name__ == "__main__":
    html_files = [f for f in os.listdir('.') if f.endswith('.html') and 'Anime' not in f]
    database = []
    for file in html_files:
        print(f"Processing {file}...")
        database.append(get_full_data(file))
    
    with open('anime_db.json', 'w') as f:
        json.dump(database, f, indent=4)
    print(f"Done! {len(database)} anime saved to anime_db.json")
