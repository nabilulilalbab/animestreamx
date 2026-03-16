package main

import (
	"fmt"
	"strings"
	"time"

	_ "streamex-api-go/docs"

	"github.com/go-resty/resty/v2"
	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/gofiber/swagger"
)

// ProviderConfig menyimpan konfigurasi untuk setiap provider
type ProviderConfig struct {
	Name   string            // Nama provider
	Type   string            // Jenis konten: "tv", "movie", "anime"
	URL    string            // Template URL
	Params map[string]string // Parameter tambahan
}

// Daftar provider yang didukung
var providerRegistry = []ProviderConfig{
	// Provider untuk TV/Movie
	{Name: "streamx", Type: "tv", URL: "https://embed.wplay.me/embed/tv/{id}/{season}/{episode}"},
	{Name: "mapi", Type: "tv", URL: "https://www.zxcstream.xyz/embed/tv/{id}/{season}/{episode}"},
	{Name: "cinemaos", Type: "tv", URL: "https://cinemaos.tech/player/{id}/{season}/{episode}"},
	{Name: "rive", Type: "tv", URL: "https://watch.rivestream.app/embed?type=tv&id={id}&season={season}&episode={episode}"},
	{Name: "videasy", Type: "tv", URL: "https://player.videasy.net/tv/{id}/{season}/{episode}"},
	{Name: "vidpro", Type: "tv", URL: "https://vidlink.pro/tv/{id}/{season}/{episode}"},
	{Name: "vidking", Type: "tv", URL: "https://vidking.net/embed/tv/{id}/{season}/{episode}"},
	{Name: "embedcc", Type: "tv", URL: "https://www.2embed.cc/embedtv/{id}&s={season}&e={episode}"},
	{Name: "zxcstream", Type: "tv", URL: "https://www.zxcstream.xyz/player/tv/{id}/{season}/{episode}"},
	{Name: "french", Type: "tv", URL: "https://frembed.buzz/api/serie.php?id={id}&sa={season}&epi={episode}"},
	{Name: "spanish", Type: "tv", URL: "https://play.modocine.com/play.php/embed/tv/{id}/{season}/{episode}"},
	{Name: "italian", Type: "tv", URL: "https://vixsrc.to/tv/{id}/{season}/{episode}?lang=it"},

	// Provider untuk Anime
	{Name: "vidcc-sub", Type: "anime", URL: "https://vidsrc.cc/v2/embed/anime/ani{id}/{episode}/sub"},
	{Name: "vidcc-dub", Type: "anime", URL: "https://vidsrc.cc/v2/embed/anime/ani{id}/{episode}/dub"},
	{Name: "pahe-sub", Type: "anime", URL: "https://vidnest.fun/animepahe/{id}/{episode}/sub"},
	{Name: "pahe-dub", Type: "anime", URL: "https://vidnest.fun/animepahe/{id}/{episode}/dub"},
	{Name: "videasy-sub", Type: "anime", URL: "https://player.videasy.net/anime/{id}/{episode}"},
	{Name: "videasy-dub", Type: "anime", URL: "https://player.videasy.net/anime/{id}/{episode}?dub=true"},
	{Name: "vidnest-sub", Type: "anime", URL: "https://vidnest.fun/anime/{id}/{episode}/sub"},
	{Name: "vidnest-dub", Type: "anime", URL: "https://vidnest.fun/anime/{id}/{episode}/dub"},
}

// getSources menghasilkan daftar sumber streaming untuk konten tertentu
func getSources(mediaType, id, season, episode string) []map[string]string {
	sources := []map[string]string{}

	for _, provider := range providerRegistry {
		if provider.Type != mediaType {
			continue
		}

		url := provider.URL
		url = strings.ReplaceAll(url, "{id}", id)
		url = strings.ReplaceAll(url, "{season}", season)
		url = strings.ReplaceAll(url, "{episode}", episode)

		sources = append(sources, map[string]string{
			"provider": provider.Name,
			"url":      url,
		})
	}

	return sources
}

const (
	StreamExBase = "https://streamex.sh/api"
	PlayerBase   = "https://player.videasy.net"
)

var (
	client = resty.New()
)

func init() {
	client.SetHeaders(map[string]string{
		"User-Agent":         "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
		"Referer":            "https://streamex.sh/",
		"Accept":             "*/*",
		"Accept-Language":    "en-US,en;q=0.5",
		"Sec-Ch-Ua-Platform": "\"Linux\"",
		"Sec-Fetch-Dest":     "empty",
		"Sec-Fetch-Mode":     "cors",
		"Sec-Fetch-Site":     "same-origin",
	})
}

func safeStringID(id interface{}) string {
	if id == nil {
		return ""
	}
	switch v := id.(type) {
	case float64:
		return fmt.Sprintf("%.0f", v)
	case string:
		return v
	default:
		return fmt.Sprintf("%v", v)
	}
}

// findAnimeMapping mencari ID anime (Anilist/MAL) berdasarkan judul
func findAnimeMapping(title string) string {
	var searchData map[string]interface{}
	resp, err := client.R().
		SetQueryParam("query", title).
		SetResult(&searchData).
		Get(StreamExBase + "/hianime/search")

	if err != nil || resp.IsError() {
		return ""
	}

	results, ok := searchData["results"].([]interface{})
	if !ok || len(results) == 0 {
		return ""
	}

	// Ambil slug ID dari hasil pertama
	first := results[0].(map[string]interface{})
	slugID := safeStringID(first["id"])

	var infoData map[string]interface{}
	respInfo, err := client.R().
		SetResult(&infoData).
		Get(StreamExBase + "/hianime/info/" + slugID)

	if err != nil || respInfo.IsError() {
		return ""
	}

	// Prioritaskan anilistId, fallback ke malId
	anilistID := safeStringID(infoData["anilistId"])
	if anilistID == "" || anilistID == "0" {
		anilistID = safeStringID(infoData["malId"])
	}

	return anilistID
}

// ProviderStatus melaporkan status kesehatan provider
// swagger:model
type ProviderStatus struct {
	Name     string `json:"name"`                    // Nama provider
	Type     string `json:"type"`                    // Jenis konten: tv, movie, anime
	Status   string `json:"status"`                  // Status: up, down, unstable
	Response int    `json:"response_time,omitempty"` // Waktu respons dalam ms
	Error    string `json:"error,omitempty"`         // Pesan error jika ada
}

// HealthCheckHandler memeriksa kesehatan semua provider
// @Summary      Dapatkan status kesehatan semua provider
// @Description  Memeriksa ketersediaan dan waktu respons semua provider streaming
// @Tags         providers
// @Accept       json
// @Produce      json
// @Success      200  {array}   ProviderStatus
// @Failure      500  {object}  map[string]string
// @Router       /api/providers/health [get]
func HealthCheckHandler(c *fiber.Ctx) error {
	results := make([]ProviderStatus, 0, len(providerRegistry))
	statusChan := make(chan ProviderStatus, len(providerRegistry))

	// Test semua provider secara konkuren
	for _, p := range providerRegistry {
		go func(provider ProviderConfig) {
			start := time.Now()
			status := ProviderStatus{
				Name: provider.Name,
				Type: provider.Type,
			}

			// Buat URL tes berdasarkan jenis provider
			testURL := provider.URL
			if provider.Type == "tv" {
				testURL = strings.ReplaceAll(testURL, "{id}", "1399") // ID Game of Thrones
				testURL = strings.ReplaceAll(testURL, "{season}", "1")
				testURL = strings.ReplaceAll(testURL, "{episode}", "1")
			} else {
				testURL = strings.ReplaceAll(testURL, "{id}", "20") // ID Naruto
				testURL = strings.ReplaceAll(testURL, "{episode}", "1")
			}

			resp, err := client.R().Get(testURL)
			elapsed := int(time.Since(start).Milliseconds())

			if err != nil {
				status.Status = "down"
				status.Error = err.Error()
			} else if resp.StatusCode() >= 200 && resp.StatusCode() < 300 {
				status.Status = "up"
				status.Response = elapsed
			} else {
				status.Status = "unstable"
				status.Response = elapsed
				status.Error = fmt.Sprintf("Status %d", resp.StatusCode())
			}

			statusChan <- status
		}(p)
	}

	// Kumpulkan hasil
	for i := 0; i < len(providerRegistry); i++ {
		results = append(results, <-statusChan)
	}

	return c.JSON(results)
}

func main() {
	app := fiber.New()
	app.Use(logger.New())
	app.Use(cors.New(cors.Config{
		AllowOrigins: "*",
		AllowHeaders: "Origin, Content-Type, Accept",
	}))

	app.Get("/swagger/*", swagger.HandlerDefault)

	app.Get("/api/search", SearchHandler)
	app.Get("/api/list/:category", ListHandler)
	app.Get("/api/detail/:category/:id", DetailHandler)
	app.Get("/api/providers/health", HealthCheckHandler) // Endpoint baru

	app.Listen(":5000")
}

// SearchHandler mencari film, serial TV, atau anime
// @Summary      Cari konten
// @Description  Mencari film, serial TV, atau anime berdasarkan query
// @Tags         search
// @Accept       json
// @Produce      json
// @Param        query    query     string  true  "Kata kunci pencarian"
// @Param        page     query     string  false "Halaman" default(1)
// @Success      200      {array}   map[string]interface{}
// @Failure      500      {object}  map[string]string
// @Router       /api/search [get]
func SearchHandler(c *fiber.Ctx) error {
	query := c.Query("query")
	page := c.Query("page", "1")
	if query == "" {
		return c.JSON([]interface{}{})
	}

	var data map[string]interface{}
	resp, err := client.R().
		SetQueryParams(map[string]string{"query": query, "page": page}).
		SetResult(&data).
		Get(StreamExBase + "/tmdb/search/multi")

	if err != nil || resp.IsError() {
		return c.Status(500).JSON(fiber.Map{"error": "Failed to fetch search results"})
	}

	results := []map[string]interface{}{}
	if rawResults, ok := data["results"].([]interface{}); ok {
		for _, itemRaw := range rawResults {
			item, ok := itemRaw.(map[string]interface{})
			if !ok || item["media_type"] == "person" {
				continue
			}

			title := item["name"]
			if title == nil || title == "" {
				title = item["title"]
			}

			item["id"] = safeStringID(item["id"])
			item["title"] = title
			if p, ok := item["poster_path"].(string); ok && p != "" {
				item["poster"] = "https://image.tmdb.org/t/p/w342" + p
			}
			item["type"] = item["media_type"] // 'tv' or 'movie'
			results = append(results, item)
		}
	}
	return c.JSON(results)
}

// ListHandler menampilkan daftar konten populer berdasarkan kategori
// @Summary      Daftar konten populer
// @Description  Menampilkan daftar film, serial TV, atau anime populer
// @Tags         content
// @Accept       json
// @Produce      json
// @Param        category  path      string  true  "Kategori: tv, movie, anime"
// @Param        page      query     string  false "Halaman" default(1)
// @Success      200       {array}   map[string]interface{}
// @Failure      500       {object}  map[string]string
// @Router       /api/list/{category} [get]
func ListHandler(c *fiber.Ctx) error {
	category := strings.ToLower(c.Params("category"))
	page := c.Query("page", "1")

	var url string
	if category == "anime" {
		url = StreamExBase + "/hianime/most-popular?page=" + page
	} else {
		// TMDB API requires lowercase 'tv' or 'movie'
		url = fmt.Sprintf("%s/tmdb/%s/popular?page=%s", StreamExBase, category, page)
	}

	var data map[string]interface{}
	resp, err := client.R().SetResult(&data).Get(url)
	if err != nil || resp.IsError() {
		return c.Status(500).JSON(fiber.Map{"error": fmt.Sprintf("StreamEx API Error: %v", resp.Status())})
	}

	results := []map[string]interface{}{}
	if rawResults, ok := data["results"].([]interface{}); ok {
		for _, itemRaw := range rawResults {
			item, ok := itemRaw.(map[string]interface{})
			if !ok {
				continue
			}

			if category == "anime" {
				// PENTING: Paksa type menjadi 'anime' agar frontend tidak bingung dengan type 'TV' asli dari API
				item["type"] = "anime"
				results = append(results, item)
			} else {
				title := item["name"]
				if title == nil || title == "" {
					title = item["title"]
				}
				item["id"] = safeStringID(item["id"])
				item["title"] = title
				if p, ok := item["poster_path"].(string); ok && p != "" {
					item["poster"] = "https://image.tmdb.org/t/p/w342" + p
				}
				item["type"] = category
				results = append(results, item)
			}
		}
	}
	return c.JSON(results)
}

// DetailHandler menampilkan detail konten dan episode
// @Summary      Detail konten
// @Description  Menampilkan detail film, serial TV, atau anime beserta episode
// @Tags         content
// @Accept       json
// @Produce      json
// @Param        category  path      string  true  "Kategori: tv, movie, anime"
// @Param        id        path      string  true  "ID konten"
// @Param        season    query     string  false "Musim (hanya untuk TV)" default(1)
// @Success      200       {object}  map[string]interface{}
// @Failure      404       {object}  map[string]string
// @Failure      500       {object}  map[string]string
// @Router       /api/detail/{category}/{id} [get]
func DetailHandler(c *fiber.Ctx) error {
	category := strings.ToLower(c.Params("category"))
	id := c.Params("id")

	// Deteksi otomatis jika ID mengandung tanda hubung (slug), itu pasti Anime
	if strings.Contains(id, "-") {
		category = "anime"
	}

	if category == "anime" {
		var info map[string]interface{}
		var eps map[string]interface{}
		errChan := make(chan error, 2)

		go func() {
			_, err := client.R().SetResult(&info).Get(StreamExBase + "/hianime/info/" + id)
			errChan <- err
		}()
		go func() {
			_, err := client.R().SetResult(&eps).Get(StreamExBase + "/hianime/episodes/" + id)
			errChan <- err
		}()

		for i := 0; i < 2; i++ {
			if err := <-errChan; err != nil {
				return c.Status(500).JSON(fiber.Map{"error": "Failed to fetch anime data"})
			}
		}

		if info == nil || info["title"] == nil {
			return c.Status(404).JSON(fiber.Map{"error": "Anime not found"})
		}

		anilistID := safeStringID(info["anilistId"])
		if epsList, ok := eps["episodes"].([]interface{}); ok {
			for _, epRaw := range epsList {
				ep := epRaw.(map[string]interface{})
				episodeNo := fmt.Sprintf("%v", ep["episode_no"])
				ep["sources"] = getSources("anime", anilistID, "1", episodeNo)
			}
			info["episodes"] = epsList
		}
		info["type"] = "anime"
		return c.JSON(info)
	} else {
		// Handle TV and Movie from TMDB
		if category != "tv" && category != "movie" {
			category = "tv" // Default fallback
		}

		season := c.Query("season", "1")
		var info map[string]interface{}

		// 1. Ambil info utama (Movie/TV)
		respInfo, err := client.R().SetResult(&info).Get(fmt.Sprintf("%s/tmdb/%s/%s", StreamExBase, category, id))
		if err != nil || respInfo.IsError() {
			return c.Status(404).JSON(fiber.Map{"error": "Content not found on TMDB"})
		}

		tmdbID := safeStringID(info["id"])

		// 2. Normalisasi Field (TV menggunakan 'name', Movie menggunakan 'title')
		title := info["name"]
		if title == nil || title == "" {
			title = info["title"]
		}
		info["title"] = title
		info["description"] = info["overview"]
		if p, ok := info["poster_path"].(string); ok && p != "" {
			info["poster"] = "https://image.tmdb.org/t/p/w500" + p
		}
		info["tmdbId"] = tmdbID
		info["type"] = category

		// Deteksi Genre Animation
		isAnimation := false
		if genres, ok := info["genres"].([]interface{}); ok {
			for _, gRaw := range genres {
				g := gRaw.(map[string]interface{})
				name := strings.ToLower(safeStringID(g["name"]))
				if name == "animation" {
					isAnimation = true
					break
				}
			}
		}

		// Cari mapping anime jika konten adalah animasi
		animeID := ""
		if isAnimation {
			animeID = findAnimeMapping(title.(string))
		}

		// 3. Handle Episode/Sources logic
		if category == "tv" {
			var eps map[string]interface{}
			client.R().SetResult(&eps).Get(fmt.Sprintf("%s/tmdb/tv/%s/season/%s", StreamExBase, id, season))

			if epsList, ok := eps["episodes"].([]interface{}); ok {
				for _, epRaw := range epsList {
					ep := epRaw.(map[string]interface{})
					episodeNo := fmt.Sprintf("%v", ep["episode_number"])

					// Gabungkan sumber Movie/TV standar dan Anime (jika ada)
					sources := getSources("tv", tmdbID, season, episodeNo)
					if animeID != "" {
						animeSources := getSources("anime", animeID, "1", episodeNo)
						sources = append(sources, animeSources...)
					}
					ep["sources"] = sources
				}
				info["episodes"] = epsList
			}
			info["seasons_count"] = info["number_of_seasons"]
		} else {
			// Jika Movie, buat 1 episode dummy agar provider tetap muncul
			sources := getSources("tv", tmdbID, "1", "1")
			if animeID != "" {
				animeSources := getSources("anime", animeID, "1", "1")
				sources = append(sources, animeSources...)
			}

			info["episodes"] = []map[string]interface{}{
				{
					"episode_number": 1,
					"name":           "Full Movie",
					"sources":        sources,
				},
			}
			info["seasons_count"] = 0
		}

		return c.JSON(info)
	}
}
