import sys, os
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QRadioButton
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class MenuRegistrasi(QWidget):
    def __init__(self, user_id, on_finished=None):
        super().__init__()
        self.user_id = user_id
        self.on_finished = on_finished
        self.setWindowTitle("Menu Registrasi")
        self.setFixedSize(400, 600)
        self.init_ui()

        # Background ilustrasi dari Canva 
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(
            QPixmap("assets/regis_screen.png")
            .scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        )
        self.bg_label.setGeometry(0, 0, 400, 600)
        self.bg_label.lower()

    def init_ui(self):

        # Layout utama
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 80, 30, 30)
        layout.setSpacing(16)

        # Input nama
        self.Nama_label = QLabel("Nama:")
        self.Nama = QLineEdit()
        self.Nama.setPlaceholderText("Masukkan nama")

        # Input NIK
        self.NIK_label = QLabel("NIK:")
        self.NIK = QLineEdit()
        self.NIK.setPlaceholderText("Masukkan NIK")

        # Tanggal lahir
        self.tgl_label = QLabel("Tanggal Lahir:")
        self.Tanggal_Lahir = QLineEdit()
        self.Tanggal_Lahir.setPlaceholderText("DD-MM-YYYY")
       
        # Gender
        self.gender_label = QLabel("Gender:")
        gender_layout = QHBoxLayout()
        self.male_radio = QRadioButton("Laki-laki")
        self.female_radio = QRadioButton("Perempuan")

        # Tambahkan radio ke layout
        gender_layout.addWidget(self.gender_label)
        gender_layout.addWidget(self.male_radio)
        gender_layout.addWidget(self.female_radio)

        # Kota
        self.kota_label = QLabel("Kota:")
        self.kota_input = QLineEdit()
        self.kota_input.setPlaceholderText("Kota")

        # Riwayat penyakit
        self.riwayat_label = QLabel("Riwayat Penyakit:")
        self.riwayat_input = QLineEdit()
        self.riwayat_input.setPlaceholderText("Riwayat penyakit Anda")

        # Tombol simpan data 
        self.btn_simpan = QPushButton("Simpan Data")
        self.btn_simpan.clicked.connect(self.simpan_data)

        # Masukkan semua widget ke layout
        layout.addStretch(1)
        layout.addWidget(self.Nama_label)
        layout.addWidget(self.Nama)

        layout.addWidget(self.NIK_label)
        layout.addWidget(self.NIK)

        layout.addWidget(self.tgl_label)
        layout.addWidget(self.Tanggal_Lahir)  

        layout.addWidget(self.gender_label)
        layout.addLayout(gender_layout)

        layout.addWidget(self.kota_label)
        layout.addWidget(self.kota_input)

        layout.addWidget(self.riwayat_label)
        layout.addWidget(self.riwayat_input)

        layout.addWidget(self.btn_simpan)

        self.setLayout(layout)
    
        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: #F7FAFF;
            }
            QLabel {
                font-family: Arial;
                background-color: transparent;
                color: black;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #C5CAE9;
                border-radius: 6px;
                background-color: white;
                color: black;
            }
            QRadioButton {
                color: black;
                font-size: 14px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
                border: 2px solid #5a91e8;
                border-radius: 7px;
            }
            QRadioButton::indicator:checked {
                background-color: #5a91e8;
            }
            QPushButton {
                background-color: #C5CAE9;
                color: #222222;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #82b1f7;
            }
            QPushButton:pressed {
                background-color: #4a81d8;
                color: white;
            }
        """)

    def simpan_data(self):
        nama = self.Nama.text()
        nik = self.NIK.text()

        # Ambil gender
        if self.male_radio.isChecked():
            gender = "Laki-laki"
        elif self.female_radio.isChecked():
            gender = "Perempuan"
        else:
            gender = ""

        # Validasi
        if nama == "" or nik == "" or gender == "":
            QMessageBox.warning(self, "Error", "Lengkapi semua data terlebih dahulu!")
            return
        
        # Simpan ke database
        import sqlite3
        conn = sqlite3.connect("hospital.db")
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO patients (user_id, nama, nik, dob, gender, kota, riwayat)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.user_id,
            self.Nama.text(),
            self.NIK.text(),
            self.Tanggal_Lahir.text(),
            gender,
            self.kota_input.text(),
            self.riwayat_input.text()
        ))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Sukses", "Data registrasi berhasil disimpan!")

         # 🔹 buka Appointment dengan efek fade in
        from modules.Appointment import PatientAppointmentWindow  # type: ignore
        if self.on_finished:
            self.appointment = PatientAppointmentWindow(user_id=self.user_id, on_finished=None)
            self.appointment.apply_fade_in()
            self.appointment.show()

        self.close()

if __name__ == "__main__":
    app = QApplication([])
    window = MenuRegistrasi(user_id="")
    window.show()
    app.exec()
