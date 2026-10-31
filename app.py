import streamlit as st
from pathlib import Path
import PyPDF2
import docx
import io
import pandas as pd
import json

from src.preprocessing import tokenisasi, set_kamus_lokal_global
from src.extraction import ekstrak_konsep_utama, hitung_pmi
from src.visualization import buat_graf_konsep, tampilkan_graf_di_streamlit
from src.database import (init_db, simpan_analisis, ambil_semua_riwayat, 
                          ambil_detail_riwayat, ambil_kamus_lokal, 
                          tambah_kamus_lokal, hapus_kamus_lokal)
from src.reporting import buat_laporan_word

st.set_page_config(page_title="Kamasan Analytics", page_icon="🔨", layout="wide")

init_db()

# === SIDEBAR ===
with st.sidebar:
    st.image("assets/kamasan.png", width=80)
    st.markdown("### Riwayat Tempaan")
    riwayat = ambil_semua_riwayat()
    if not riwayat:
        st.caption("Belum ada riwayat.")
    else:
        for r in riwayat:
            # r = (id, nama_proyek, tanggal, daftar_file)
            proyek_name = r[1] if r[1] else "Tanpa Nama"
            file_list = ", ".join(json.loads(r[3]))[:15] + "..."
            if st.button(f"📁 {proyek_name}\n({r[2]})", key=f"btn_{r[0]}", use_container_width=True):
                st.session_state['view_riwayat'] = r[0]
    
    st.divider()
    
    # KAMUS ISTILAH LOKAL
    st.markdown("### 📖 Kamus Istilah Lokal")
    kamus_sekarang = ambil_kamus_lokal()
    for k in kamus_sekarang:
        col1, col2 = st.columns([3, 1])
        col1.write(f"• {k}")
        if col2.button("❌", key=f"del_{k}"):
            hapus_kamus_lokal(k)
            st.rerun()
            
    kata_baru = st.text_input("Tambah istilah:", placeholder="misal: wamena")
    if st.button("Tambah"):
        if kata_baru and tambah_kamus_lokal(kata_baru):
            st.rerun()

    st.divider()
    st.caption("Kamasan Analytics v0.3")

# === HEADER ===
col_logo, col_title = st.columns([1, 8])
with col_logo:
    if Path("assets/kamasan.png").exists():
        st.image("assets/kamasan.png", width=100)
with col_title:
    st.title("Kamasan Analytics")
    st.caption("Tajam Menganalisis, Bijak Menyimpulkan")

st.divider()

def baca_file(uploaded_file):
    teks = ""
    if uploaded_file.name.endswith('.txt'):
        teks = uploaded_file.read().decode("utf-8")
    elif uploaded_file.name.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        for page in pdf_reader.pages:
            if page.extract_text(): teks += page.extract_text() + "\n"
    elif uploaded_file.name.endswith('.docx'):
        doc = docx.Document(io.BytesIO(uploaded_file.read()))
        for para in doc.paragraphs: teks += para.text + "\n"
    return teks

# === HALAMAN RIWAYAT ===
if 'view_riwayat' in st.session_state:
    id_riwayat = st.session_state['view_riwayat']
    detail = ambil_detail_riwayat(id_riwayat)
    
    if detail:
        nama_proyek = detail['nama_proyek'] or "Analisis_Tanpa_Nama"
        nama_file_aman = "".join(c if c.isalnum() else "_" for c in nama_proyek)
        
        st.info(f"Menampilkan hasil analisis: **{nama_proyek}** (Tanggal: {detail['tanggal']})")
        if st.button("⬅️ Kembali"):
            del st.session_state['view_riwayat']
            st.rerun()
            
        # Import fungsi narasi
        from src.reporting import buat_narasi_otomatis
        narasi = buat_narasi_otomatis(nama_proyek, detail['daftar_file'], detail['konsep_utama'], detail['hasil_pmi'])

        # Tampilkan Narasi di Layar
        st.markdown("### 📝 Kesimpulan Eksekutif")
        st.info(narasi)
        
        st.divider()
            
        col_kiri, col_kanan = st.columns([1, 2])
        with col_kiri:
            st.markdown("### 💡 Konsep Utama")
            for k in detail['konsep_utama']:
                st.write(f"- **{k['konsep']}** (Skor: {k['skor']:.2f})")
        with col_kanan:
            st.markdown("### 🕸️ Peta Jaringan (Klik & Geser)")
            html_graf = buat_graf_konsep(detail['hasil_pmi'], detail['konsep_utama'])
            tampilkan_graf_di_streamlit(html_graf)
            
            if html_graf:
                html_download = html_graf.replace("</head>", "<style>canvas { transform: none !important; }</style></head>")
                st.download_button("⬇️ Download Peta Jaringan (HTML)", html_download, f"Peta_Konsep_{nama_file_aman}.html", "text/html")
        
        st.divider()
        st.markdown("### 📊 Tabel PMI")
        df_pmi = pd.DataFrame(detail['hasil_pmi'])
        st.dataframe(df_pmi, use_container_width=True)
        
        col_dl1, col_dl2, col_dl3 = st.columns(3)
        with col_dl1:
            # Tambahkan narasi ke Markdown
            laporan_md = f"# Laporan: {nama_proyek}\nTanggal: {detail['tanggal']}\n\n"
            laporan_md += f"## Kesimpulan Eksekutif\n{narasi}\n\n"
            laporan_md += f"## Konsep Utama\n"
            for k in detail['konsep_utama']: laporan_md += f"- {k['konsep']}\n"
            laporan_md += "\n## Tabel PMI\n" + df_pmi.to_markdown(index=False)
            
            st.download_button("⬇️ Laporan (Markdown)", laporan_md, f"Laporan_{nama_file_aman}.md", "text/markdown")
            
        with col_dl2:
            word_file = buat_laporan_word(nama_proyek, detail['tanggal'], detail['daftar_file'], detail['konsep_utama'], detail['hasil_pmi'])
            st.download_button("⬇️ Laporan (Word)", word_file, f"Laporan_{nama_file_aman}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
        with col_dl3:
            csv_data = df_pmi.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Tabel PMI (CSV)", csv_data, f"Data_PMI_{nama_file_aman}.csv", "text/csv")
            
        st.stop()

# === TAB MENU ===
tab1, tab2 = st.tabs(["📂 Unggah & Analisis", "🔍 Pencarian Kata"])

with tab1:
    st.subheader("Unggah Dokumen & Beri Nama")
    
    # INPUT NAMA PROYEK BARU
    nama_proyek_input = st.text_input("🏷️ Nama Proyek / Data (Wajib):", placeholder="Contoh: Analisis UU Otsus 2021")
    
    uploaded_files = st.file_uploader("Pilih file", type=["txt", "docx", "pdf"], accept_multiple_files=True)

    if uploaded_files:
        if not nama_proyek_input:
            st.warning("⚠️ Harap isi 'Nama Proyek / Data' di atas agar file laporan rapi.")
        else:
            st.success(f"{len(uploaded_files)} file siap ditempa.")
            if st.button("🚀 Mulai Tempa Analisis", type="primary"):
                with st.spinner("Menempa data..."):
                    semua_kata, daftar_kata_per_dokumen, nama_file = [], [], []
                    
                    kamus_terbaru = ambil_kamus_lokal()
                    set_kamus_lokal_global(kamus_terbaru) 
                    
                    for file in uploaded_files:
                        nama_file.append(file.name)
                        kata_dokumen = tokenisasi(baca_file(file))
                        daftar_kata_per_dokumen.append(kata_dokumen)
                        semua_kata.extend(kata_dokumen)
                    
                    if len(semua_kata) == 0:
                        st.warning("Teks tidak cukup.")
                    else:
                        konsep_utama = ekstrak_konsep_utama(daftar_kata_per_dokumen, top_n=15)
                        hasil_pmi = hitung_pmi(semua_kata, min_cooccurrence=5)
                        
                        # Simpan beserta nama proyeknya
                        simpan_analisis(nama_proyek_input, nama_file, konsep_utama, hasil_pmi)
                        
                        st.divider()
                        st.subheader(f"🔥 Hasil Tempaan: {nama_proyek_input}")
                        
                        col_kiri, col_kanan = st.columns([1, 2])
                        with col_kiri:
                            st.markdown("### 💡 Konsep Utama")
                            for k in konsep_utama:
                                st.write(f"- **{k['konsep']}** (Skor: {k['skor']:.2f})")
                        with col_kanan:
                            st.markdown("### 🕸️ Peta Jaringan Konsep")
                            if hasil_pmi:
                                html_graf = buat_graf_konsep(hasil_pmi, konsep_utama)
                                tampilkan_graf_di_streamlit(html_graf)
                        if hasil_pmi:
                            with st.expander("Lihat Detail Hubungan (PMI)"):
                                st.dataframe(pd.DataFrame(hasil_pmi), use_container_width=True)
    else:
        st.info("Belum ada file.")

with tab2:
    st.subheader("🔍 Pencarian Konteks Kata")
    uploaded_search = st.file_uploader("Unggah file untuk dicari", type=["txt", "docx", "pdf"])
    kata_dicari = st.text_input("Masukkan kata")
    
    if uploaded_search and kata_dicari:
        if st.button("Cari Kata"):
            teks_mentah = baca_file(uploaded_search)
            kalimat_list = teks_mentah.split('.')
            hasil_pencarian = [ " ".join(kal.split()) for kal in kalimat_list if kata_dicari.lower() in kal.lower() ]
            
            if hasil_pencarian:
                st.success(f"Ditemukan {len(hasil_pencarian)} kalimat.")
                for i, kalimat in enumerate(hasil_pencarian[:20]):
                    st.info(f"**{i+1}.** ...{kalimat}...")
            else:
                st.warning(f"Kata '{kata_dicari}' tidak ditemukan.")

st.divider()
st.caption("Kamasan Analytics · Offline-first · Data tetap di perangkat Anda")