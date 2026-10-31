from pyvis.network import Network
import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os

# Daftar kata kunci untuk kategorisasi warna
KATA_POLITIK = {"otonomi", "khusus", "pemerintahan", "dewan", "perwakilan", "partai", "politik", "dana", "kewenangan", "perdasi", "perdasus", "hukum", "undang", "negara", "pusat", "kepolisian", "pembangunan", "anggaran", "penerimaan", "jabatan", "diangkat", "dipilih"}
KATA_ADAT = {"adat", "masyarakat", "asli", "orang", "papua", "noken", "budaya", "suku", "kepala", "honai", "kariwari", "biak", "asmat", "musyawarah", "papuans", "oap"}

def buat_graf_konsep(hasil_pmi, konsep_utama, simpan_ke_file=None):
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
    if html_data:
        html_data = html_data.replace("</head>", "<style>canvas { transform: none !important; }</style></head>")
        components.html(html_data, height=620)