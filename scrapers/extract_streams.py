import json
from bs4 import BeautifulSoup
import os
import re

def extract_id_from_iframe_file(folder_path):
    """Mencari ID di dalam folder _files (biasanya di 1.html atau 1(1).html)."""
    if not os.path.exists(folder_path):
        return None
    
    for filename in ['1.html', '1(1).html']:
        file_path = os.path.join(folder_path, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(500) # Cukup baca awal file
                # Cari URL videasy
                match = re.search(r'player\.videasy\.net/anime/([^/]+)/', content)
                if match:
                    return match.group(1)
    return None

def get_episodes(soup):
    ep_numbers = []
    # Pendekatan lebih robust: cari di sidebar episode
    buttons = soup.find_all('button')
    for btn in buttons:
        # Cari span dengan nomor "1.", "2.", dst
        num_span = btn.find('span', string=re.compile(r'^\d+\.$'))
        if num_span:
            num = num_span.text.strip('.')
            if num not in ep_numbers:
                ep_numbers.append(num)
    
    if not ep_numbers:
        # Fallback: cari angka saja di tombol yang mungkin episode
        for btn in buttons:
            txt = btn.get_text(strip=True)
            if txt.isdigit():
                ep_numbers.append(txt)
                
    return sorted(list(set(ep_numbers)), key=int) if ep_numbers else []

def analyze_and_generate_links(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    
    title_tag = soup.find('title')
    title = title_tag.text.replace('| StreameX', '').strip() if title_tag else "Unknown"
    
    # 1. Coba ambil ID dari iframe langsung
    ani_id = None
    iframe = soup.find('iframe', title='Video Player')
    if iframe and 'src' in iframe.attrs:
        src = iframe['src']
        match = re.search(r'anime/([^/]+)/', src)
        if match: ani_id = match.group(1)
    
    # 2. Jika gagal (karena local link), cari di folder _files
    if not ani_id or ani_id == '.':
        folder_files = file_path.replace('.html', '_files')
        ani_id = extract_id_from_iframe_file(folder_files)
    
    # 3. Fallback Khusus Naruto (berdasarkan data manual jika file rusak)
    if not ani_id:
        if "Shippuden" in title: ani_id = "1735"
        elif "Naruto" in title and "Spin-Off" not in title: ani_id = "20"

    ep_list = get_episodes(soup)
    
    streams = []
    if ani_id:
        for ep in ep_list:
            streams.append({
                'episode': ep,
                'link_sub': f"https://player.videasy.net/anime/{ani_id}/{ep}",
                'link_dub': f"https://player.videasy.net/anime/{ani_id}/{ep}?dub=true"
            })
    
    return {
        'title': title,
        'anilist_id': ani_id,
        'total_episodes': len(ep_list),
        'streams': streams
    }

if __name__ == "__main__":
    html_files = [f for f in os.listdir('.') if f.endswith('.html') and 'Anime' not in f]
    
    for file in html_files:
        try:
            anime = analyze_and_generate_links(file)
            print("="*60)
            print(f"ANIME: {anime['title']}")
            print(f"Stream ID: {anime['anilist_id']}")
            print(f"Total Episode: {anime['total_episodes']}")
            
            if anime['streams']:
                # Print 2 episode pertama dan terakhir
                first_two = anime['streams'][:2]
                last_one = anime['streams'][-1:] if len(anime['streams']) > 2 else []
                
                for s in first_two:
                    print(f"Ep {s['episode']} [SUB]: {s['link_sub']}")
                
                if last_one:
                    if anime['total_episodes'] > 3: print("...")
                    for s in last_one:
                        print(f"Ep {s['episode']} [SUB]: {s['link_sub']}")
            else:
                print("Link streaming tidak dapat dibuat.")
        except Exception as e:
            print(f"Error: {file} -> {e}")
