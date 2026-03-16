import json
from bs4 import BeautifulSoup
import os
import re

def analyze_anime_page(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Extract Structured Data (ld+json)
    ld_json_tag = soup.find('script', type='application/ld+json')
    ld_json = json.loads(ld_json_tag.string) if ld_json_tag else {}
    
    # 2. Extract Basic Info
    # Canonical link often contains the clean URL and ID
    canonical = soup.find('link', rel='canonical')
    url = canonical['href'] if canonical else ""
    
    # Extract ID from URL (e.g., https://streamex.sh/watch/anime/jujutsu-kaisen-20401)
    anime_id = ""
    if url:
        match = re.search(r'/anime/([^/?#]+)', url)
        if match:
            anime_id = match.group(1)

    title_tag = soup.find('span', class_=lambda x: x and 'text-lg' in x and 'mr-2' in x)
    if not title_tag:
        title_tag = soup.find('span', class_=lambda x: x and 'xl:text-' in x and 'font-semibold' in x)
    title = title_tag.text.strip() if title_tag else ld_json.get('name')
    
    # 3. Extract Episodes (Avoiding duplicates from mobile/desktop view)
    episodes = []
    seen_episodes = set()
    
    buttons = soup.find_all('button')
    for btn in buttons:
        num_span = btn.find('span', string=lambda s: s and s.strip().endswith('.') and s.strip()[:-1].isdigit())
        if num_span:
            ep_num = num_span.text.strip('.')
            name_span = num_span.find_next_sibling('span')
            if name_span:
                ep_name = name_span.text.strip()
                if (ep_num, ep_name) not in seen_episodes:
                    episodes.append({
                        'number': ep_num,
                        'name': ep_name
                    })
                    seen_episodes.add((ep_num, ep_name))
    
    # 4. Extract Genres
    genres = []
    genre_container = soup.find('div', class_='flex gap-2 flex-wrap items-center')
    if genre_container:
        genres = [btn.text.strip() for btn in genre_container.find_all('button')]
    elif 'genre' in ld_json:
        genres = ld_json['genre']
    
    # 5. Extract Server info
    iframe = soup.find('iframe', title='Video Player')
    iframe_src = iframe['src'] if iframe else None
    
    return {
        'id': anime_id,
        'title': title,
        'genres': genres,
        'episodes_count': len(episodes),
        'episodes_sample': episodes[:3],
        'iframe_src': iframe_src
    }

if __name__ == "__main__":
    html_files = [f for f in os.listdir('.') if f.endswith('.html') and 'Anime' not in f]
    
    all_results = []
    for file in html_files:
        try:
            result = analyze_anime_page(file)
            all_results.append(result)
        except Exception as e:
            print(f"Error analyzing {file}: {e}")
    
    # Print summary
    print(f"{'ID':<40} | {'Title':<40} | {'Eps':<5}")
    print("-" * 90)
    for res in sorted(all_results, key=lambda x: x['title']):
        print(f"{res['id']:<40} | {res['title']:<40} | {res['episodes_count']:<5}")
    
    print(f"\nTotal anime analyzed: {len(all_results)}")
