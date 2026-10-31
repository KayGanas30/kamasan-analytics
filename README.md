# Kamasan Analytics 🔨
**"Tajam Menganalisis, Bijak Menyimpulkan"**

Kamasan Analytics adalah alat analisis teks kualitatif offline-first yang dirancang untuk membantu akademisi, peneliti, dan praktisi dalam memetakan konsep dan hubungan antar-kata dari dokumen teks (PDF, Word, TXT). Terinspirasi dari keahlian "Kamasan" (pandai besi) dari Biak, aplikasi ini menempa data mentah menjadi wawasan yang tajam.

## Fitur Utama
1. **Ekstraksi Konsep Otomatis:** Menggunakan TF-IDF untuk menemukan konsep paling penting dalam dokumen.
2. **Peta Jaringan Konsep (PMI):** Visualisasi interaktif yang menunjukkan kata mana yang sering muncul bersamaan (berdasarkan Pointwise Mutual Information).
3. **Kategorisasi Warna:** Node berwarna **Emas** untuk konteks Politik/Hukum, dan **Merah** untuk konteks Adat/Budaya.
4. **Kamus Istilah Lokal Dinamis:** Pengguna dapat menambahkan istilah khusus (misal: nama marga, tempat) agar tidak dibuang oleh sistem.
5. **Pencarian Konteks:** Mencari kata spesifik dan melihat kalimat aslinya.
6. **Ekspor Laporan:** Menyimpan hasil analisis ke format Markdown, HTML (untuk graf), dan Word (.docx).
7. **Riwayat Lokal:** Menyimpan riwayat analisis di database SQLite (offline, data aman di laptop).

## Cara Menjalankan Aplikasi
1. Pastikan Python sudah terinstall.
2. Buka folder `kamasan-analytics`.
3. Klik 2x file **`run_kamasan.bat`**.
4. Aplikasi akan otomatis terbuka di browser (http://localhost:8501).

## Struktur Folder
- `app.py`: Antarmuka utama Streamlit.
- `src/`: Berisi mesin analisis (`preprocessing.py`, `extraction.py`, `visualization.py`, `database.py`, `reporting.py`).
- `assets/`: Berisi logo Kamasan.
- `kamasan_data.db`: Database riwayat (dibuat otomatis).

---
*Dibangun untuk mendukung riset politik dan adat istiadat di Tanah Papua.*"# kamasan-analytics" 
