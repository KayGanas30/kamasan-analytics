import docx
from docx.shared import Pt, Inches
import io
import pandas as pd

def buat_narasi_otomatis(nama_proyek, daftar_file, konsep_utama, hasil_pmi):
    if not konsep_utama or not hasil_pmi:
        return "Analisis belum menghasilkan cukup data."
    top_konsep = [k['konsep'] for k in konsep_utama[:3]]
    teks_konsep = ", ".join(top_konsep[:-1]) + f", dan {top_konsep[-1]}" if len(top_konsep) > 1 else top_konsep[0]
    top_pasangan = hasil_pmi[:3]
    frasa_kuat = [f"'{p['kata_a']}' dengan '{p['kata_b']}'" for p in top_pasangan]
    teks_frasa = "; ".join(frasa_kuat[:-1]) + f"; dan {frasa_kuat[-1]}" if len(frasa_kuat) > 1 else frasa_kuat[0]
    
    return (
        f"Berdasarkan hasil tempaan analisis terhadap {len(daftar_file)} dokumen dalam proyek {nama_proyek}, "
        f"sistem menemukan bahwa fokus utama pembahasan terletak pada konsep {teks_konsep}. "
        f"Pola kedekatan kata (PMI) menunjukkan hubungan konsisten antara {teks_frasa}. "
        f"Hal ini mengindikasikan bahwa inti dari pembahasan dokumen sangat berkaitan erat dengan relasi antar-konsep tersebut."
    )

def buat_laporan_word_jurnal(nama_proyek, tanggal, daftar_file, konsep_utama, hasil_pmi, paket_jurnal_ai):
    doc = docx.Document()
    
    # Set Font Default (Times New Roman 12)
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)

    # 1. Judul & Metadata (Placeholder)
    doc.add_heading('Draf Artikel Jurnal Internasional (Scopus Q1/Q2)', 0)
    doc.add_paragraph(f"Proyek Analisis: {nama_proyek}")
    doc.add_paragraph(f"Tanggal Generate: {tanggal}")
    doc.add_paragraph(f"Sumber Dokumen: {', '.join(daftar_file)}")
    
    doc.add_heading('1. Rekomendasi Judul & Abstrak (AI Generated)', level=1)
    doc.add_paragraph(paket_jurnal_ai)
    
    doc.add_heading('2. Hasil Analisis Kuantitatif Teks (Kamasan Engine)', level=1)
    
    # Narasi Otomatis
    narasi = buat_narasi_otomatis(nama_proyek, daftar_file, konsep_utama, hasil_pmi)
    doc.add_paragraph(narasi)
    
    # Konsep Utama
    doc.add_heading('Konsep Utama Terdeteksi', level=2)
    for k in konsep_utama:
        doc.add_paragraph(f"{k['konsep']} (Skor: {k['skor']:.2f})", style='List Bullet')
        
    # Tabel PMI
    doc.add_heading('Matriks Hubungan Konsep (PMI)', level=2)
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