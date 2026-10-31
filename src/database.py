import sqlite3
import json
from datetime import datetime

DB_PATH = "kamasan_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Tabel Riwayat
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS riwayat_analisis (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nama_proyek TEXT,
            tanggal TEXT,
            daftar_file TEXT, 
            konsep_utama TEXT, 
            hasil_pmi TEXT
        )
    ''')
    # Tabel Kamus Lokal
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kamus_lokal (
            id INTEGER PRIMARY KEY AUTOINCREMENT, kata TEXT UNIQUE
        )
    ''')
    # Tabel Pengaturan (Untuk API Key)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pengaturan (
            kunci TEXT PRIMARY KEY,
            nilai TEXT
        )
    ''')
    
    # Masukkan default kata jika kosong
    cursor.execute('SELECT COUNT(*) FROM kamus_lokal')
    if cursor.fetchone()[0] == 0:
        default_kata = ["noken", "patuans", "oap", "lemasa", "anak adat", "musyawarah", "perdasus", "perdasi"]
        for k in default_kata:
            cursor.execute('INSERT INTO kamus_lokal (kata) VALUES (?)', (k,))
            
    conn.commit()
    conn.close()

# --- FUNGSI RIWAYAT ---
def simpan_analisis(nama_proyek, daftar_file, konsep_utama, hasil_pmi):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO riwayat_analisis (nama_proyek, tanggal, daftar_file, konsep_utama, hasil_pmi) 
        VALUES (?, ?, ?, ?, ?)
    ''', (
        nama_proyek,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        json.dumps(daftar_file), 
        json.dumps(konsep_utama), 
        json.dumps(hasil_pmi)
    ))
    conn.commit()
    conn.close()

def ambil_semua_riwayat():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, nama_proyek, tanggal, daftar_file FROM riwayat_analisis ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def ambil_detail_riwayat(id_riwayat):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT nama_proyek, tanggal, daftar_file, konsep_utama, hasil_pmi FROM riwayat_analisis WHERE id = ?', (id_riwayat,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "nama_proyek": row[0],
            "tanggal": row[1], 
            "daftar_file": json.loads(row[2]), 
            "konsep_utama": json.loads(row[3]), 
            "hasil_pmi": json.loads(row[4])
        }
    return None

def hapus_riwayat(id_riwayat):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM riwayat_analisis WHERE id = ?', (id_riwayat,))
    conn.commit()
    conn.close()

# --- FUNGSI KAMUS LOKAL ---
def ambil_kamus_lokal():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT kata FROM kamus_lokal')
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def tambah_kamus_lokal(kata_baru):
    """Menambahkan kata ke kamus. Mengembalikan True jika berhasil, False jika sudah ada."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO kamus_lokal (kata) VALUES (?)', (kata_baru.lower().strip(),))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Jika kata sudah ada, jangan lempar error, tapi kembalikan False
        return False
    finally:
        conn.close()

def hapus_kamus_lokal(kata):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM kamus_lokal WHERE kata = ?', (kata,))
    conn.commit()
    conn.close()

# --- FUNGSI PENGATURAN (API KEY) ---
def ambil_pengaturan(kunci, default=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT nilai FROM pengaturan WHERE kunci = ?', (kunci,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else default

def simpan_pengaturan(kunci, nilai):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pengaturan (kunci, nilai) VALUES (?, ?)
        ON CONFLICT(kunci) DO UPDATE SET nilai=excluded.nilai
    ''', (kunci, nilai))
    conn.commit()
    conn.close()