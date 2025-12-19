from PySide6.QtWidgets import QWidget, QLabel, QGraphicsOpacityEffect
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QTimer, QPropertyAnimation, QEasingCurve, Qt

class SplashScreen(QWidget):
    def __init__(self, on_finished):
        super().__init__()
        self.setWindowTitle("CARESYNC")
        self.setFixedSize(400, 600)

        # Background dari Canva
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(QPixmap("assets/splash_screen.png").scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
        self.bg_label.setGeometry(0, 0, 400, 600)
     
        # Efek transparansi
        self.opacity_effect = QGraphicsOpacityEffect(self.bg_label)
        self.bg_label.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)

        # Timer untuk mulai animasi fade-out
        self._on_finished = on_finished
        QTimer.singleShot(2500, self._start_fade_out)  # mulai fade setelah 2.5 detik

    def _start_fade_out(self):
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(1000)  # durasi fade-out 1 detik
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.finished.connect(self._finish)
        self.animation.start()

    def _finish(self):
        if callable(self._on_finished):
            self._on_finished()

