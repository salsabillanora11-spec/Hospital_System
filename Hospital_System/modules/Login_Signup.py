import sys, json, os
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QGraphicsOpacityEffect
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QPropertyAnimation

USER_FILE = "users.json"

# Helper Functions 
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# Signup Window 
class SignupWindow(QWidget):
    def __init__(self, on_success, back_to_login):
        super().__init__()
        self.on_success = on_success
        self.back_to_login = back_to_login
        self.setWindowTitle("Signup Pasien-CARESYNC")
        self.setFixedSize(400, 600)

        # Background ilustrasi dari Canva 
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(QPixmap("assets/Sign in_screen.png").scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.bg_label.setGeometry(0, 0, 400, 600)
        self.bg_label.lower()

        # Layout Utama
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(16)

        # Layout box text 
        self.usn_label = QLabel("Username: ")
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.email_label = QLabel("Email: ")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Masukkan email")

        self.pwd_label = QLabel("Password: ")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.confirm_label = QLabel("Confirm Password: ")
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm Password")
        self.confirm_input.setEchoMode(QLineEdit.Password)

        # Tombol login dan register 
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.signup)

        back_btn = QPushButton("Back to login")
        back_btn.clicked.connect(self.back_to_login)

        dashboard_btn = QPushButton("Go to Dashboard")
        dashboard_btn.clicked.connect(self.on_success)

        layout.addStretch(3)
        layout.addWidget(self.usn_label)
        layout.addWidget(self.username)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.pwd_label)
        layout.addWidget(self.password)
        layout.addWidget(self.confirm_label)
        layout.addWidget(self.confirm_input)
        layout.addStretch(2)
        layout.addWidget(register_btn)
        layout.addWidget(back_btn)
        layout.addWidget(dashboard_btn)
        layout.addStretch()
        
        self.setLayout(layout)

        # Gaya CARESYNC
        self.setStyleSheet("""
            QWidget {
                background-color: #F7FAFF;
            }
            QLabel {
                font-family: League Spartan;
                background-color: white;
                color: black;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #C5CAE9;
                border-radius: 6px;
                background-color: white;
                color: black;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #C5CAE9;
                border-radius: 6px;
                background-color: white;
                color: black;
                font-family: Arial;
            }
            QComboBox QAbstractItemView {
                background-color: #2A2A3F;
                color: white;
                selection-background-color: #3A3A5F;
            }
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
                color: black;
            }
        """)

    def back_to_dashboard(self):
        from main import MainDashboard # type: ignore
        self.close()
        self.dashboard = MainDashboard()
        self.dashboard.apply_fade_in()
        self.dashboard.show()


    def signup(self):
        users = load_users()
        uname = self.username.text()
        pwd = self.password.text()
        confirm_pwd = self.confirm_input.text()

        if uname in users:
            QMessageBox.warning(self, "Error", "Username sudah terdaftar!")
            return

        if not uname or not pwd or not confirm_pwd:
            QMessageBox.warning(self, "Error", "Isi semua field!")
            return
        
        if pwd != confirm_pwd:
            QMessageBox.warning(self, "Error", "Password tidak sama!")
            return
        
        import sqlite3
        conn = sqlite3.connect("hospital.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO patients(user_id, nama, dob, gender) VALUES(?,?,?,?)",
            (uname, uname, "2000-01-01", "Tidak Diketahui"))
        conn.commit()
        conn.close()

        # Simpan akun ke file JSON 
        users[uname] = {"password": pwd, "email": self.email_input.text()}
        save_users(users)
        QMessageBox.information(self, "Sukses", "Akun berhasil dibuat!")
        self.close()
        self.back_to_login()

    def back_to_dashboard(self):
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)

        self.animation_out = QPropertyAnimation(effect, b"opacity")
        self.animation_out.setDuration(800)
        self.animation_out.setStartValue(1)
        self.animation_out.setEndValue(0)
        self.animation_out.finished.connect(self._show_dashboard)
        self.animation_out.start()


# Login Window
class LoginWindow(QWidget):
    def __init__(self, on_success=None):
        super().__init__()
        self.on_success = on_success
        self.setWindowTitle("Login Pasien")
        self.setFixedSize(400, 600)
        

        # Background ilustrasi dari canva 
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(QPixmap("assets/Log in_screen.png").scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.bg_label.setGeometry(0, 0, 400, 600)
        self.bg_label.setScaledContents(True)
        self.bg_label.lower()

        # Layout Utama
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(16)

        self.username_label = QLabel("Username: ")
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password_label = QLabel("Password: ")
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password) 

        # Tombol login dan signup 
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)

        signup_btn = QPushButton("Signup")
        signup_btn.clicked.connect(self.open_signup)

        dashboard_btn = QPushButton("Kembali ke Dashboard")
        dashboard_btn.clicked.connect(self.back_to_dashboard)

        layout.addStretch(80)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username)
        layout.addWidget(self.password_label) 
        layout.addWidget(self.password)
        layout.setStretch(2, 1)
        layout.addWidget(login_btn)
        layout.addWidget(signup_btn)
        layout.addWidget(dashboard_btn)
        layout.addStretch()

        self.setLayout(layout)

         # Gaya CARESYNC
        self.setStyleSheet("""
            QWidget {
                background-color: #F7FAFF;
            }
            QLabel {
                font-family: League Spartan;
                background-color: white;
                color: black;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #C5CAE9;
                border-radius: 6px;
                background-color: white;
                color: black;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #C5CAE9;
                border-radius: 6px;
                background-color: white;
                color: black;
                font-family: Arial;
            }
            QComboBox QAbstractItemView {
                background-color: #2A2A3F;
                color: white;
                selection-background-color: #3A3A5F;
            }
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
                color: black;
            }
        """)
        
    def back_to_login(self):
        self.show()
        if hasattr(self, "signup_window"):
            self.signup_window.close()

    def back_to_dashboard(self):
        from main import MainDashboard  # type: ignore # pastikan import ini ada
        self.close()
        self.dashboard = MainDashboard()
        self.dashboard.apply_fade_in()  # opsional: efek transisi
        self.dashboard.show()

    
    def login(self):
        users = load_users()
        uname = self.username.text()
        pwd = self.password.text()

        if uname in users and users[uname]["password"] == pwd:
            QMessageBox.information(self, "Sukses", f"Selamat datang {uname}!")
            # TODO: buka window booking appointment
            if self.on_success:
                self.on_success(uname) 
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Username atau password salah!")
    
    def proses_login(self):
        user_id = "user123"  # hasil dari validasi
        if self.on_success:
            self.on_success(user_id)
        self.close()

    def open_signup(self):
        self.signup_window = SignupWindow(
            on_success=self.show,
            back_to_login=self.back_to_login
        )
        self.signup_window.show()
        self.hide()

    def back_to_dashboard(self):
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)

        self.animation_out = QPropertyAnimation(effect, b"opacity")
        self.animation_out.setDuration(800)
        self.animation_out.setStartValue(1)
        self.animation_out.setEndValue(0)
        self.animation_out.finished.connect(self._show_dashboard)
        self.animation_out.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())
