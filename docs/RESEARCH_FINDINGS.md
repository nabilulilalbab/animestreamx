# Research Findings: StreameX Scraper Provider Mapping

## Overview
Based on analysis of the JavaScript file `68d250667a7f6da4.js` and direct API testing, we have uncovered the complete provider mapping used by StreameX. This includes both global TV/movie providers and anime-specific providers.

## Provider Mapping

### Global TV/Movie Providers
| Flag     | Domain Provider      | URL Pattern (TV)                                      |
|----------|----------------------|-------------------------------------------------------|
| streamx  | embed.wplay.me       | `/embed/tv/{id}/{s}/{e}`                              |
| mapi     | zxcstream.xyz        | `/embed/tv/{id}/{s}/{e}`                              |
| cinemaos | cinemaos.tech        | `/player/{id}/{s}/{e}`                                |
| rive     | rivestream.app       | `/embed?type=tv&id={id}&season={s}&episode={e}`       |
| videasy  | player.videasy.net   | `/tv/{id}/{s}/{e}`                                    |
| vidpro   | vidlink.pro          | `/tv/{id}/{s}/{e}`                                    |
| vidking  | vidking.net          | `/embed/tv/{id}/{s}/{e}`                              |

### Anime-Specific Providers
| Flag         | URL Pattern                                      | Notes                          |
|--------------|--------------------------------------------------|--------------------------------|
| vidcc-sub    | vidsrc.cc/v2/embed/anime/ani{id}/{ep}/sub       | Most recommended              |
| vidcc-dub    | vidsrc.cc/v2/embed/anime/ani{id}/{ep}/dub       |                                |
| pahe-sub     | vidnest.fun/animepahe/{id}/{ep}/sub             | Source from AnimePahe         |
| videasy-sub  | player.videasy.net/anime/{id}/{ep}              | Default source currently      |
| videasy-dub  | player.videasy.net/anime/{id}/{ep}?dub=true     | How to get dub on videasy     |

## API Endpoints Discovered

### 1. Database API (`db.videasy.net`)
- Base URL: `https://db.videasy.net/3`
- Status: Returns 204 No Content (likely health check)
- Used as Axios base URL in the frontend.

### 2. Streaming Sources API (`api.videasy.net`)
- Endpoint: `https://api.videasy.net/hianime/sources-with-title`
- Parameters: `title`, `year`, `episodeId`, `dub`
- Returns JSON with:
  - `details`: anime metadata and episode list
  - `mediaSources`: contains `sources` (video URLs) and `subtitles`
- Example response for "Naruto" (2002) includes 220 episodes and a single source URL that is obfuscated.

### 3. Tracking API (`users.videasy.net`)
- Endpoint: `https://users.videasy.net/api/track`
- Method: POST
- Expected payload includes discriminator field `type` with values: `pageview`, `custom_event`, `performance`, `error`
- Without proper payload, returns 400 error.

### 4. Provider APIs
- `cinemaos.tech/api/providerv2` - Returns error "Failed to fetch media sources" without parameters.
- `streams.smashystream.top/proxy/m3u8/{BASE64_ENCODED_URL}/{JSON_HEADERS}` - Proxy for m3u8 streams.

## Obfuscation Patterns

### 1. Source URL Obfuscation
The video source URL returned by `sources-with-title` is heavily obfuscated:
- Format: `https://p.10020.workers.dev/afc7d47f/{LONG_TOKEN}.m3u8`
- The token appears to be a base64-like string with URL-safe characters.
- This is likely a Cloudflare Worker that decrypts the token to the actual m3u8 URL.

### 2. Encryption in Provider Responses
According to the analysis, some provider APIs (e.g., `cinemaos.tech/api/providerv2`) return JSON that is encrypted. The frontend likely decrypts it using a client-side key.

### 3. Tracking Requirement
Before video playback, the frontend must send a tracking request to `users.videasy.net/api/track` to activate the streaming session. Without this, the session may expire.

## Testing Results

All provider URLs are live and return HTML embed pages (status 200). This confirms the mapping is accurate and can be used directly.

## Recommendations for Direct Access

1. **For anime streaming**: Use `api.videasy.net/hianime/sources-with-title` with proper title and episode ID.
2. **For direct provider access**: Use the provider URLs directly with the appropriate ID mapping (TMDB ID for TV/movies, AniList ID for anime).
3. **Tracking**: Implement a POST request to the tracking endpoint with a valid payload to ensure session activation.
4. **Proxy handling**: The m3u8 URLs are proxied through Cloudflare Workers; the token may need to be decoded or the worker may be bypassable.

## Next Steps

- Reverse engineer the token generation algorithm to obtain direct m3u8 URLs.
- Investigate the encryption used by cinemaos and other providers.
- Build a comprehensive scraper that mimics the frontend's API calls.

## Files Created During Research

- `test_db_videasy.py` - Initial API testing
- `analyze_api.py` - Comprehensive endpoint testing
- `test_providers.py` - Provider URL validation
- `sources_response.json` - Full API response example

## Conclusion

The provider mapping is a "gold mine" as described, providing direct access to multiple streaming sources. With proper implementation, a robust scraper can be built that bypasses the StreameX frontend entirely.