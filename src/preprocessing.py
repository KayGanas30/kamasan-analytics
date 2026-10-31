import re
import string

STOPWORDS_ID = set([
    "yang", "dan", "di", "ke", "dari", "ini", "itu", "dengan", "untuk", 
    "pada", "adalah", "saya", "kita", "kami", "mereka", "dia", "kamu", 
    "akan", "sudah", "telah", "bisa", "ada", "dalam", "oleh", "sebagai",
    "tidak", "juga", "karena", "atau", "tetapi", "namun", "seperti",
    "pasal", "ayat", "huruf", "angka", "dimaksud", "sebagaimana", "republik",
    "indonesia", "pemerintah", "daerah", "provinsi", "kabupaten", "kota",
    "gubernur", "bupati", "wali", "kepala", "menteri", "presiden", "pusat",
    "undang", "uu", "nomor", "tahun", "bagian", "bab", "paragraf", "serta",
    "secara", "lebih", "lanjut", "dapat", "wajib", "harus", "sesuai", 
    "hal", "tersebut", "merupakan", "menjadi", "dilakukan",
    "berdasarkan", "mengenai", "terhadap", "antar", "cukup", "jelas",
    "rangka", "terkait", "berlaku", "peraturan", "ketentuan", "undangan", "perundang", "dimaksudkan", "apabila",
    "juli", "agustus", "september", "oktober", "november", "desember", "januari", "februari", "maret", "april", "mei", "juni",
    "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx",
    "bahwa", "atas", "bagi", "saat", "masa", "merdeka", "bersama",
    "berbunyi", "berikut", "diubah", "tentang", "sebesar", "puluh", 
    "lembaran", "negara", "iden", "pres" 
])

# Variabel global untuk menampung istilah lokal dari database
KAMUS_LOKAL_GLOBAL = set()

def set_kamus_lokal_global(daftar_kata):
    global KAMUS_LOKAL_GLOBAL
    KAMUS_LOKAL_GLOBAL = set(daftar_kata)

def bersihkan_teks(teks):
    if not isinstance(teks, str):
        return ""
    teks = teks.lower()
    teks = teks.replace("-", " ")
    teks = re.sub(r'http\S+|www\S+|https\S+', '', teks, flags=re.MULTILINE)
    teks = re.sub(r'\d+', '', teks)
    teks = re.sub(r'[^a-z\s]', ' ', teks)
    teks = re.sub(r'\s+', ' ', teks).strip()
    return teks

def tokenisasi(teks):
    teks_bersih = bersihkan_teks(teks)
    kata_kata = teks_bersih.split()
    
    kata_penting = []
    for kata in kata_kata:
        if len(kata) < 4:
            continue
        if not any(vokal in kata for vokal in "aiueo"):
            continue
        # Cek stopword ATAU cek kamus lokal
        if kata in STOPWORDS_ID and kata not in KAMUS_LOKAL_GLOBAL:
            continue
        kata_penting.append(kata)
        
    return kata_penting