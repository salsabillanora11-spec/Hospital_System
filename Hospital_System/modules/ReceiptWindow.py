from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QFileDialog, QMessageBox, QGraphicsOpacityEffect
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
import qrcode
from datetime import datetime
import os

class ReceiptWindow(QWidget):
    def __init__(self, data, on_back=None):
        super().__init__()
        self.data = data
        self.on_back = on_back
        self.qr_path = "appointment_qr.png"

        self.setWindowTitle("Hospital System App - Medical Blue UI")
        self.resize(400, 600)
        self.setup_ui()
        self.generate_qr()

        # Desain 
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(
            QPixmap("assets/biruu.png")
            .scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        )
        self.bg_label.setGeometry(0, 0, 400, 600)
        self.bg_label.lower()

        # 🔹 Efek fade in saat window muncul
        self.apply_fade_in()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("STRUK PENDAFTARAN")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px; font-weight:bold;")

        info = QLabel(
            f"""
Nomor Antrian : {self.data['queue']}
Nama Pasien : {self.data['patient']}
Dokter : {self.data['doctor']}
Tanggal : {self.data['date']}
Jam : {self.data['time']}
Dicetak : {datetime.now().strftime('%d-%m-%Y')}
            """
        )
        info.setAlignment(Qt.AlignCenter)
        info.setStyleSheet("font-size:14px;")

        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)

        btn_download = QPushButton("Download QR Code")
        btn_back = QPushButton("Kembali ke Menu")

        btn_download.clicked.connect(self.download_qr)
        btn_back.clicked.connect(self.back)

        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(info)
        layout.addSpacing(10)
        layout.addWidget(self.qr_label)
        layout.addSpacing(15)
        layout.addWidget(btn_download)
        layout.addWidget(btn_back)

        

        # 🔹 Dominasi desain biru dengan font gelap
        self.setStyleSheet("""
            QWidget {
                background-color: #E3F2FD;   /* biru utama */
                font-family: 'Segoe UI';
                font-size: 14px;
                color: #0D47A1;              /* teks default putih agar kontras */
            }
            QLabel {
                font-size: 15px;
                font-weight: 600;
                color: #1565C0;              /* biru muda untuk teks label */
            }
            QPushButton {
                background-color: #1976D2;   /* tombol putih-biru */
                color: white;              /* font lebih gelap */
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #BBDEFB;   /* hover biru lebih terang */
            }
            QPushButton:pressed {
                background-color: #90CAF9;   /* pressed biru medium */
            }
             QFrame#qrFrame {
                border: 2px solid #1976D2;
                border-radius: 10px;
                padding: 6px;
                background-color: white;
            }
        """)
        self.setLayout(layout)

    def generate_qr(self):
        qr_data = f"""
Queue: {self.data['queue']}
Patient: {self.data['patient']}
Doctor: {self.data['doctor']}
Date: {self.data['date']}
Time: {self.data['time']}
        """

        img = qrcode.make(qr_data)
        img.save(self.qr_path)

        pixmap = QPixmap(self.qr_path).scaled(200, 200, Qt.KeepAspectRatio)
        self.qr_label.setPixmap(pixmap)

    def download_qr(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save QR Code", "appointment_qr.png", "PNG Files (*.png)"
        )
        if path:
            os.replace(self.qr_path, path)
            QMessageBox.information(self, "Berhasil", "QR Code berhasil disimpan.")
    
    # 🔹 Efek fade in
    def apply_fade_in(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.animation_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation_in.setDuration(1000)
        self.animation_in.setStartValue(3.0)
        self.animation_in.setEndValue(2.0)
        self.animation_in.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation_in.start()

    # 🔹 Efek fade out sebelum kembali
    def back(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.animation_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation_out.setDuration(800)
        self.animation_out.setStartValue(3.0)
        self.animation_out.setEndValue(0.0)
        self.animation_out.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation_out.finished.connect(self._go_back)
        self.animation_out.start()

    def back(self):
        self.close()
        if self.on_back:
            self.on_back()
