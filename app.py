import streamlit as st
from pathlib import Path
import PyPDF2
import docx
import io
import pandas as pd
import json
import re

from src.preprocessing import tokenisasi, set_kamus_lokal_global
from src.extraction import ekstrak_konsep_utama, hitung_pmi
from src.visualization import buat_graf_konsep, tampilkan_graf_di_streamlit
from src.database import (init_db, simpan_analisis, ambil_semua_riwayat, 
                          ambil_detail_riwayat, ambil_kamus_lokal, 
                          tambah_kamus_lokal, hapus_kamus_lokal, hapus_riwayat,
                          ambil_pengaturan, simpan_pengaturan)
from src.reporting import buat_laporan_word_jurnal, buat_narasi_otomatis
from src.ai_helper import (tanya_ai_analisis, dapatkan_client_groq, 
                           buat_ringkasan_ai, kategorisasi_konsep_ai, 
                           generate_jurnal_package, buat_paket_jurnal_lengkap)

st.set_page_config(page_title="Kamasan Analytics", page_icon="🔨", layout="wide")

# --- TAMBAHAN BARU: PENAMPIL HASIL SEMENTARA ---
if 'hasil_baru' in st.session_state:
    hasil = st.session_state['hasil_baru']
    st.success("✅ Analisis berhasil disimpan ke Riwayat!")
    
    st.subheader(f"🔥 Hasil Tempaan: {hasil['nama']}")
    col_kiri, col_kanan = st.columns([1, 2])
    with col_kiri:
        st.markdown("### 💡 Konsep Utama")
        for k in hasil['konsep']:
            st.write(f"- **{k['konsep']}** (Skor: {k['skor']:.2f})")
    with col_kanan:
        st.markdown("### 🕸️ Peta Jaringan Konsep")
        if hasil['pmi']:
            html_graf = buat_graf_konsep(hasil['pmi'], hasil['konsep'])
            tampilkan_graf_di_streamlit(html_graf)
            
    if st.button("Tutup Hasil Ini & Mulai Baru"):
        del st.session_state['hasil_baru']
        st.rerun()
        
    st.divider()
# -----------------------------------------------

init_db()

# === SIDEBAR ===
with st.sidebar:
    st.image("assets/kamasan.png", width=80)
    
    # --- SISTEM KEAMANAN ---
    st.markdown("---")
    sandi_admin = st.text_input("🔒 Akses Admin (Kosongkan jika tamu)", type="password", help="Masukkan sandi untuk membuka fitur hapus.")
    is_admin = (sandi_admin == "kamasan2026") 
    st.markdown("---")
    
    # --- PENGATURAN AI (API KEY) ---
    st.markdown("### 🤖 Pengaturan AI")
    api_key_tersimpan = ambil_pengaturan("groq_api_key", "")
    api_key_input = st.text_input("Groq API Key:", value=api_key_tersimpan, type="password", help="Dapatkan di console.groq.com")
    if st.button("Simpan API Key"):
        simpan_pengaturan("groq_api_key", api_key_input)
        st.success("API Key disimpan!")
    st.markdown("---")
    
    st.markdown("### Riwayat Tempaan")
    riwayat = ambil_semua_riwayat()
    if not riwayat:
        st.caption("Belum ada riwayat.")
    else:
        for r in riwayat:
            proyek_name = r[1] if r[1] else "Tanpa Nama"
            col_buka, col_hapus = st.columns([0.85, 0.15])
            
            with col_buka:
                if st.button(f"📁 {proyek_name}\n({r[2][:10]})", key=f"btn_{r[0]}", use_container_width=True):
                    st.session_state['view_riwayat'] = r[0]
                    
            with col_hapus:
                if is_admin:
                    if st.button("🗑️", key=f"del_hist_{r[0]}", help="Hapus riwayat"):
                        hapus_riwayat(r[0])
                        if 'view_riwayat' in st.session_state and st.session_state['view_riwayat'] == r[0]:
                            del st.session_state['view_riwayat']
                        st.rerun()
                else:
                    st.write("") 
    
    st.divider()
    st.caption("Kamasan Analytics v0.7 (AI Powered)")

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
            
        narasi = buat_narasi_otomatis(nama_proyek, detail['daftar_file'], detail['konsep_utama'], detail['hasil_pmi'])
        
        # --- ACADEMIC CO-PILOT (GENERATOR JURNAL) ---
        st.divider()
                # --- ACADEMIC CO-PILOT (SUITE) ---
        st.divider()
        st.markdown("### 🤖 Academic Co-Pilot (Suite)")
        
        api_key_cek = ambil_pengaturan("groq_api_key", "")
        if not api_key_cek:
            st.error("⚠️ API Key Groq belum diatur. Silakan atur di sidebar kiri terlebih dahulu.")
        else:
            # Membuat Tab di dalam Halaman Riwayat
            co_tab1, co_tab2, co_tab3, co_tab4 = st.tabs(["📝 Generator Draf", "📚 Referensi Riil", "🧐 Review Jurnal", "🔍 Cek Plagiarisme"])
            
            with co_tab1:
                st.write("Ubah hasil analisis ini menjadi draf jurnal siap publikasi (Format IMRaD).")
                col1, col2, col3 = st.columns(3)
                with col1:
                    target_jurnal = st.text_input("Target Jurnal:", placeholder="misal: Jurnal Hukum Internasional")
                with col2:
                    bidang_ilmu = st.text_input("Bidang Ilmu:", placeholder="misal: Hukum Tata Negara")
                with col3:
                    sudut_pandang = st.text_input("Sudut Pandang/Teori:", placeholder="misal: Teori Otonomi Daerah")
                    
                if st.button("✨ Generate Opsi Ide", type="primary"):
                    if not target_jurnal:
                        st.warning("Harap isi Target Jurnal terlebih dahulu.")
                    else:
                        with st.spinner("Professor AI sedang menganalisis..."):
                            paket_jurnal = buat_paket_jurnal_lengkap(
                                nama_proyek, 
                                detail['konsep_utama'], 
                                detail['hasil_pmi'],
                                target_jurnal,
                                bidang_ilmu,
                                sudut_pandang
                            )
                            st.session_state['paket_jurnal_ai'] = paket_jurnal
                            
                if 'paket_jurnal_ai' in st.session_state and st.session_state['paket_jurnal_ai']:
                    st.markdown(st.session_state['paket_jurnal_ai'])
                    
                    st.markdown("### Pilih Opsi & Buat Draf Final")
                    opsi_terpilih = st.text_area("Salin-tempel Opsi Ide yang Anda pilih di sini:", height=100)
                    
                    if st.button("🚀 Buat Draf Final IMRaD"):
                        with st.spinner("Menulis draf final..."):
                            draf_final = pilih_opsi_dan_buat_draf(
                                nama_proyek, detail['konsep_utama'], detail['hasil_pmi'],
                                target_jurnal, bidang_ilmu, sudut_pandang, opsi_terpilih
                            )
                            st.session_state['draf_final'] = draf_final
                            
                if 'draf_final' in st.session_state and st.session_state['draf_final']:
                    st.markdown("### 📄 Draf Artikel Final")
                    st.info(st.session_state['draf_final'])
                    
                    word_jurnal = buat_laporan_word_jurnal(
                        nama_proyek, detail['tanggal'], detail['daftar_file'], 
                        detail['konsep_utama'], detail['hasil_pmi'], 
                        st.session_state['draf_final']
                    )
                    st.download_button(
                        label="⬇️ Download Draf Jurnal Lengkap (Word)",
                        data=word_jurnal,
                        file_name=f"Draf_Jurnal_{nama_file_aman}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary"
                    )
            
            with co_tab2:
                st.write("Cari referensi riil dari database akademik global (Semantic Scholar).")
                if st.button("🔎 Cari Referensi untuk Konsep Ini"):
                    with st.spinner("Mencari referensi..."):
                        referensi = cari_referensi_riil(detail['konsep_utama'])
                        st.markdown(referensi)
                        
            with co_tab3:
                st.write("Minta AI untuk mereview draf jurnal Anda seolah-olah dia adalah Reviewer Jurnal Scopus.")
                if 'draf_final' in st.session_state and st.session_state['draf_final']:
                    if st.button("🧐 Review Draf Jurnal Ini"):
                        with st.spinner("Reviewer AI sedang membaca draf..."):
                            review = review_jurnal_otomatis(st.session_state['draf_final'], target_jurnal)
                            st.session_state['review_ai'] = review
                            
                    if 'review_ai' in st.session_state:
                        st.markdown(st.session_state['review_ai'])
                else:
                    st.warning("Silakan buat Draf Final di Tab 'Generator Draf' terlebih dahulu.")
                    
            with co_tab4:
                st.write("Cek kemiripan draf Anda dengan riwayat analisis sebelumnya (Cosine Similarity).")
                riwayat_lain = ambil_semua_riwayat()
                opsi_riwayat = {f"{r[1]} ({r[2][:10]})": r[0] for r in riwayat_lain if r[0] != id_riwayat}
                
                if not opsi_riwayat:
                    st.info("Belum ada riwayat lain untuk dibandingkan.")
                else:
                    pilihan_banding = st.selectbox("Pilih Riwayat Pembanding:", list(opsi_riwayat.keys()))
                    if st.button("🔍 Cek Kemiripan"):
                        if 'draf_final' in st.session_state and st.session_state['draf_final']:
                            with st.spinner("Menghitung kemiripan..."):
                                hasil_cek = cek_plagiarisme_dasar(
                                    st.session_state['draf_final'], 
                                    opsi_riwayat[pilihan_banding]
                                )
                                st.info(hasil_cek)
                        else:
                            st.warning("Silakan buat Draf Final di Tab 'Generator Draf' terlebih dahulu.")
                            
        st.divider()
        
        # --- KESIMPULAN & VISUALISASI ---
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
        
        # --- TOMBOL DOWNLOAD STANDAR ---
        col_dl1, col_dl2, col_dl3 = st.columns(3)
        with col_dl1:
            laporan_md = f"# Laporan: {nama_proyek}\nTanggal: {detail['tanggal']}\n\n"
            laporan_md += f"## Kesimpulan Eksekutif\n{narasi}\n\n"
            laporan_md += f"## Konsep Utama\n"
            for k in detail['konsep_utama']: laporan_md += f"- {k['konsep']}\n"
            laporan_md += "\n## Tabel PMI\n" + df_pmi.to_markdown(index=False)
            st.download_button("⬇️ Laporan (Markdown)", laporan_md, f"Laporan_{nama_file_aman}.md", "text/markdown")
            
        with col_dl2:
            word_file = buat_laporan_word_jurnal(
                nama_proyek, detail['tanggal'], detail['daftar_file'], 
                detail['konsep_utama'], detail['hasil_pmi'], 
                "Laporan Standar (Non-AI). Klik tombol Generator Jurnal di atas untuk draf AI."
            )
            st.download_button("⬇️ Laporan Standar (Word)", word_file, f"Laporan_{nama_file_aman}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
        with col_dl3:
            csv_data = df_pmi.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Tabel PMI (CSV)", csv_data, f"Data_PMI_{nama_file_aman}.csv", "text/csv")
            
        st.stop()

# === TAB MENU ===
if is_admin:
    tab1, tab2, tab3 = st.tabs(["📂 Unggah & Analisis", "🔍 Pencarian Kata", "📖 Kamus Istilah"])
else:
    tab1, tab2 = st.tabs(["📂 Unggah & Analisis", "🔍 Pencarian Kata"])
    tab3 = None 

with tab1:
    st.subheader("Unggah Dokumen & Beri Nama")
    nama_proyek_input = st.text_input("🏷️ Nama Proyek / Data (Wajib):", placeholder="Contoh: Analisis UU Otsus 2021")
    uploaded_files = st.file_uploader("Pilih file", type=["txt", "docx", "pdf"], accept_multiple_files=True)

    if uploaded_files:
        if not nama_proyek_input:
            st.warning("⚠️ Harap isi 'Nama Proyek / Data' di atas.")
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
                        
                        simpan_analisis(nama_proyek_input, nama_file, konsep_utama, hasil_pmi)
                        
                        st.session_state['hasil_baru'] = {
                            "nama": nama_proyek_input,
                            "konsep": konsep_utama,
                            "pmi": hasil_pmi
                        }
                        st.rerun()
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

if tab3 is not None:
    with tab3:
        st.subheader("📖 Kamus Istilah Lokal")
        st.write("Tambahkan istilah khusus agar sistem tidak membuangnya saat analisis.")
        
        st.markdown("### 📥 Impor Massal (Copy-Paste)")
        teks_massal = st.text_area("Tempel daftar kata di sini:", height=150)
        
        if st.button("🚀 Impor Semua ke Kamus", type="primary"):
            if teks_massal:
                daftar_kata = re.split(r'[,\n\s]+', teks_massal)
                daftar_kata = [k.strip().lower() for k in daftar_kata if k.strip()]
                
                berhasil, gagal = 0, 0
                for k in daftar_kata:
                    if tambah_kamus_lokal(k): berhasil += 1
                    else: gagal += 1
                
                st.success(f"Selesai! {berhasil} istilah baru ditambahkan. ({gagal} istilah sudah ada).")
                st.rerun()
                
        st.divider()
        
        st.markdown("### ➕ Tambah Satu Istilah")
        col_input, col_btn = st.columns([3, 1])
        with col_input:
            kata_baru = st.text_input("Istilah baru:", placeholder="Contoh: wamena")
        with col_btn:
            st.write("") 
            st.write("")
            if st.button("Tambah", use_container_width=True):
                if kata_baru:
                    if tambah_kamus_lokal(kata_baru):
                        st.success(f"Istilah '{kata_baru}' ditambahkan!")
                        st.rerun()
                    else:
                        st.warning(f"Istilah sudah ada.")
                        
        st.divider()
        
        st.markdown("### Daftar Istilah Saat Ini")
        kamus_sekarang = ambil_kamus_lokal()
        if not kamus_sekarang:
            st.info("Kamus masih kosong.")
        else:
            for k in sorted(kamus_sekarang):
                col_kata, col_hapus = st.columns([4, 1])
                col_kata.write(f"• **{k.capitalize()}**")
                if col_hapus.button("Hapus 🗑️", key=f"del_kamus_{k}"):
                    hapus_kamus_lokal(k)
                    st.rerun()

st.divider()
st.caption("Kamasan Analytics · Offline-first · Data tetap di perangkat Anda")