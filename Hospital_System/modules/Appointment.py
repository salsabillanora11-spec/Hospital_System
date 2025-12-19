from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QGridLayout, QComboBox, QMessageBox, QCalendarWidget, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QTextCharFormat, QColor, QPixmap
import sqlite3
from modules.ReceiptWindow import ReceiptWindow # type: ignore

class PatientAppointmentWindow(QWidget):
    def __init__(self, user_id, on_finished=None):
        super().__init__()
        self.user_id = user_id
        self.on_finished = on_finished
        self.selected_slot = None
        self.slot_buttons = []

        self.setWindowTitle("Booking Janji Temu Pasien")
        self.setFixedSize(400, 600)

        # Desain 
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(
            QPixmap("assets/biruu.png")
            .scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        )
        self.bg_label.setGeometry(0, 0, 400, 600)
        self.bg_label.lower()

        # =========================
        # DATA DOKTER & SPESIALIS
        # =========================
        self.doctors = {
            "Penyakit Dalam": [
                "Dr. Andi Pratama - Sp.PD"
            ],
            "THT": [
                "Dr. Laura Alexandra - MRCP(ENT), MBBS, DNB"
            ],
            "Kulit": [
                "Dr. Siti Rahma - Sp.KK"
            ],
            "Kandungan": [
                "Dr. Budi Santoso - Sp.OG"
            ]
        }

        self.keluhan_to_spesialis = {
            "Flu / Demam": "Penyakit Dalam",
            "Batuk & Gangguan THT": "THT",
            "Masalah Kulit": "Kulit",
            "Kehamilan & Kandungan": "Kandungan"
        }

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(14)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)

        # =========================
        # PILIH KELUHAN
        # =========================
        layout.addWidget(QLabel("Pilih Keluhan / Konsultasi"))
        self.keluhan_combo = QComboBox()
        self.keluhan_combo.addItems(self.keluhan_to_spesialis.keys())
        self.keluhan_combo.currentIndexChanged.connect(self.update_doctor_list)
        layout.addWidget(self.keluhan_combo)

        # =========================
        # PILIH DOKTER (AUTO FILTER)
        # =========================
        layout.addWidget(QLabel("Dokter Spesialis"))
        self.doctor_combo = QComboBox()
        layout.addWidget(self.doctor_combo)

        # =========================
        # PILIH TANGGAL
        # =========================
        layout.addWidget(QLabel("Pilih Jadwal Kontrol"))
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setMinimumDate(QDate.currentDate())
        self.calendar.selectionChanged.connect(self.highlight_selected_date)
        layout.addWidget(self.calendar)

        self.setup_calendar_style()

        # =========================
        # SLOT WAKTU
        # =========================
        slot_grid = QGridLayout()
        slots = {
            "Pagi": ["10:00 AM", "11:00 AM", "12:00 PM"],
            "Siang": ["01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM"],
            "Malam": ["05:00 PM", "06:00 PM", "07:00 PM", "08:00 PM"]
        }

        row = 0
        for period, times in slots.items():
            slot_grid.addWidget(QLabel(period), row, 0)
            for i, time in enumerate(times):
                btn = QPushButton(time)
                btn.clicked.connect(lambda checked, b=btn, t=time: self.select_slot(b, t))

                if time in ["12:00 PM", "01:00 PM", "03:00 PM"]:
                    btn.setEnabled(False)
                self.slot_buttons.append(btn)
                slot_grid.addWidget(btn, row, i + 1)
            row += 1

        layout.addLayout(slot_grid)

        # =========================
        # KONFIRMASI
        # =========================
        confirm_btn = QPushButton("Konfirmasi Janji Temu")
        confirm_btn.clicked.connect(self.confirm_appointment)
        layout.addWidget(confirm_btn)

        # Tombol kembali ke menu
        daashboard_btn = QPushButton("Kembali ke Menu")
        daashboard_btn.clicked.connect(self._start_fade_out)
        layout.addWidget(daashboard_btn)

        self.setLayout(layout)

    # =========================
    # UPDATE DOKTER SESUAI KELUHAN
    # =========================
    def update_doctor_list(self):
        keluhan = self.keluhan_combo.currentText()
        spesialis = self.keluhan_to_spesialis.get(keluhan)

        self.doctor_combo.clear()
        if spesialis in self.doctors:
            self.doctor_combo.addItems(self.doctors[spesialis])

    # =========================
    # KALENDAR STYLE
    # =========================
    def setup_calendar_style(self):
        today = QDate.currentDate()

        default_format = QTextCharFormat()
        default_format.setForeground(QColor("#2D8CDE"))

        weekend_format = QTextCharFormat()
        weekend_format.setForeground(QColor("#F48FB1"))

        today_format = QTextCharFormat()
        today_format.setBackground(QColor("#89BAE3"))
        today_format.setForeground(QColor("#0D47A1"))

        self.calendar.setDateTextFormat(today, today_format)

        for day in range(1, 32):
            date = QDate(today.year(), today.month(), day)
            if date.isValid():
                if date.dayOfWeek() in [6, 7]:
                    self.calendar.setDateTextFormat(date, weekend_format)
                else:
                    self.calendar.setDateTextFormat(date, default_format)

    def highlight_selected_date(self):
        selected = self.calendar.selectedDate()
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("#1478DC"))
        fmt.setForeground(QColor("white"))
        self.calendar.setDateTextFormat(selected, fmt)

    # =========================
    # PILIH SLOT
    # =========================
    def select_slot(self, button, slot_time):
        if not button.isEnabled():
            QMessageBox.warning(self, "Slot Tidak Tersedia", "Slot ini tidak bisa dipilih.")
            return

        for btn in self.slot_buttons:
            btn.setProperty("selected", False)
            btn.setStyleSheet("")

        button.setProperty("selected", True)
        button.setStyleSheet("background-color:#43A047;color:white;")
        self.selected_slot = slot_time


    # =========================
    # SIMPAN JANJI TEMU
    # =========================
    def confirm_appointment(self):
        if not self.selected_slot:
            QMessageBox.warning(self, "Peringatan", "Silakan pilih slot waktu!")
            return

        keluhan = self.keluhan_combo.currentText()
        spesialis = self.keluhan_to_spesialis.get(keluhan)
        doctor = self.doctor_combo.currentText()
        day = self.calendar.selectedDate().toString("dddd, dd MMMM yyyy")
        slot = self.selected_slot

        conn = sqlite3.connect("hospital.db")
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                doctor TEXT,
                day TEXT,
                slot TEXT,
                queue_number INTEGER
            )
        """)

        # 🔧 PATCH ERROR (TANPA HAPUS DATA)
        try:
            cur.execute("ALTER TABLE appointment ADD COLUMN keluhan TEXT")
        except sqlite3.OperationalError:
            pass

        try:
            cur.execute("ALTER TABLE appointment ADD COLUMN spesialis TEXT")
        except sqlite3.OperationalError:
            pass

        # 🔧 Tambahkan kolom queue_number jika belum ada
        try:
            cur.execute("ALTER TABLE appointment ADD COLUMN queue_number INTEGER")
        except sqlite3.OperationalError:
            pass  # kolom sudah ada, lanjutkan

        cur.execute("SELECT COUNT(*) FROM appointment WHERE day=?", (day,))
        queue = cur.fetchone()[0] + 1

        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                keluhan TEXT,
                spesialis TEXT,
                doctor TEXT,
                day TEXT,
                slot TEXT,
                queue_number INTEGER
            )
        """)

        conn.commit()
        conn.close()

        QMessageBox.information(
            self,
            "Berhasil",
            f"Janji temu berhasil!\nNomor Antrian: {queue}"
        )

        # panggil ReceiptWindow dg data hasil appointment
        self.receipt = ReceiptWindow(
            data={
                "queue": queue,
                "patient": self.user_id,
                "doctor": doctor,
                "date": day,
                "time": slot,
                "keluhan": keluhan,
                "spesialis": spesialis
            },
            on_back=lambda: self.on_finished(self.user_id) if self.on_finished else None
        )
        self.receipt.show()
        self._start_fade_out_to_receipt()

    def apply_fade_in(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.animation_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation_in.setDuration(1000)
        self.animation_in.setStartValue(0.0)
        self.animation_in.setEndValue(1.0)
        self.animation_in.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation_in.start()

    def _start_fade_out(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.animation_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation_out.setDuration(800)
        self.animation_out.setStartValue(1.0)
        self.animation_out.setEndValue(0.0)
        self.animation_out.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation_out.finished.connect(self._finish_back)
        self.animation_out.start()

    def _finish_back(self):
        self.close()
        if self.on_finished:
            self.on_finished(self.user_id)

    def _start_fade_out_to_receipt(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.animation_out_to_receipt = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation_out_to_receipt.setDuration(1000)
        self.animation_out_to_receipt.setStartValue(1.0)
        self.animation_out_to_receipt.setEndValue(0.0)
        self.animation_out_to_receipt.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation_out_to_receipt.finished.connect(self._open_receipt)
        self.animation_out_to_receipt.start()

    def _open_receipt(self):
        self.close()
        self.receipt = ReceiptWindow(
            data=self.receipt_data,
            on_back=lambda: self.on_finished(self.user_id) if self.on_finished else None
        )
        self.receipt.show()

    # =========================
    # STYLE UI
    # =========================
    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: "Segoe UI", Arial;
                font-size: 14px;
                color: #1976D2;
            }
            QLabel {
                font-size: 15px;
                font-weight: 600;
                color: #0D47A1;
            }
            QComboBox {
                background-color: #F5F9FF;
                background: white;
                border: 1px solid #BBDEFB;
                border-radius: 6px;
                padding: 6px;
                color: #1976D2;
            }
            QComboBox::drop-down {
                background-color: #E3F2FD;
                border-left: 1px solid #BBDEFB;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                selection-background-color: #1976D2;
                selection-color: white;
            }
            QPushButton {
                background-color: #1976D2;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)