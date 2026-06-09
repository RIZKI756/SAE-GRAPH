from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt

class GridWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 300)

    def paintEvent(self, event):
        # Zone grise temporaire représentant l'emplacement de la grille
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#dcdde1"))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Néonaure - Squelette Application")
        self.resize(800, 600)
        self._creer_interface()

    def _creer_interface(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QHBoxLayout(widget_central)

        # Composant pour la future grille (Zone gauche)
        self.grid_widget = GridWidget()
        layout_principal.addWidget(self.grid_widget, stretch=3)

        # Séparateur visuel
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        layout_principal.addWidget(line)

        # Panneau de contrôle latéral (Zone droite)
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)

        title_label = QLabel("NÉONAURE")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(title_label)

        # Boutons bruts de l'interface
        self.btn_charger = QPushButton("Charger une Grille")
        sidebar_layout.addWidget(self.btn_charger)

        self.btn_verifier = QPushButton("Vérifier")
        sidebar_layout.addWidget(self.btn_verifier)

        self.btn_resoudre = QPushButton("Résoudre")
        sidebar_layout.addWidget(self.btn_resoudre)

        sidebar_layout.addStretch()
        layout_principal.addWidget(sidebar, stretch=1)