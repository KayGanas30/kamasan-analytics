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