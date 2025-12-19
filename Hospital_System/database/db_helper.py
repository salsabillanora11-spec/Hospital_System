import sqlite3

DB_FILE = "hospital.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Tabel Pasien
    


    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            nama TEXT,
            nik TEXT,
            dob TEXT,
            gender TEXT,
            kota TEXT,
            riwayat TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            doctor TEXT,
            day TEXT,
            slot TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            diagnosis TEXT,
            notes TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            drug_name TEXT,
            dose TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ehr_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            summary TEXT,
            created_at TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    """)

    conn.commit()
    conn.close()


def get_or_create_patient_id(user_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # cek apakah pasien sudah ada
    cur.execute("SELECT id FROM patients WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    if row:
        pid = row[0]
    else:
        # buat baris baru minimal dengan user_id
        cur.execute("INSERT INTO patients(user_id, nama) VALUES(?, ?)", (user_id, ""))
        conn.commit()
        pid = cur.lastrowid
        
    conn.close()
    return pid

def validate_ehr(user_id: str):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("SELECT id FROM patients WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    if not row:
        print(f"[❌] user_id '{user_id}' tidak ditemukan.")
        conn.close()
        return

    patient_id = row[0]
    print(f"[✅] patient_id = {patient_id}")

    cur.execute("SELECT diagnosis, notes FROM medical_records WHERE patient_id=?", (patient_id,))
    print("[📋] Rekam Medis:", cur.fetchall())

    cur.execute("SELECT drug_name, dose FROM prescriptions WHERE patient_id=?", (patient_id,))
    print("[💊] Resep:", cur.fetchall())

    cur.execute("SELECT summary, created_at FROM ehr_records WHERE patient_id=?", (patient_id,))
    print("[📂] EHR:", cur.fetchall())

    conn.close()

    # Tambahkan pasien GUEST jika belum ada
    cur.execute("SELECT COUNT(*) FROM patients WHERE user_id='GUEST'")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO patients(user_id, name, dob, gender) VALUES(?,?,?,?)",
                    ("GUEST", "Guest User", "2000-01-01", "Tidak Diketahui"))

    conn.commit()
    conn.close()
    
def audit_tables():
    """Audit struktur tabel untuk memastikan kolom created_at ada."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(ehr_records)")
    print("📑 Struktur tabel ehr_records:", cur.fetchall())
    conn.close()

# Contoh penggunaan
if __name__ == "__main__":
    init_db()
    test_user_id = "USER-001"  # Ganti dengan user_id aktif
    validate_ehr(test_user_id)
    audit_tables()


    