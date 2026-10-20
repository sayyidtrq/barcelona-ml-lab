# Decision Log

Catat keputusan penting di sini (tanggal, keputusan, alasan, alternatif).

| Tanggal | Keputusan | Alasan |
|---|---|---|
| 2026-10-09 | Split data berbasis waktu, bukan random | Hindari leakage; meniru kondisi prediksi nyata |
| 2026-10-11 | Sumber utama: football-data.co.uk, simpan semua laga La Liga (bukan cuma Barca) | Gratis, ada odds untuk baseline pasar; laga tim lain dibutuhkan untuk kekuatan lawan (Elo, klasemen) |
| 2026-10-11 | Odds: rata-rata pasar pre-match, fallback Bet365; closing odds tidak dipakai | Pre-match = tersedia sebelum laga, jadi tidak bocor |
| 2026-10-09 | Fitur hanya pre-match | Fitur in-match (event/skor) tidak tersedia saat prediksi |
| 2026-10-20 | Opponent strength via league-wide Elo (K=20, home adv. 60, 1/3 regress per season) | Simple, transparent, only needs results; standard football Elo settings. Alternatives (Pi-rating, market odds) can be compared later |
