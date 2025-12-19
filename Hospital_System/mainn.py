import sys, sqlite3
from PySide6.QtWidgets import (
      QApplication, QWidget, QPushButton, QVBoxLayout, 
      QGraphicsOpacityEffect, QMessageBox
)
from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from PySide6.QtGui import QPixmap   
from modules.splash_screen import SplashScreen
from modules.Login_Signup import SignupWindow, LoginWindow 
from modules.Revisi_Regristrasi import MenuRegistrasi 
from modules.Appointment import PatientAppointmentWindow # type: ignore
from modules.EHR import CDSSWindow, StrukEHR
from database.db_helper import init_db  # type: ignore

class MainDashboard(QWidget):
      def __init__(self):
            super().__init__()
            self.current_user_id = None
            self.setWindowTitle("Hospital System")
            self.setFixedSize(400, 600)

            # Background ilustrasi dari Canva 
            self.bg_label = QLabel(self)
            self.bg_label.setPixmap(QPixmap("assets/dashboard.png").scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
            self.bg_label.setGeometry(0, 0, 400, 600)
            self.bg_label.lower()

            layout = QVBoxLayout()
            layout.setContentsMargins(30, 20, 30, 30)
            layout.setSpacing(12)

            btn_login = QPushButton("Login / Signup")
            btn_login.clicked.connect(self.open_login)

            btn_registrasi = QPushButton("Registrasi Pasien")
            btn_registrasi.clicked.connect(self.open_registrasi)

            btn_appointment = QPushButton("Janji Temu")
            btn_appointment.clicked.connect(self.open_appointment)

            btn_cdss_ehr = QPushButton("Riwayat CDSS & EHR")
            btn_cdss_ehr.clicked.connect(self.open_cdss_ehr)

            btn_ehr_viewer = QPushButton("Lihat Rekaman EHR")
            btn_ehr_viewer.clicked.connect(self.open_ehr_viewer)
           
            layout.addStretch(2)
            layout.addWidget(btn_login)
            layout.addWidget(btn_registrasi)
            layout.addWidget(btn_appointment)
            layout.addWidget(btn_cdss_ehr)
            layout.addWidget(btn_ehr_viewer)
            layout.addStretch()

            self.setLayout(layout)

            self.setStyleSheet("""
                  QWidget {
                        background-color: #F7FAFF;
                        font-family: 'Segoe UI';
                        font-size: 14px;
                        color: #2A2A3F;
                  }
                  QPushButton {
                        background-color: #1976D2;
                        color: white;
                        padding: 12px;
                        border-radius: 10px;
                        font-weight: bold;
                        font-size: 15px;
                        margin: 6px;
                  }
                  QPushButton:hover {
                        background-color: #1565C0;
                        color: #E3F2FD;
                  }
                  QPushButton:pressed {
                        background-color: #0D47A1;
                  }
            """)
            
            self.apply_fade_in()    
            
            # 🔹 Tambahkan efek fade-in
      def apply_fade_in(self):
            self.opacity_effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(self.opacity_effect)

            self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.animation.setDuration(1200)  # 1.2 detik
            self.animation.setStartValue(0.0)
            self.animation.setEndValue(1.0)
            self.animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.animation.start()

      # Login / Signup     
      def open_login(self):
        def after_login(user_id):
            self.current_user_id = user_id

            def after_registrasi(user_id):
                self.current_user_id = user_id

                def after_appointment():
                    # setelah appointment selesai, kembali ke dashboard
                    QMessageBox.information(self, "Selesai", "Appointment berhasil dibuat!")
                    self.show()

                # buka appointment setelah registrasi
                self.app = PatientAppointmentWindow(user_id=user_id, on_finished=after_appointment)
                self.app.show()

            # buka registrasi setelah login
            self.reg = MenuRegistrasi(user_id=user_id, on_finished=after_registrasi)
            self.reg.show()

        self.login = LoginWindow(on_success=after_login)
        self.login.show()

      def open_signup(self):
        def after_signup(user_id):
            self.current_user_id = user_id

            def after_registrasi(user_id):
                self.current_user_id = user_id

                def after_appointment():
                    QMessageBox.information(self, "Selesai", "Appointment berhasil dibuat!")
                    self.show()

                self.app = PatientAppointmentWindow(user_id=user_id, on_finished=after_appointment)
                self.app.show()

            self.reg = MenuRegistrasi(user_id=user_id, on_finished=after_registrasi)
            self.reg.show()

        self.signup_window = SignupWindow(back_to_login=after_signup)
        self.signup_window.show()
        self.hide()
 
      # Registrasi 
      def open_registrasi(self):
           if not self.current_user_id:
                 QMessageBox.warning(self, "Peringatan", "Silakan login terlebih dahulu!")
                 return
           self.reg = MenuRegistrasi(user_id=self.current_user_id)
           self.reg.show()

      # Appointment 
      def open_appointment(self):
            if not self.current_user_id:
                  QMessageBox.warning(self, "Peringatan", "Silakan login terlebih dahulu!")
                  return
            self.app = PatientAppointmentWindow(user_id=self.current_user_id)
            self.app.show()

      # CDSS & EHR 
      def open_cdss_ehr(self):
        user_id = self.current_user_id if self.current_user_id else "GUEST"
        self.cdss_ehr = CDSSWindow(user_id=user_id)
        self.cdss_ehr.show()

      def open_ehr_viewer(self):
            user_id = self.current_user_id if self.current_user_id else "GUEST"
            self.ehr_viewer = StrukEHR({
                  "patient": "Demo User",
                  "doctor": "Dr. Laura Alexandra, MRCP(ENT), MBBS",
                  "day": "Jumat",
                  "date": "19 Desember 2025",
                  "time": "14:30 WIB",
                  "riwayat": ["Demam", "Batuk"],
                  "resep": ["Paracetamol 500mg - 3x sehari"]
            }, on_back=self.show)
            self.ehr_viewer.show()
            self.hide()

     
def main():
      init_db()
      app = QApplication(sys.argv)

      # fungsi callback setelah splash 
      def show_dashboard():
            splash.close()
            window = MainDashboard()
            window.show()
            app.window = window 

      # tampilkan splash screen
      splash = SplashScreen(on_finished=show_dashboard)
      splash.show()

      sys.exit(app.exec())
            
if __name__ == "__main__":
      main()

