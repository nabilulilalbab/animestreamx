# Streamex API Go

API untuk mengakses konten streaming dari berbagai provider.

## Peningkatan Multi-Provider

### Rencana Implementasi

1. **Registri Provider**
   - Konfigurasi template URL untuk semua provider
   - Klasifikasi provider berdasarkan jenis konten (TV, film, anime)

2. **Endpoint Detail**
   - Modifikasi respons untuk menyertakan semua sumber streaming yang tersedia
   - Struktur respons baru:
     ```json
     {
       "episodes": [
         {
           "episode_no": 1,
           "sources": [
             {"provider": "streamx", "url": "https://..."},
             {"provider": "vidcc-sub", "url": "https://..."}
           ]
         }
       ]
     }
     ```

3. **Endpoint Kesehatan Provider**
   - `GET /api/providers/health`
   - Memantau status ketersediaan setiap provider

4. **Dokumentasi**
   - Pembaruan dokumentasi Swagger untuk endpoint baru
   - Penambahan contoh respons multi-provider

### Manfaat
- Dukungan penuh untuk 20 provider
- Failover otomatis ke provider yang tersedia
- Peningkatan ketersediaan konten

### Timeline
1. Fase 1: Implementasi registri provider - 1 hari
2. Fase 2: Modifikasi endpoint detail - 2 hari
3. Fase 3: Pengujian integrasi - 1 hari