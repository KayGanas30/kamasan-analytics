import streamlit as st
from groq import Groq
from src.database import ambil_pengaturan, simpan_pengaturan

def dapatkan_client_groq():
    """Mengambil client Groq dari API key yang tersimpan."""
    api_key = ambil_pengaturan("groq_api_key")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def tanya_ai_analisis(pertanyaan, nama_proyek, konsep_utama, hasil_pmi):
    """Mengirim pertanyaan ke AI beserta konteks hasil analisis."""
    client = dapatkan_client_groq()
    if not client:
        return "⚠️ API Key Groq belum diatur. Silakan atur di menu Pengaturan AI."
    
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
    """Meminta AI membuat paragraf kesimpulan yang natural."""
    client = dapatkan_client_groq()
    if not client:
        return "API Key belum diatur, tidak bisa membuat ringkasan AI."
        
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
    """Meminta AI mengelompokkan konsep ke dalam kategori."""
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

def generate_jurnal_package(nama_proyek, konsep_utama, hasil_pmi):
    """Menghasilkan Judul, Abstrak, dan Rekomendasi Reviewer untuk Jurnal Hukum."""
    client = dapatkan_client_groq()
    if not client:
        return None
        
    konteks_konsep = ", ".join([k['konsep'] for k in konsep_utama[:10]])
    konteks_pmi = ", ".join([f"{p['kata_a']}-{p['kata_b']}" for p in hasil_pmi[:5]])

    prompt = f"""Anda adalah seorang Professor of Law dan Editor-in-Chief jurnal Scopus Q1.
Berdasarkan hasil analisis teks berikut:
Proyek: {nama_proyek}
Konsep Kunci: {konteks_konsep}
Hubungan Kuat: {konteks_pmi}

Tolong buatkan paket publikasi dalam format berikut (JANGAN gunakan bullet points, gunakan penomoran/heading):
1. **3 JUDUL ARTIKEL (Gaya Hukum Internasional, beri penekanan pada novelty/ kebaruan)**: Buat judul bahasa Inggris yang akademis dan tidak plagiat.
2. **EXECUTIVE SUMMARY (ABSTRACT)**: 1 paragraf padat (150-200 kata) berisi latar belakang, tujuan, metode analisis teks, dan temuan utama.
3. **REKOMENDASI JURNAL (Q1/Q2)**: Sebutkan 3 jurnal hukum internasional yang cocok untuk topik ini beserta alasan singkatnya.
4. **CATATAN REVIEWER (Reviewer's Critique)**: Berikan 3 kritik pedas namun membangun (seolah-olah Anda mereview paper ini) agar temuan ini bisa lolos Q1/Q2.
"""
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.6
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Gagal membuat paket jurnal: {e}"
def buat_paket_jurnal_lengkap(nama_proyek, konsep_utama, hasil_pmi, target_jurnal, bidang_ilmu, sudut_pandang):
    client = dapatkan_client_groq()
    if not client:
        return "API Key Groq belum diatur."
        
    konteks_konsep = ", ".join([k['konsep'] for k in konsep_utama[:15]])
    konteks_pmi = "\n".join([f"- {p['kata_a']} berhubungan dengan {p['kata_b']} (Frek: {p['frekuensi']})" for p in hasil_pmi[:10]])

    prompt = f"""Anda adalah Editor Jurnal Internasional Scopus Q1/Q2. Tugas Anda adalah membantu dosen mengubah data mentah menjadi artikel ilmiah standar IMRaD.

DATA MENTAH:
Nama Proyek: {nama_proyek}
Konsep Kunci: {konteks_konsep}
Hubungan Konsep (PMI): 
{konteks_pmi}

KONTEKS TARGET:
Jurnal Tujuan: {target_jurnal}
Bidang: {bidang_ilmu}
Sudut Pandang: {sudut_pandang}

INSTRUKSI OUTPUT (Gunakan format Markdown yang bersih, TANPA penomoran angka di heading):

# BAGIAN 1: OPSI IDE & NOVELTY (Pilih Salah Satu)
Berikan 2 opsi ide penelitian. Untuk masing-masing, jelaskan "Apa kebaruan (novelty)-nya?" dalam 1-2 kalimat.

# BAGIAN 2: DRAF ARTIKEL ILMIAH (Format IMRaD)
Tulis draf lengkap berdasarkan Opsi Ide Terbaik. Gunakan heading berikut (tanpa angka):

## Title
(Tulis judul bahasa Inggris yang akademis dan spesifik)

## Abstract
(Tulis 1 paragraf padat 150-200 kata. Harus memuat: Latar Belakang, Tujuan, Metode (sebutkan Text Mining/PMI), Temuan Utama, dan Implikasi.)

## Introduction
(Paragraf 1: Latar belakang masalah spesifik. Paragraf 2: Celah pengetahuan/Research Gap. Paragraf 3: Tujuan penelitian dan kontribusi.)

## Methods
(Jelaskan secara metodologis: Pengumpulan data dokumen, proses preprocessing teks, ekstraksi konsep menggunakan TF-IDF, dan analisis hubungan menggunakan PMI. Sebutkan bahwa ini adalah pendekatan analisis teks kuantitatif-kualitatif.)

## Results and Discussion
(Sajikan temuan berdasarkan Konsep Kunci dan PMI. Diskusikan mengapa hubungan antar kata tersebut penting secara akademis. Hubungkan dengan teori {sudut_pandang}. Jangan hanya menyebutkan angka, tapi interpretasikan maknanya.)

## Conclusion
(Ringkas temuan utama dalam 1 paragraf. Jelaskan implikasi praktis untuk {bidang_ilmu}. Berikan saran untuk penelitian selanjutnya.)

## References
(Buat 3-5 contoh referensi fiktif/umum yang relevan dengan topik ini dalam format APA Style untuk memberikan gambaran.)
"""
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-120b",
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Gagal membuat paket jurnal: {e}"