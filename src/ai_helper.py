import streamlit as st
from groq import Groq
from src.database import ambil_pengaturan, simpan_pengaturan
import os
import PyPDF2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def dapatkan_client_groq():
    api_key = ambil_pengaturan("groq_api_key")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def baca_template_jurnal(file_path="assets/template_jurnal.pdf"):
    if not os.path.exists(file_path):
        return ""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            teks = ""
            for page in reader.pages:
                if page.extract_text():
                    teks += page.extract_text() + "\n"
            return teks[:2000] 
    except Exception:
        return ""

def tanya_ai_analisis(pertanyaan, nama_proyek, konsep_utama, hasil_pmi):
    client = dapatkan_client_groq()
    if not client:
        return "⚠️ API Key Groq belum diatur."
    
    konteks_konsep = ", ".join([f"{k['konsep']} (skor {k['skor']:.2f})" for k in konsep_utama[:10]])
    konteks_pmi = "\n".join([f"- {p['kata_a']} berhubungan dengan {p['kata_b']} (muncul {p['frekuensi']}x)" for p in hasil_pmi[:10]])
    
    prompt_sistem = f"""Anda adalah asisten peneliti cerdas bernama Kamasan AI. 
Anda membantu menganalisis dokumen untuk proyek berjudul '{nama_proyek}'.
Berikut adalah hasil ekstraksi teks dari dokumen tersebut:
Konsep Utama: {konteks_konsep}
Hubungan Konsep (PMI):
{konteks_pmi}

Jawablah pertanyaan pengguna HANYA berdasarkan data hasil ekstraksi di atas. 
Jawab dengan bahasa Indonesia yang akademis, jelas, dan ringkas."""

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_sistem},
                {"role": "user", "content": pertanyaan}
            ],
            model="openai/gpt-oss-120b",
            temperature=0.3,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Terjadi kesalahan saat menghubungi AI: {e}"

def buat_ringkasan_ai(nama_proyek, konsep_utama, hasil_pmi):
    client = dapatkan_client_groq()
    if not client:
        return "API Key belum diatur."
        
    konteks = f"Proyek: {nama_proyek}\nKonsep Utama: {', '.join([k['konsep'] for k in konsep_utama[:10]])}\n"
    if hasil_pmi:
        konteks += f"Hubungan Terkuat: {hasil_pmi[0]['kata_a']} - {hasil_pmi[0]['kata_b']} ({hasil_pmi[0]['frekuensi']}x)"
    
    prompt = f"""Buatlah 1 paragraf ringkasan eksekutif (executive summary) yang tajam dan akademis berdasarkan data analisis teks berikut:
{konteks}
Jelaskan apa maksud dan tujuan utama dari dokumen yang dianalisis ini. Jangan gunakan bullet points, buat dalam bentuk paragraf yang mengalir."""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Gagal membuat ringkasan AI: {e}"

def kategorisasi_konsep_ai(konsep_utama):
    client = dapatkan_client_groq()
    if not client:
        return "API Key belum diatur."
        
    daftar_konsep = [k['konsep'] for k in konsep_utama]
    prompt = f"""Kelompokkan konsep-konsep berikut ke dalam kategori yang logis (maksimal 4 kategori, misal: Hukum, Adat, Politik, Ekonomi). 
Konsep: {', '.join(daftar_konsep)}
Berikan jawaban dalam format:
Kategori 1: konsep_a, konsep_b
Kategori 2: konsep_c, konsep_d"""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Gagal: {e}"

def buat_paket_jurnal_lengkap(nama_proyek, konsep_utama, hasil_pmi, target_jurnal, bidang_ilmu, sudut_pandang):
    client = dapatkan_client_groq()
    if not client:
        return "API Key Groq belum diatur."
        
    konteks_konsep = ", ".join([k['konsep'] for k in konsep_utama[:15]])
    konteks_pmi = "\n".join([f"- {p['kata_a']} berhubungan dengan {p['kata_b']} (Frek: {p['frekuensi']})" for p in hasil_pmi[:10]])
    template_teks = baca_template_jurnal()

    prompt = f"""Anda adalah seorang Professor dan Editor Jurnal Internasional Bereputasi (Scopus Q1/Q2).
Saya memiliki hasil analisis teks dari data survei/penelitian berjudul '{nama_proyek}'.
Data yang ditemukan:
Konsep Utama: {konteks_konsep}
Hubungan Konsep (PMI): 
{konteks_pmi}

Target Jurnal: {target_jurnal}
Bidang Ilmu: {bidang_ilmu}
Sudut Pandang Teori: {sudut_pandang}

CONTOH GAYA PENULISAN JURNAL TARGET (ikuti gaya ini):
{template_teks if template_teks else "Gunakan gaya akademik standar IMRaD."}

Tugas Anda:
1. **OPSI IDE & NOVELTY**: Berikan 3 Opsi Ide Penelitian/Judul Artikel beserta penjelasan singkat "Apa Kebaruan (Novelty)-nya?".
2. **STRUKTUR DRAF JURNAL STANDAR (IMRaD)**: Berdasarkan Opsi Ide Terbaik (beri label "REKOMENDASI UTAMA"), buatkan draf jurnal dengan struktur:
   - **Title**: Judul bahasa Inggris yang *publishable*.
   - **Abstract**: 1 paragraf (150-200 kata).
   - **Introduction**: Latar belakang, masalah, dan tujuan.
   - **Methodology**: Jelaskan bahwa analisis menggunakan pendekatan kuantitatif-kualitatif (sebutkan *Text Mining/PMI*).
   - **Results & Discussion**: Narasikan temuan dari tabel PMI dan Konsep Utama.
   - **Conclusion**: Kesimpulan dan saran.
3. **CHECKLIST REVIEWER**: Berikan 3 catatan (Reviewer Notes) apa saja yang harus diperbaiki dosen agar sesuai dengan kriteria `{target_jurnal}`.

Tulis dalam bahasa Indonesia yang sangat formal, akademis, dan siap dipublikasikan. Gunakan format Heading untuk setiap bagian."""
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Gagal membuat paket jurnal: {e}"

def pilih_opsi_dan_buat_draf(nama_proyek, konsep_utama, hasil_pmi, target_jurnal, bidang_ilmu, sudut_pandang, opsi_terpilih):
    client = dapatkan_client_groq()
    if not client:
        return "API Key Groq belum diatur."
        
    konteks_konsep = ", ".join([k['konsep'] for k in konsep_utama[:15]])
    konteks_pmi = "\n".join([f"- {p['kata_a']} berhubungan dengan {p['kata_b']} (Frek: {p['frekuensi']})" for p in hasil_pmi[:10]])

    prompt = f"""Anda adalah Professor Hukum dan Editor Jurnal Internasional (Scopus Q1/Q2).
Data hasil analisis:
Nama Proyek: {nama_proyek}
Konsep Kunci: {konteks_konsep}
Hubungan Konsep: {konteks_pmi}

Target Jurnal: {target_jurnal}
Bidang: {bidang_ilmu}
Sudut Pandang: {sudut_pandang}

IDE TERPILIH:
{opsi_terpilih}

Tugas: Tulis draf artikel jurnal lengkap menggunakan format IMRaD standar (Title, Abstract, Introduction, Methods, Results and Discussion, Conclusion, References). Gunakan bahasa akademik tingkat tinggi, spesifik, dan siap publikasi. Jangan gunakan bullet points, gunakan paragraf yang mengalir."""
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Gagal membuat draf: {e}"

def cari_referensi_riil(konsep_utama):
    import requests
    query = " ".join([k['konsep'] for k in konsep_utama[:3]])
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit=5&fields=title,authors,year,url"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        if 'data' in data and data['data']:
            hasil = "### 📚 Referensi Riil (Ditemukan AI):\n"
            for paper in data['data']:
                authors = ", ".join([a['name'] for a in paper.get('authors', [])])
                hasil += f"- {authors} ({paper.get('year', 'N/A')}). **{paper['title']}**. [Link]({paper.get('url', '#')})\n"
            return hasil
        else:
            return "Tidak ada referensi yang ditemukan untuk konsep ini."
    except Exception as e:
        return f"Gagal mencari referensi: {e}"

def review_jurnal_otomatis(teks_draf, target_jurnal):
    client = dapatkan_client_groq()
    if not client:
        return "API Key belum diatur."
        
    prompt = f"""Anda adalah Reviewer Senior untuk jurnal {target_jurnal} (Scopus Q1/Q2).
Tugas Anda adalah mereview draf artikel berikut dan memberikan catatan kritis agar bisa lolos publikasi.

DRAF ARTIKEL:
{teks_draf[:3000]} 

Berikan review dalam format:
1. **Ringkasan Penilaian**: Apakah artikel ini layak dilanjutkan? (1 paragraf)
2. **Kekuatan Utama**: 2-3 poin kekuatan artikel.
3. **Kelemahan & Saran Revisi**: 3-4 poin kritis yang harus diperbaiki.
4. **Rekomendasi Akhir**: (Accept / Minor Revision / Major Revision / Reject).
"""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Gagal melakukan review: {e}"

def cek_plagiarisme_dasar(teks_baru, id_riwayat_lama):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from src.database import ambil_detail_riwayat
    import json

    detail_lama = ambil_detail_riwayat(id_riwayat_lama)
    if not detail_lama:
        return "Data lama tidak ditemukan."
        
    from src.reporting import buat_narasi_otomatis
    teks_lama = buat_narasi_otomatis(
        detail_lama['nama_proyek'], detail_lama['daftar_file'], 
        detail_lama['konsep_utama'], detail_lama['hasil_pmi']
    )
    
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([teks_baru, teks_lama])
        skor = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        persentase = round(skor * 100, 2)
        
        if persentase > 70:
            status = "🔴 TINGGI (Risiko Plagiarisme)"
        elif persentase > 40:
            status = "🟡 SEDANG (Perlu Parafrase)"
        else:
            status = "🟢 RENDAH (Aman)"
            
        return f"Skor Kemiripan: **{persentase}%**\nStatus: {status}\n\n*(Dibandingkan dengan proyek: {detail_lama['nama_proyek']})*"
    except Exception as e:
        return f"Gagal mengecek: {e}"

def sintesis_pengetahuan_lintas_proyek(semua_riwayat_data):
    client = dapatkan_client_groq()
    if not client:
        return "API Key Groq belum diatur."
        
    memori = ""
    for idx, r in enumerate(semua_riwayat_data):
        konsep = ", ".join([k['konsep'] for k in r['konsep_utama'][:5]])
        memori += f"Proyek {idx+1}: {r['nama_proyek']} | Konsep Utama: {konsep}\n"
        
    prompt = f"""Anda adalah seorang Professor dan Visioner Riset. 
Saya memiliki catatan analisis dari berbagai proyek penelitian di masa lalu. 
Tugas Anda adalah melakukan SINTESIS LINTAS PROYEK untuk menemukan IDE BARU yang inovatif.

MEMORI DATA PENELITIAN SAYA:
{memori}

Tugas Anda:
1. **Analisis Pola**: Apa tema besar yang berulang di semua proyek ini? Apa yang berubah (tren)?
2. **Identifikasi Celah (Gap)**: Apa topik yang belum pernah digabungkan atau dianalisis?
3. **3 Ide Penelitian Inovatif**: Buatkan 3 ide penelitian baru yang menggabungkan konsep dari beberapa proyek di atas. Berikan judul dan alasan mengapa ide ini sangat orisinal dan bisa dipublikasikan di jurnal Q1.

Tulis dalam bahasa akademik yang formal."""
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Gagal melakukan sintesis: {e}"

def kirim_email_laporan(email_penerima, subjek, isi_teks, lampiran_bytes=None, nama_file_lampiran="Laporan.docx"):
    """Mengirim email dengan opsi lampiran menggunakan SMTP Gmail."""
    try:
        email_pengirim = st.secrets["email"]["gmail"]
        password_pengirim = st.secrets["email"]["password"]
        
        msg = MIMEMultipart()
        msg['From'] = email_pengirim
        msg['To'] = email_penerima
        msg['Subject'] = subjek
        
        msg.attach(MIMEText(isi_teks, 'plain'))
        
        if lampiran_bytes:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(lampiran_bytes)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{nama_file_lampiran}"')
            msg.attach(part)
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_pengirim, password_pengirim)
        server.send_message(msg)
        server.quit()
        return True, "Email berhasil dikirim!"
    except Exception as e:
        return False, f"Gagal mengirim email: {e}"