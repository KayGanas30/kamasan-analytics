import docx
from docx.shared import Pt
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
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)

    if not paket_jurnal_ai or not isinstance(paket_jurnal_ai, str):
        doc.add_heading('Gagal Generate Draf Jurnal', 0)
        doc.add_paragraph("Teks dari AI kosong. Silakan coba lagi.")
        file_stream = io.BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

    # --- PEMBERSIH MARKDOWN & LATEX ---
    teks = paket_jurnal_ai
    teks = teks.replace('\\[', '').replace('\\]', '').replace('\\', '')
    teks = teks.replace('**', '').replace('*', '')
    teks = teks.replace('---', '')
    
    for baris in teks.split('\n'):
        baris = baris.strip()
        if not baris:
            continue
            
        # Deteksi Heading
        if baris.startswith('#### '):
            doc.add_heading(baris.replace('#### ', '').strip(), level=3)
        elif baris.startswith('### '):
            doc.add_heading(baris.replace('### ', '').strip(), level=2)
        elif baris.startswith('## '):
            doc.add_heading(baris.replace('## ', '').strip(), level=1)
        elif baris.startswith('# '):
            doc.add_heading(baris.replace('# ', '').strip(), level=1)
        elif baris.lower() == 'title':
            pass # Skip, karena judul sudah ada
        elif baris.startswith('Title'):
            doc.add_heading(baris.replace('Title', '').strip(), level=0)
        elif baris.lower() == 'abstract':
            doc.add_heading('Abstract', level=1)
        elif baris.lower().startswith('keywords'):
            # Gabungkan dengan paragraf sebelumnya jika kosong
            sisa = baris.replace('Keywords:', '').replace('Keywords', '').strip()
            if sisa:
                doc.add_paragraph(f"Keywords: {sisa}")
            else:
                doc.add_paragraph("Keywords: ")
        else:
            # Paragraf biasa
            doc.add_paragraph(baris)
    
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream