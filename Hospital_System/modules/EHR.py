import sys, sqlite3
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QListWidget, QMessageBox, QFrame, QGraphicsOpacityEffect, QHBoxLayout
)
from PySide6.QtGui import QFont, QPixmap, QIcon
from datetime import datetime
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve

DB_FILE = "hospital.db"

# ---------------------
# Database Initialization
# ---------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Tabel pasien
    cur.execute("""CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        name TEXT,
        dob TEXT,
        gender TEXT
    )""")

    # Tabel rekam medis
    cur.execute("""CREATE TABLE IF NOT EXISTS medical_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        diagnosis TEXT,
        notes TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )""")

    # Tabel resep
    cur.execute("""CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        drug_name TEXT,
        dose TEXT,
        FOREIGN KEY(patient_id) REFERENCES patients(id)
    )""")

    # Tambahkan pasien contoh
    cur.execute("SELECT COUNT(*) FROM patients")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO patients(user_id, name, dob, gender) VALUES(?,?,?,?)",
                    ("USER", "Salsabilla", "2000-01-01", "Perempuan"))

    conn.commit()
    conn.close()

# ---------------------
# Struk EHR Window
# ---------------------
class StrukEHR(QWidget):
    def __init__(self, data, on_back=None):
        super().__init__()
        self.setWindowTitle("Struk Konsultasi Medis EHR")
        self.setFixedSize(400, 600)

        self.data = data
        self._on_finished = on_back

       # Desain 
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(
            QPixmap("assets/biruu.png")
            .scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        )
        self.bg_label.setGeometry(0, 0, 400, 600)
        self.bg_label.lower()

        # Build UI
        self._build_layout()
        self.bg_label.lower()

        # Fade effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)

    def _build_layout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(12)

        info = [
            ("Nama Pasien", self.data.get("patient", "-")),
            ("Dokter", self.data.get("doctor", "-")),
            ("Hari Konsul", self.data.get("day", "-")),
            ("Tanggal Konsul", self.data.get("date", "-")),
            ("Jam Konsul", self.data.get("time", "-"))
        ]
        for label, value in info:
            line = QLabel(f"{label} : {value}")
            line.setFont(QFont("Arial", 11))
            line.setStyleSheet("background: transparent; color: #1F2937;")
            layout.addWidget(line)

        riwayat_text = "Riwayat Penyakit:\n" + ("\n".join([f"- {item}" for item in self.data.get("riwayat", [])]) or "-")
        riwayat_label = QLabel(riwayat_text)
        riwayat_label.setFont(QFont("Arial", 11))
        riwayat_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        riwayat_label.setWordWrap(True)
        layout.addWidget(riwayat_label)

        resep_text = "Resep Obat:\n" + ("\n".join([f"- {item}" for item in self.data.get("resep", [])]) or "-")
        resep_label = QLabel(resep_text)
        resep_label.setFont(QFont("Arial", 11))
        resep_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        resep_label.setWordWrap(True)
        layout.addWidget(resep_label)

        dicetak = QLabel(f"Dicetak pada   : {datetime.now().strftime('%d-%m-%Y %H:%M')}")
        dicetak.setFont(QFont("Arial", 10))
        dicetak.setStyleSheet("color: #1F2937;")
        layout.addWidget(dicetak)
        layout.addWidget(self._divider())

        btn_close = QPushButton("Tutup")
        btn_close.setIcon(QIcon("assets/icon_close_blue.png")) 
        btn_back = QPushButton("Kembali ke Menu")
        btn_back.setIcon(QIcon("assets/icon_back_blue.png"))

        for btn in (btn_close, btn_back):
            btn.setFont(QFont("Arial", 11))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1976D2;
                    color: white;
                    border-radius: 6px;
                    padding: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1565C0;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
            """)
        btn_close.clicked.connect(self.close)
        btn_back.clicked.connect(self._start_fade_out)
        layout.addWidget(btn_back)
        layout.addWidget(btn_close)
        layout.addWidget(btn_back)
        self.setLayout(layout)

    def _divider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background: transparent;")
        return line
    
    def apply_fade_in(self):
        self.animation_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation_in.setDuration(1000)
        self.animation_in.setStartValue(0.0)
        self.animation_in.setEndValue(1.0)
        self.animation_in.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation_in.start()

    def _start_fade_out(self):
        self.animation_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation_out.setDuration(900)
        self.animation_out.setStartValue(1.0)
        self.animation_out.setEndValue(0.0)
        self.animation_out.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation_out.finished.connect(self._finish)
        self.animation_out.start()

    def _finish(self):
        if callable(self._on_finished):
            self._on_finished()
        self.close()

# ---------------------
# CDSS Window
# ---------------------
class CDSSWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("CDSS + EHR Integration")
        self.setFixedSize(400, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        header = QLabel("Clinical Decision Support System (CDSS)")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size:18px; font-weight:bold; color:#1976D2;")
        layout.addWidget(header)

        self.symptom_list = QListWidget()
        self.symptom_list.addItems(["Demam", "Batuk", "Sesak Napas", "Nyeri Dada"])
        layout.addWidget(QLabel("Pilih Gejala Pasien:"))
        layout.addWidget(self.symptom_list)

        process_btn = QPushButton("Proses Gejala → Cetak Struk EHR")
        process_btn.clicked.connect(self.process_symptoms)
        layout.addWidget(process_btn)

        self.result_label = QLabel("Diagnosis: -")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def process_symptoms(self):
        selected = [item.text() for item in self.symptom_list.selectedItems()]
        if not selected:
            QMessageBox.warning(self, "Info", "Silakan pilih gejala terlebih dahulu!")
            return

        # Logika sederhana diagnosis
        if "Sesak Napas" in selected and "Demam" in selected:
            diagnosis = "Pneumonia"
            drug = "Antibiotik 500mg, 2x sehari"
        elif "Batuk" in selected:
            diagnosis = "Bronkitis"
            drug = "Mukolitik sesuai label"
        else:
            diagnosis = "ISPA"
            drug = "Parasetamol 500mg, 3x sehari"

        self.result_label.setText(f"Diagnosis: {diagnosis}\nObat: {drug}")

        # Simpan ke DB
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM patients WHERE user_id=?", (self.user_id,))
        row = cur.fetchone()
        if not row:
            QMessageBox.warning(self, "Error", f"Pasien dengan user_id '{self.user_id}' tidak ditemukan.")
            conn.close()
            return
        patient_id, patient_name = row

        cur.execute("INSERT INTO medical_records(patient_id, diagnosis, notes) VALUES(?,?,?)",
                (patient_id, diagnosis, f"Gejala: {', '.join(selected)}"))
        cur.execute("INSERT INTO prescriptions(patient_id, drug_name, dose) VALUES(?,?,?)",
                    (patient_id, drug.split(" - ")[0], drug.split(" - ")[1] if " - " in drug else ""))
        conn.commit()
        conn.close()

        # 🔹 Data untuk StrukEHR
        data = {
            "patient": patient_name,
            "doctor": "Dr. Laura Alexandra, MRCP(ENT), MBBS",   # bisa diganti sesuai modul dokter
            "day": "Jumat",
            "date": "19 Desember 2025",
            "time": "14:30 WIB",
            "riwayat": selected,
            "resep": [f"{drug}"]
        }

        # Buka StrukEHR
        self.struk = StrukEHR(data, on_back=self.show)
        self.struk.show()
        self.hide()

# Style UI
        self.setStyleSheet("""
            QWidget {
                background-color: #E3F2FD;
                font-family: 'Segoe UI';
            }
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)

        header = QLabel("Struk Pendaftaran")
        header.setFixedHeight(50)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            background-color: #1565C0;
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)

        card_info = QFrame()
        card_info.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 16px;
            }
            QLabel {
                font-size: 14px;
                color: #263238;
            }
        """)

        info_layout = QVBoxLayout(card_info)

        def row(label, value):
            r = QHBoxLayout()
            r.addWidget(QLabel(label))
            val = QLabel(value)
            val.setStyleSheet("font-weight: bold;")
            r.addStretch()
            r.addWidget(val)
            return r

        info_layout.addLayout(row("Nomor Antrian", {"queue_number"}))
        info_layout.addLayout(row("Nama Pasien", {"patient_name"}))
        info_layout.addLayout(row("Dokter", {"doctor_name"}))
        info_layout.addLayout(row("Tanggal", {"date"}))
        info_layout.addLayout(row("Jam", {"time"}))

        card_qr = QFrame()
        card_qr.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 16px;
            }
        """)

        qr_layout = QVBoxLayout(card_qr)

        qr_title = QLabel("QR Code Antrian")
        qr_title.setAlignment(Qt.AlignCenter)
        qr_title.setStyleSheet("font-weight: bold;")

        qr_layout.addWidget(qr_title)
        qr_layout.addWidget(self.qr_label, alignment=Qt.AlignCenter)

        footer = QLabel("Dicetak: 19-12-2025")
        footer.setAlignment(Qt.AlignRight)
        footer.setStyleSheet("font-size: 11px; color: #546E7A;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        layout.addWidget(header)
        layout.addWidget(card_info)
        layout.addWidget(card_qr)
        layout.addWidget(footer)
        layout.addStretch()
        







   

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    w = CDSSWindow(user_id="USER")
    w.show()
    sys.exit(app.exec())
