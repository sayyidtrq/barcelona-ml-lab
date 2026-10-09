# Barcelona ML Lab

Prediksi hasil pertandingan, gol/xG, dan gaya main FC Barcelona dengan tiga tugas ML:
**klasifikasi**, **regresi**, dan **clustering**. Target akhir: model dan demo web di Hugging Face Spaces.

> Untuk hiburan dan analitik. Bukan alat taruhan.

## Quick start (Windows PowerShell)

```powershell
./scripts/setup.ps1
pytest
jupyter lab
```

## Struktur

```
configs/      konfigurasi (split waktu, target, path)
data/         raw -> interim -> processed (tidak di-commit)
notebooks/    eksplorasi (01 EDA, 02 klasifikasi, 03 clustering, 04 regresi)
src/barca_ml/ kode reusable: data, features, models
app/          Gradio app untuk Hugging Face Spaces
tests/        pytest (termasuk tes anti-leakage)
models/       artefak model (tidak di-commit)
docs/         decision log
```

Lihat `PLAN.md` untuk roadmap dan `CLAUDE.md` untuk konteks bagi Claude.
