# PLAN.md - Roadmap Barca ML Projects

Legenda: `[ ]` belum, `[x]` selesai. Kerjakan berurutan; tiap fase punya kriteria selesai (DoD).

## Fase 0 - Fondasi (selesai sebagian)
- [x] Boilerplate repo, `.gitignore`, config, tes smoke, CI, pre-commit
- [x] `CLAUDE.md` dan `PLAN.md`
- [ ] Jalankan `scripts/setup.ps1`, pastikan `pytest` hijau di Windows
- [ ] Salin data lama dari Drive ke `data/raw/`; pindahkan notebook Colab lama ke `notebooks/legacy/`
- [ ] Commit pertama + buat repo GitHub (private dulu)

**DoD:** `pytest` lolos lokal, data lama terbaca lewat `barca_ml.data.load`.

## Fase 1 - Data & skema fitur
- [ ] Validasi data lama: semantik `Poss`, duplikasi, tipe data, nilai hilang (`referee.name` kosong 33/85)
- [x] Rancang **skema tabel kanonik** per laga: tanggal, musim, kandang/tandang, lawan, gol, xG (jika ada), hasil
- [ ] Ingest data baru (urutan prioritas): football-data.co.uk (hasil + odds) -> Understat (xG) -> StatsBomb open data untuk detail event
- [x] Skrip `scripts/fetch_*.py` yang idempoten; simpan ke `data/raw/` dengan tanggal ambil
- [ ] Cek ketentuan penggunaan/lisensi tiap sumber, catat di `docs/data_sources.md`
- [ ] Gabungkan jadi satu dataset 2017/18 sampai musim terbaru

**DoD:** satu file `data/processed/matches.parquet|csv` konsisten, minimal beberapa ratus laga (idealnya semua laga Barca di La Liga beberapa musim), dengan dokumen sumber dan lisensi.

## Fase 2 - EDA & fitur pre-match
- [ ] Notebook `01_eda`: distribusi hasil, kandang vs tandang, tren per musim, kualitas data
- [ ] Fitur di `src/barca_ml/features/build.py`: form 5 laga (poin, gol, kebobolan), kandang/tandang, hari istirahat, rating/Elo lawan, head-to-head, posisi klasemen sebelum laga
- [ ] Tes anti-leakage untuk setiap fitur (nilai laga t tidak boleh bergantung pada laga >= t)
- [ ] Dokumentasikan setiap fitur (arti, sumber, risiko leakage) di `docs/features.md`

**DoD:** tabel fitur siap pakai tanpa leakage, lolos tes.

## Fase 3 - Klasifikasi
- [x] Baseline: kelas mayoritas, "Barca selalu menang", (opsional) probabilitas implisit dari odds
- [ ] Model: logistic regression -> random forest -> XGBoost; tuning dengan **time-series CV**
- [ ] Evaluasi di hold-out musim terbaru: accuracy, **log loss, Brier**, kurva kalibrasi, confusion matrix
- [ ] Simpan model terbaik + metadata (versi data, fitur, tanggal) ke `models/`

**DoD:** model mengalahkan baseline di hold-out dan terkalibrasi wajar. Laporkan akurasi jujur (ekspektasi realistis 3-kelas sekitar 50-55%; biner "Barca menang" bisa lebih tinggi tapi bandingkan dengan baseline mayoritas).

## Fase 4 - Regresi
- [ ] Target: gol Barca (dan/atau xG) per laga; ganti dari possession
- [ ] Model: Poisson regression / gradient boosting; metrik MAE, RMSE, deviance
- [ ] Turunkan distribusi skor -> probabilitas Win/Draw/Lose sebagai pembanding model klasifikasi

**DoD:** MAE lebih baik daripada baseline rata-rata gol, ada perbandingan dengan klasifikasi.

## Fase 5 - Clustering
- [ ] Fitur gaya main per laga/tim (passes, pressing, dribble, posisi rata-rata, durasi penguasaan)
- [ ] K-Means / hierarchical; pilih k dengan silhouette + elbow + interpretasi
- [ ] Beri nama dan karakter tiap klaster; kaitkan dengan hasil laga
- [ ] Gantikan aturan z-score arbitrer dari EDA lama dengan klaster berbasis data

**DoD:** klaster stabil, bisa dijelaskan dalam bahasa sepak bola, dan tersimpan sebagai fitur opsional untuk model.

## Fase 6 - Deploy ke Hugging Face
- [ ] `app/app.py` (Gradio) memuat model dan menampilkan probabilitas + faktor utama
- [ ] Tampilkan disclaimer: hiburan/analitik, bukan taruhan; tampilkan metrik dan keterbatasan model
- [ ] Buat Space (Gradio), upload model ke HF Hub, uji endpoint API
- [ ] GitHub Actions terjadwal: tarik data baru -> retrain -> push model
- [ ] (Opsional) FE kustom: FastAPI di Docker Space + frontend statis

**DoD:** URL Space publik berfungsi, API bisa dipanggil, model bisa diperbarui otomatis.

## Fase 7 - Prediksi pemain (opsional, setelah 1-6)
- [ ] Cari data level pemain (menit, gol, assist, xG/xA)
- [ ] Prediksi gol/assist pemain per laga (Poisson)
- [ ] Integrasikan ke app

## Risiko & mitigasi
| Risiko | Mitigasi |
|---|---|
| Data kecil (85 laga) | Tambah musim dan sumber; fokus probabilitas, bukan klaim akurasi |
| Leakage | Fitur pre-match saja, `shift(1)`, tes otomatis, split waktu |
| Sumber data berubah/dibatasi | Skema kanonik independen sumber; skrip fetch terpisah |
| Klaim akurasi berlebihan | Selalu tampilkan baseline dan metrik probabilistik |
| Isu hukum/lisensi/judi | Cek lisensi data; posisikan sebagai analitik, bukan taruhan |

## Log progres
- 2026-10-09: boilerplate dibuat, `CLAUDE.md` dan `PLAN.md` ditulis, EDA lama dibaca dan temuan dicatat.
- 2026-10-11: pipeline football-data.co.uk (`scripts/fetch_football_data.py`, `barca_ml.data.football_data`) + skema kanonik + tes; lint CI dibereskan. Fetch belum jalan lokal: domain diblokir ISP (perlu VPN/Colab/Actions).
- 2026-10-20: fitur pre-match Elo liga + hari istirahat (`barca_ml.features.build`) dengan tes anti-leakage, `docs/features.md`; baseline evaluasi (frekuensi train, selalu menang, odds pasar) + Brier multikelas di `barca_ml.models.evaluate`. Fitur Fase 2 yang tersisa: head-to-head, posisi klasemen.
