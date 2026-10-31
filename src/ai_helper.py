from groq import Groq

def tanya_ai(konteks_dokumen, pertanyaan_user, api_key):
    if not api_key:
        return "API Key belum dimasukkan."

    try:
        client = Groq(api_key=api_key)
        
        # Batasi konteks agar tidak melebihi limit token
        konteks_terbatas = konteks_dokumen[:15000] 

        prompt_sistem = (
            "Anda adalah Kamasan AI, asisten peneliti yang cerdas. "
            "Jawablah pertanyaan pengguna HANYA berdasarkan konteks dokumen yang diberikan. "
            "Jika jawabannya tidak ada di dokumen, katakan 'Maaf, informasi tersebut tidak ditemukan dalam dokumen.' "
            "Gunakan bahasa Indonesia yang formal, ringkas, dan akademis."
        )
        
        prompt_user = f"Konteks Dokumen:\n{konteks_terbatas}\n\nPertanyaan: {pertanyaan_user}"

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt_sistem},
                {"role": "user", "content": prompt_user}
            ],
            model="openai/gpt-oss-120b", 
            temperature=0.3, 
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        return f"Terjadi kesalahan pada AI: {str(e)}"

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