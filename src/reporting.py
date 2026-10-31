import docx
import io
import pandas as pd

def buat_narasi_otomatis(nama_proyek, daftar_file, konsep_utama, hasil_pmi):
    """Membuat kesimpulan berbasis logika dari hasil analisis."""
    if not konsep_utama or not hasil_pmi:
        return "Analisis belum menghasilkan cukup data untuk disimpulkan."

    # 1. Ambil 3 konsep teratas
    top_konsep = [k['konsep'] for k in konsep_utama[:3]]
    teks_konsep = ", ".join(top_konsep[:-1]) + f", dan {top_konsep[-1]}" if len(top_konsep) > 1 else top_konsep[0]
    
    # 2. Ambil 3 pasangan kata terkuat (berdasarkan frekuensi & PMI)
    top_pasangan = hasil_pmi[:3]
    frasa_kuat = []
    for p in top_pasangan:
        frasa_kuat.append(f"'{p['kata_a']}' dengan '{p['kata_b']}' (muncul {p['frekuensi']} kali)")
    
    teks_frasa = "; ".join(frasa_kuat[:-1]) + f"; dan {frasa_kuat[-1]}" if len(frasa_kuat) > 1 else frasa_kuat[0]

    # 3. Susun Narasi
    narasi = (
        f"Berdasarkan hasil tempaan analisis terhadap {len(daftar_file)} dokumen dalam proyek **{nama_proyek}**, "
        f"sistem menemukan bahwa fokus utama pembahasan terletak pada konsep {teks_konsep}.\n\n"
        f"Lebih lanjut, jika dilihat dari pola kedekatan kata (PMI), dokumen ini secara konsisten "
        f"menghubungkan {teks_frasa}. Hal ini mengindikasikan bahwa inti dari pembahasan dokumen "
        f"sangat berkaitan erat dengan relasi antar-konsep tersebut.\n\n"
        f"Dengan demikian, maksud dan tujuan dari data yang dianalisis ini berpusat pada bagaimana "
        f"konsep {top_konsep[0]} beroperasi dan berhubungan langsung dengan {top_konsep[1] if len(top_konsep) > 1 else 'konteks lainnya'}."
    )
    return narasi

def buat_laporan_word(nama_proyek, tanggal, daftar_file, konsep_utama, hasil_pmi):
    doc = docx.Document()
    
    # Judul
    doc.add_heading(f'Laporan Analisis: {nama_proyek}', 0)
    doc.add_paragraph(f'Tanggal Analisis: {tanggal}')
    doc.add_paragraph(f'Dokumen yang dianalisis: {", ".join(daftar_file)}')
    
    # === FITUR BARU: NARASI OTOMATIS ===
    doc.add_heading('Kesimpulan Eksekutif (Narasi Otomatis)', level=1)
    narasi = buat_narasi_otomatis(nama_proyek, daftar_file, konsep_utama, hasil_pmi)
    # Bersihkan format markdown bold (**) agar rapi di Word
    narasi_bersih = narasi.replace("**", "")
    doc.add_paragraph(narasi_bersih)
    
    # Konsep Utama
    doc.add_heading('Konsep Utama', level=1)
    for k in konsep_utama:
        doc.add_paragraph(f"{k['konsep']} (Skor: {k['skor']:.2f})", style='List Bullet')
        
    # Tabel PMI
    doc.add_heading('Tabel Hubungan Konsep (PMI)', level=1)
    if hasil_pmi:
        df = pd.DataFrame(hasil_pmi)
        table = doc.add_table(rows=1, cols=len(df.columns))
        table.style = 'Table Grid'
        
        hdr_cells = table.rows[0].cells
        for i, col in enumerate(df.columns):
            hdr_cells[i].text = col.capitalize()
            
        for _, row in df.iterrows():
            row_cells = table.add_row().cells
            for i, val in enumerate(row):
                row_cells[i].text = str(val)
    
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream