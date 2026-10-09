# CLAUDE.md - Barca ML Projects

Konteks project untuk Claude (Cowork dan Claude Code). Baca ini sebelum mengubah apa pun, lalu baca `PLAN.md`.

## Tujuan
Membangun model ML untuk memprediksi pertandingan FC Barcelona dengan tiga objektif:
1. **Klasifikasi**: probabilitas hasil Win / Draw / Lose (sudut pandang Barcelona).
2. **Regresi**: gol atau xG Barcelona per laga (bukan lagi possession; possession kurang bernilai bisnis).
3. **Clustering**: kelompokkan laga/tim berdasarkan gaya main.

Target akhir: model + demo web (Gradio) di Hugging Face Spaces, dengan API otomatis. Ini project pribadi/portfolio yang berawal dari tugas kuliah KASDAD 25/26 (kelompok "Dadsak"). Pemilik: Sayyid (sayyidthariq02@gmail.com). Bahasa komunikasi: Indonesia santai; kode, nama variabel, dan docstring dalam bahasa Inggris.

Bukan alat taruhan. Jangan membingkai output sebagai saran judi.

## Data
- Sumber lama: StatsBomb-style open data La Liga, **hanya 85 laga Barcelona (2018-2021)**, 328.675 event. Terlalu kecil untuk klaim akurasi tinggi; butuh data musim baru.
- File (Google Drive `LFM_Kasdad/klasifikasi/`, juga ada di `regresi/`): `train.csv`, `test.csv`, `events_train.csv`, `startingxi.csv`, `position_guide.csv`. Taruh salinan lokal di `data/raw/` (tidak di-commit).
- Kolom match: `match_id, match_date, kick_off, home_score, away_score, match_week, home_team.home_team_name, away_team.away_team_name, stadium.name, referee.name, home/away_team.managers_*, Poss, Result`.
- Kandidat sumber data baru: football-data.co.uk (hasil + odds, CSV), football-data.org (API gratis), Understat (xG), API-Football/FBref (cek ketentuan dan ketersediaan). Skema fitur kita sendiri harus independen dari sumber (lihat PLAN fase 1).

## Aturan keras (jangan dilanggar)
1. **Tidak ada leakage.** Fitur untuk laga t hanya dari laga < t. Jangan pakai `home_score`/`away_score`/`Result`, agregat event, atau `Poss` dari laga yang sedang diprediksi sebagai fitur. Semua rolling pakai `shift(1)`.
2. **Split berbasis waktu**, bukan random. Fit scaler/encoder hanya di train.
3. **Selalu bandingkan dengan baseline** (kelas mayoritas, "Barca selalu menang", dan jika ada odds pasar). Laporkan log loss dan Brier/kalibrasi selain akurasi.
4. **Jangan menjanjikan akurasi 85%+** untuk 3 kelas. Realistis sekitar 50-55%; klaim hanya berdasarkan hasil di hold-out musim terbaru.
5. Logika reusable ada di `src/barca_ml/`, notebook hanya eksplorasi. Output notebook di-strip (nbstripout). Tidak ada path Google Drive/Colab (`/content/drive/...`) di kode.
6. Jangan commit data mentah, model besar, atau secret. Tambah tes untuk setiap fungsi fitur baru (terutama tes anti-leakage).
7. Seed tetap (`random_state` dari `configs/config.yaml`).

## Temuan dari notebook EDA lama (`dadsak_EDA.ipynb`) yang perlu diwaspadai
- Fitur agregat event (passes, goals, dll.) dihitung dari laga yang sama, jadi **bocor** kalau dipakai memprediksi hasil sebelum laga. Cocok untuk analisis, bukan untuk prediksi.
- `Poss` dibalik (`100 - Poss` saat Barca kandang). Verifikasi dulu apakah `Poss` itu possession tim tandang atau kandang sebelum dipakai.
- Pengelompokan per tahun kalender memotong musim; pakai **musim** (mis. 2018/19). Data 2020-2021 jarang.
- `LabelEncoder` dipakai ulang untuk banyak kolom, dan kode outcome di-hardcode (`== 0`, `== 1`) tanpa konsisten (sukses dribble didefinisikan berbeda di dua tempat). Ganti dengan pemetaan eksplisit.
- Klasifikasi playstyle dan pola defensif memakai ambang z-score yang arbitrer; "formasi 4-2-4 menang 100%" berasal dari 1-2 laga, tidak signifikan secara statistik.
- Dua notebook tugas (`LFM_Klasifikasi`, `LFM_Regresi`) hanya stub load data; yang regresi error (mount Drive gagal, path tidak ketemu).
- Temuan yang masih berguna: Messi memimpin pemecah kebuntuan (39) dan kreator terbanyak; kecenderungan possession Barca naik dari ~63% (2018) ke ~71% (2020).

## Perintah umum (PowerShell, dari root repo)
```
./scripts/setup.ps1        # venv + dependensi + pre-commit + nbstripout
pytest                     # tes
ruff check . ; ruff format .
python -m barca_ml.models.train
python app/app.py          # demo Gradio lokal
```

## Konvensi
- Python 3.10+, ruff (line 100), pytest. Nama file notebook `NN_topik.ipynb`.
- Commit kecil dan deskriptif (conventional commits: `feat:`, `fix:`, `docs:`). Catat keputusan penting di `docs/decisions.md`.
- Setiap sesi kerja: baca `PLAN.md`, kerjakan satu fase/tugas, centang checklist, update `docs/decisions.md` bila ada keputusan baru.

## Cara bekerja dengan Sayyid
Sayyid ingin paham, bukan sekadar hasil jalan. Jelaskan alasan tiap keputusan modeling secara singkat, tandai konsep yang perlu dikuasai (leakage, overfitting, kalibrasi), dan jujur soal keterbatasan data.
