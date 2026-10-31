import matplotlib.pyplot as plt
from io import BytesIO
from collections import Counter
import random
from pyvis.network import Network
import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os

# Daftar kata kunci untuk kategorisasi warna
KATA_POLITIK = {"otonomi", "khusus", "pemerintahan", "dewan", "perwakilan", "partai", "politik", "dana", "kewenangan", "perdasi", "perdasus", "hukum", "undang", "negara", "pusat", "kepolisian", "pembangunan", "anggaran", "penerimaan", "jabatan", "diangkat", "dipilih"}
KATA_ADAT = {"adat", "masyarakat", "asli", "orang", "papua", "noken", "budaya", "suku", "kepala", "honai", "kariwari", "biak", "asmat", "musyawarah", "papuans", "oap"}

def buat_graf_konsep(hasil_pmi, konsep_utama, simpan_ke_file=None):
    """Membuat visualisasi jaringan interaktif dengan PyVis."""
    if not hasil_pmi:
        return None

    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#333333", directed=False)
    
    node_set = set()
    for rel in hasil_pmi:
        node_set.add(rel["kata_a"])
        node_set.add(rel["kata_b"])
        
    skor_dict = {k["konsep"]: k["skor"] for k in konsep_utama}

    for node in node_set:
        ukuran = 15 + (skor_dict.get(node, 1) * 5) 
        
        # Logika Pewarnaan
        if node in KATA_ADAT:
            warna = {"background": "#e63946", "border": "#a4161a"} # Merah (Adat)
        elif node in KATA_POLITIK:
            warna = {"background": "#f4a900", "border": "#b37b00"} # Emas (Politik)
        else:
            warna = {"background": "#457b9d", "border": "#1d3557"} # Biru (Netral/Lainnya)

        net.add_node(
            node, label=node, size=ukuran, title=f"Konsep: {node}",
            color=warna, font={"size": 14, "face": "Arial", "bold": True, "strokeWidth": 0}
        )

    for rel in hasil_pmi:
        ketebalan = max(2, int(rel["pmi"] * 1.5)) 
        net.add_edge(
            rel["kata_a"], rel["kata_b"], value=ketebalan, 
            title=f"PMI: {rel['pmi']} | Frek: {rel['frekuensi']}",
            color={"color": "#cccccc", "highlight": "#333333"}
        )

    net.set_options("""
    var options = {
      "nodes": { "font": { "size": 14, "face": "Arial" } },
      "physics": { "forceAtlas2Based": { "gravitationalConstant": -150, "centralGravity": 0.01, "springLength": 120, "springConstant": 0.08 }, "solver": "forceAtlas2Based", "stabilization": {"iterations": 250} },
      "interaction": { "hover": true, "tooltipDelay": 100 }
    }
    """)

    try:
        tmp_dir = tempfile.gettempdir()
        path_html = os.path.join(tmp_dir, "graf_kamasan.html")
        net.save_graph(path_html)
        
        with open(path_html, 'r', encoding='utf-8') as f:
            html_data = f.read()
        
        # Jika diminta untuk disimpan (untuk fitur download)
        if simpan_ke_file:
            with open(simpan_ke_file, 'w', encoding='utf-8') as f:
                f.write(html_data.replace("</head>", "<style>canvas { transform: none !important; }</style></head>"))
                
        return html_data
    except Exception as e:
        st.error(f"Gagal membuat graf: {e}")
        return None

def tampilkan_graf_di_streamlit(html_data):
    """Menampilkan HTML PyVis di Streamlit."""
    if html_data:
        # Perbaikan: teks terbalik dan ukuran
        html_data = html_data.replace("</head>", "<style>canvas { transform: none !important; }</style></head>")
        components.html(html_data, height=620)

def buat_word_cloud(semua_kata, lebar=10, tinggi=5):
    """Membuat gambar Word Cloud manual menggunakan Matplotlib (tanpa compiler)."""
    if not semua_kata:
        return None
    
    # Hitung frekuensi kata
    freq = Counter(semua_kata)
    top_kata = freq.most_common(50) # Ambil 50 kata teratas
    
    if not top_kata:
        return None

    # Setup figure
    fig, ax = plt.subplots(figsize=(lebar, tinggi))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Warna khas Kamasan (Emas, Merah, Abu, Biru)
    colors = ['#f4a900', '#e63946', '#457b9d', '#333333', '#b37b00', '#a4161a']
    
    # Posisi acak agar tidak tumpang tindih
    posisi_x = [random.uniform(0.1, 0.9) for _ in range(len(top_kata))]
    posisi_y = [random.uniform(0.1, 0.9) for _ in range(len(top_kata))]
    
    max_freq = top_kata[0][1]
    
    for i, (kata, f) in enumerate(top_kata):
        # Ukuran font berdasarkan frekuensi
        ukuran = (f / max_freq) * 60 + 10 
        warna = random.choice(colors)
        
        ax.text(
            posisi_x[i], posisi_y[i], 
            kata, 
            fontsize=ukuran, 
            color=warna, 
            ha='center', 
            va='center',
            alpha=0.8,
            fontweight='bold'
        )
    
    # Simpan ke bytes
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    img_buffer.seek(0)
    return img_buffer.getvalue()