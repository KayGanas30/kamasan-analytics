from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
import math

def ekstrak_konsep_utama(daftar_kata, top_n=15):
    dokumen_gabung = [" ".join(kata) for kata in daftar_kata]
    if not dokumen_gabung:
        return []

    vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2)) 
    try:
        tfidf_matrix = vectorizer.fit_transform(dokumen_gabung)
        feature_names = vectorizer.get_feature_names_out()
        
        skor_total = tfidf_matrix.sum(axis=0).A1
        indeks_terurut = skor_total.argsort()[::-1]
        
        konsep_utama = [
            {"konsep": feature_names[i], "skor": float(skor_total[i])} 
            for i in indeks_terurut[:top_n]
        ]
        return konsep_utama
    except ValueError:
        return []

def hitung_pmi(daftar_kata, jendela=5, min_cooccurrence=5): # Dinaikkan jadi 5
    freq_kata = Counter(daftar_kata)
    total_kata = sum(freq_kata.values())
    
    if total_kata == 0:
        return []

    freq_pasangan = Counter()
    for i in range(len(daftar_kata)):
        for j in range(i + 1, min(i + jendela, len(daftar_kata))):
            kata_a = daftar_kata[i]
            kata_b = daftar_kata[j]
            if kata_a != kata_b:
                pasangan = tuple(sorted([kata_a, kata_b]))
                freq_pasangan[pasangan] += 1

    hasil_pmi = []
    for (kata_a, kata_b), freq_a_b in freq_pasangan.items():
        if freq_a_b < min_cooccurrence:
            continue
            
        freq_a = freq_kata[kata_a]
        freq_b = freq_kata[kata_b]
        
        p_a_b = freq_a_b / total_kata
        p_a = freq_a / total_kata
        p_b = freq_b / total_kata
        
        pmi = math.log2(p_a_b / (p_a * p_b))
        
        # Threshold PMI diturunkan, tapi min_cooccurrence dinaikkan
        if pmi > 0.1: 
            hasil_pmi.append({
                "kata_a": kata_a,
                "kata_b": kata_b,
                "frekuensi": freq_a_b,
                "pmi": round(pmi, 2)
            })
            
    hasil_pmi.sort(key=lambda x: (x["frekuensi"], x["pmi"]), reverse=True) # Urutkan berdasarkan Frekuensi dulu
    return hasil_pmi[:30]