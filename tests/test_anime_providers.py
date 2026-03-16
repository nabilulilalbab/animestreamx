import requests
import time

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

# Data 3 anime: (nama, anilist_id, episode_test)
anime_list = [
    ("Naruto", "20", "1"),
    ("Demon Slayer", "101922", "1"),
    ("Jujutsu Kaisen", "113415", "1")
]

# Provider mapping dari JS (global TV/movie + anime)
providers = [
    # TV/Movie providers (mungkin tidak support anime, tapi kita coba)
    ("streamx", "https://embed.wplay.me/embed/tv/{id}/{s}/{e}", "tv"),
    ("mapi", "https://www.zxcstream.xyz/embed/tv/{id}/{s}/{e}", "tv"),
    ("cinemaos", "https://cinemaos.tech/player/{id}/{s}/{e}", "tv"),
    ("rive", "https://watch.rivestream.app/embed?type=tv&id={id}&season={s}&episode={e}", "tv"),
    ("videasy", "https://player.videasy.net/tv/{id}/{s}/{e}", "tv"),
    ("vidpro", "https://vidlink.pro/tv/{id}/{s}/{e}", "tv"),
    ("vidking", "https://vidking.net/embed/tv/{id}/{s}/{e}", "tv"),
    ("embedcc", "https://www.2embed.cc/embedtv/{id}&s={s}&e={e}", "tv"),
    ("zxcstream", "https://www.zxcstream.xyz/player/tv/{id}/{s}/{e}", "tv"),
    ("french", "https://frembed.buzz/api/serie.php?id={id}&sa={s}&epi={e}", "tv"),
    ("spanish", "https://play.modocine.com/play.php/embed/tv/{id}/{s}/{e}", "tv"),
    ("italian", "https://vixsrc.to/tv/{id}/{s}/{e}?lang=it", "tv"),
    # Anime-specific providers
    ("vidcc-sub", "https://vidsrc.cc/v2/embed/anime/ani{id}/{ep}/sub", "anime"),
    ("vidcc-dub", "https://vidsrc.cc/v2/embed/anime/ani{id}/{ep}/dub", "anime"),
    ("pahe-sub", "https://vidnest.fun/animepahe/{id}/{ep}/sub", "anime"),
    ("pahe-dub", "https://vidnest.fun/animepahe/{id}/{ep}/dub", "anime"),
    ("videasy-sub", "https://player.videasy.net/anime/{id}/{ep}", "anime"),
    ("videasy-dub", "https://player.videasy.net/anime/{id}/{ep}?dub=true", "anime"),
    ("vidnest-sub", "https://vidnest.fun/anime/{id}/{ep}/sub", "anime"),
    ("vidnest-dub", "https://vidnest.fun/anime/{id}/{ep}/dub", "anime"),
]

def test_provider(anime_name, anime_id, episode, provider_name, pattern, provider_type):
    if provider_type == "tv":
        # Untuk TV provider, kita gunakan season=1, episode=1
        url = pattern.replace("{id}", anime_id).replace("{s}", "1").replace("{e}", episode)
    else:  # anime
        url = pattern.replace("{id}", anime_id).replace("{ep}", episode)
    
    try:
        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        status = resp.status_code
        content_type = resp.headers.get('Content-Type', '')
        length = len(resp.text)
        
        # Cek apakah respons mengandung indikator video/embed
        html_lower = resp.text.lower()
        has_video = any(keyword in html_lower for keyword in ['video', 'iframe', 'player', 'stream', 'm3u8', 'mp4'])
        
        return {
            'status': status,
            'content_type': content_type,
            'length': length,
            'has_video_indicator': has_video,
            'url': url
        }
    except Exception as e:
        return {'error': str(e), 'url': url}

print("Testing 3 anime ke semua provider...\n")
results = []

for anime_name, anime_id, episode in anime_list:
    print(f"\n{'='*60}")
    print(f"ANIME: {anime_name} (ID: {anime_id})")
    print(f"{'='*60}")
    
    for provider_name, pattern, provider_type in providers:
        print(f"  Testing {provider_name:15}... ", end='', flush=True)
        result = test_provider(anime_name, anime_id, episode, provider_name, pattern, provider_type)
        
        if 'error' in result:
            print(f"ERROR: {result['error']}")
            results.append((anime_name, provider_name, 'ERROR', result['error']))
        else:
            status = result['status']
            video_ind = "VIDEO" if result['has_video_indicator'] else "NO-VIDEO"
            print(f"Status: {status}, Length: {result['length']}, {video_ind}")
            results.append((anime_name, provider_name, status, video_ind))
        
        time.sleep(0.5)  # Delay kecil agar tidak terlalu banyak request

# Simpan hasil ke file
with open('anime_provider_test_results.txt', 'w') as f:
    f.write("Hasil Testing 3 Anime ke Semua Provider\n")
    f.write("="*60 + "\n")
    for anime_name, anime_id, episode in anime_list:
        f.write(f"\nAnime: {anime_name} (ID: {anime_id}, Episode: {episode})\n")
        f.write("-"*60 + "\n")
        for provider_name, pattern, provider_type in providers:
            # Cari hasil untuk kombinasi ini
            for r in results:
                if r[0] == anime_name and r[1] == provider_name:
                    status = r[2]
                    video_ind = r[3]
                    f.write(f"{provider_name:20} | Status: {status} | {video_ind}\n")
                    break

print(f"\n{'='*60}")
print("Testing selesai! Hasil disimpan ke 'anime_provider_test_results.txt'")

# Tampilkan summary
print("\nSUMMARY:")
for anime_name, anime_id, episode in anime_list:
    print(f"\n{anime_name}:")
    success = sum(1 for r in results if r[0] == anime_name and r[2] == 200)
    total = sum(1 for r in results if r[0] == anime_name)
    print(f"  {success}/{total} provider merespons dengan status 200")