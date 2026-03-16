# StreameX API Go Documentation

StreameX API Go adalah layanan backend berbasis bahasa pemrograman Go yang berfungsi sebagai agregator konten streaming untuk film, serial TV, dan anime. API ini mengintegrasikan metadata dari TMDB (The Movie Database) dan HiAnime untuk menyajikan daftar sumber streaming dari berbagai penyedia layanan pihak ketiga secara dinamis.

## 1. Persyaratan Sistem
- Go 1.25.0 atau versi lebih baru
- Akses internet untuk koneksi ke upstream API (TMDB, HiAnime, PlayerBase)

## 2. Instalasi dan Menjalankan Server
1. Clone repositori ini.
2. Masuk ke direktori proyek:
   ```bash
   cd streamex-api-go
   ```
3. Unduh dependensi:
   ```bash
   go mod download
   ```
4. Jalankan server:
   ```bash
   go run main.go
   ```
   Server akan berjalan secara default pada alamat `http://localhost:5000`.

## 3. Struktur API

### 3.1 Base URL
`http://localhost:5000`

### 3.2 Endpoint Tersedia

#### A. Pencarian Konten (Multi-Search)
Mencari konten lintas kategori (Movie/TV/Anime).
- **URL**: `/api/search`
- **Method**: `GET`
- **Parameter**:
  - `query` (string, wajib): Kata kunci pencarian.
  - `page` (string, opsional): Halaman hasil (default: 1).
- **Contoh Request**: `/api/search?query=naruto`

#### B. Daftar Konten Populer
Menampilkan daftar konten populer berdasarkan kategori.
- **URL**: `/api/list/{category}`
- **Method**: `GET`
- **Parameter**:
  - `category` (path): `movie`, `tv`, atau `anime`.
  - `page` (query): Nomor halaman (default: 1).
- **Contoh Request**: `/api/list/movie?page=2`

#### C. Detail Konten dan Episode
Mengambil informasi mendalam beserta daftar sumber streaming (sources) per episode.
- **URL**: `/api/detail/{category}/{id}`
- **Method**: `GET`
- **Parameter**:
  - `category` (path): `movie`, `tv`, atau `anime`.
  - `id` (path): ID TMDB (numerik) atau ID HiAnime (slug).
  - `season` (query, opsional): Nomor musim (khusus TV, default: 1).
- **Contoh Request**: `/api/detail/movie/810693` (Jujutsu Kaisen 0)

#### D. Status Kesehatan Provider
Memeriksa status ketersediaan dan waktu respons semua provider streaming.
- **URL**: `/api/providers/health`
- **Method**: `GET`

## 4. Logika Kategori dan Mapping Provider

### 4.1 Kategori Anime
Jika ID mengandung tanda hubung (slug) atau kategori ditentukan sebagai `anime`, API akan melakukan mapping ke provider khusus anime (vidcc, pahe, videasy, vidnest).

### 4.2 Kategori Movie & TV (Animation Mapping)
Untuk konten kategori `movie` atau `tv` yang memiliki genre "Animation", API secara otomatis menjalankan fungsi `findAnimeMapping`. Fungsi ini mencari kecocokan di database anime untuk menyuntikkan provider anime ke dalam daftar sumber streaming TMDB.

## 5. Struktur Data Respons Streaming

Setiap objek episode dalam respons `/api/detail` berisi array `sources`. Contoh struktur data:

```json
{
  "episode_number": 1,
  "name": "Full Movie",
  "sources": [
    {
      "provider": "streamx",
      "url": "https://embed.wplay.me/embed/movie/810693"
    },
    {
      "provider": "vidcc-sub",
      "url": "https://vidsrc.cc/v2/embed/anime/ani131573/1/sub"
    }
  ]
}
```

## 6. Cara Mengonsumsi API (Usage Example)

Untuk memutar konten di sisi klien (Frontend), ambil URL dari array `sources` dan masukkan ke dalam elemen `iframe`.

**Contoh Implementasi JavaScript (Fetch API):**

```javascript
async function getStreamLink(type, id) {
  const response = await fetch(`http://localhost:5000/api/detail/${type}/${id}`);
  const data = await response.json();
  
  // Mengambil sumber pertama dari episode pertama
  if (data.episodes && data.episodes.length > 0) {
    const firstSource = data.episodes[0].sources[0];
    console.log(`Memutar dari provider: ${firstSource.provider}`);
    console.log(`URL Iframe: ${firstSource.url}`);
    return firstSource.url;
  }
}
```

## 7. Daftar Provider yang Didukung
- **Standard (TV/Movie)**: streamx, mapi, cinemaos, rive, videasy, vidpro, vidking, embedcc, zxcstream, french, spanish, italian.
- **Anime Specific**: vidcc (sub/dub), pahe (sub/dub), videasy (sub/dub), vidnest (sub/dub).
