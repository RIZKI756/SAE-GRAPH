import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QIcon
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal

COLOR_BG_DARK = "#121214"
COLOR_SIDEBAR_BG = "#1a1a22"
COLOR_TEXT_MAIN = "#ffffff"
COLOR_TEXT_MUTED = "#8e8e9f"
COLOR_ACCENT = "#6c5ce7"
COLOR_ACCENT_HOVER = "#5b4bc4"

QCOLOR_GRID_BG = QColor("#16161c")
QCOLOR_BORDER_THIN = QColor("#2e2e3a")
QCOLOR_BORDER_THICK = QColor("#ffffff")
QCOLOR_TEXT_INITIAL = QColor("#f1c40f")
QCOLOR_TEXT_USER = QColor("#ffffff")
QCOLOR_SELECT = QColor(108, 92, 231, 80)
QCOLOR_CONFLICT = QColor(231, 76, 60, 95)

COULEURS_PASTELS = [
    QColor(43, 50, 75),
    QColor(25, 60, 65),
    QColor(70, 45, 60),
    QColor(75, 55, 40),
    QColor(35, 60, 45),
    QColor(40, 55, 75),
    QColor(55, 45, 70),
    QColor(60, 60, 65)
]

class GridWidget(QWidget):
    cellule_cliquee = pyqtSignal(int, int)
    chiffre_saisi = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grille = None
        self.selection = None
        self.conflits = []
        self.couleurs_motifs = {}
        
        self.margin = 15
        self.cell_size = 50
        self.x_offset = 0
        self.y_offset = 0
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(300, 300)

    def set_grille(self, grille):
        self.grille = grille
        self.selection = None
        self.conflits = []
        if grille:
            self.attribuer_couleurs_motifs()
        self.update()

    def set_conflits(self, conflits):
        self.conflits = conflits
        self.update()

    def attribuer_couleurs_motifs(self):
        self.couleurs_motifs = {}
        if not self.grille:
            return
        for i, motif in enumerate(self.grille.motifs):
            self.couleurs_motifs[motif.id] = i % len(COULEURS_PASTELS)

    def paintEvent(self, event):
        if not self.grille or self.grille.largeur == 0:
            painter = QPainter(self)
            painter.setPen(QPen(QColor(COLOR_TEXT_MUTED)))
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Aucune grille chargée.")
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w_dispo = self.width() - 2 * self.margin
        h_dispo = self.height() - 2 * self.margin
        
        self.cell_size = min(w_dispo // self.grille.largeur, h_dispo // self.grille.hauteur)
        self.cell_size = max(self.cell_size, 30)

        self.x_offset = self.margin + (w_dispo - self.cell_size * self.grille.largeur) // 2
        self.y_offset = self.margin + (h_dispo - self.cell_size * self.grille.hauteur) // 2

        rect_grille = QRect(self.x_offset, self.y_offset, 
                            self.cell_size * self.grille.largeur, 
                            self.cell_size * self.grille.hauteur)
        painter.fillRect(rect_grille, QCOLOR_GRID_BG)

        for (col, row), case in self.grille.cases.items():
            cx = self.x_offset + col * self.cell_size
            cy = self.y_offset + row * self.cell_size
            rect_case = QRect(cx, cy, self.cell_size, self.cell_size)

            couleur_fond = QColor("#1f1f26")
            if case.motif and case.motif.id in self.couleurs_motifs:
                couleur_idx = self.couleurs_motifs[case.motif.id]
                couleur_fond = COULEURS_PASTELS[couleur_idx]
            
            painter.fillRect(rect_case, couleur_fond)

            if self.selection == (col, row):
                painter.fillRect(rect_case, QCOLOR_SELECT)

            if case in self.conflits:
                painter.fillRect(rect_case, QCOLOR_CONFLICT)

        for (col, row), case in self.grille.cases.items():
            if case.valeur > 0:
                cx = self.x_offset + col * self.cell_size
                cy = self.y_offset + row * self.cell_size
                rect_case = QRect(cx, cy, self.cell_size, self.cell_size)

                font = QFont("Segoe UI", int(self.cell_size * 0.45))
                if case.est_initiale:
                    font.setBold(True)
                    painter.setPen(QPen(QCOLOR_TEXT_INITIAL))
                else:
                    painter.setPen(QPen(QCOLOR_TEXT_USER))
                
                painter.setFont(font)
                painter.drawText(rect_case, Qt.AlignmentFlag.AlignCenter, str(case.valeur))

        pen_thin = QPen(QCOLOR_BORDER_THIN, 1, Qt.PenStyle.SolidLine)
        pen_thick = QPen(QCOLOR_BORDER_THICK, 3, Qt.PenStyle.SolidLine)

        painter.setPen(pen_thin)
        for (col, row), case in self.grille.cases.items():
            cx = self.x_offset + col * self.cell_size
            cy = self.y_offset + row * self.cell_size
            
            c_droite = self.grille.get_case(col + 1, row)
            if c_droite and c_droite.motif == case.motif:
                painter.drawLine(cx + self.cell_size, cy, cx + self.cell_size, cy + self.cell_size)
            
            c_bas = self.grille.get_case(col, row + 1)
            if c_bas and c_bas.motif == case.motif:
                painter.drawLine(cx, cy + self.cell_size, cx + self.cell_size, cy + self.cell_size)

        painter.setPen(pen_thick)
        for (col, row), case in self.grille.cases.items():
            cx = self.x_offset + col * self.cell_size
            cy = self.y_offset + row * self.cell_size
            
            c_haut = self.grille.get_case(col, row - 1)
            if not c_haut or c_haut.motif != case.motif:
                painter.drawLine(cx, cy, cx + self.cell_size, cy)
                
            c_gauche = self.grille.get_case(col - 1, row)
            if not c_gauche or c_gauche.motif != case.motif:
                painter.drawLine(cx, cy, cx, cy + self.cell_size)

            c_droite = self.grille.get_case(col + 1, row)
            if not c_droite or c_droite.motif != case.motif:
                painter.drawLine(cx + self.cell_size, cy, cx + self.cell_size, cy + self.cell_size)

            c_bas = self.grille.get_case(col, row + 1)
            if not c_bas or c_bas.motif != case.motif:
                painter.drawLine(cx, cy + self.cell_size, cx + self.cell_size, cy + self.cell_size)

    def mousePressEvent(self, event):
        if not self.grille or self.grille.largeur == 0:
            return
        pos = event.position().toPoint()
        col = (pos.x() - self.x_offset) // self.cell_size
        row = (pos.y() - self.y_offset) // self.cell_size

        if 0 <= col < self.grille.largeur and 0 <= row < self.grille.hauteur:
            self.selection = (col, row)
            self.cellule_cliquee.emit(col, row)
            self.update()
        else:
            self.selection = None
            self.update()

    def keyPressEvent(self, event):
        if not self.grille or not self.selection:
            super().keyPressEvent(event)
            return
        col, row = self.selection
        case = self.grille.get_case(col, row)
        if not case or case.est_initiale:
            self._gerer_navigation(event.key())
            return
        key = event.key()
        if Qt.Key.Key_1 <= key <= Qt.Key.Key_9:
            self.chiffre_saisi.emit(key - Qt.Key.Key_0)
        elif key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete, Qt.Key.Key_0):
            self.chiffre_saisi.emit(0)
        else:
            self._gerer_navigation(key)

    def _gerer_navigation(self, key):
        if not self.selection or not self.grille:
            return
        col, row = self.selection
        if key == Qt.Key.Key_Up: row = max(0, row - 1)
        elif key == Qt.Key.Key_Down: row = min(self.grille.hauteur - 1, row + 1)
        elif key == Qt.Key.Key_Left: col = max(0, col - 1)
        elif key == Qt.Key.Key_Right: col = min(self.grille.largeur - 1, col + 1)
        else: return
        self.selection = (col, row)
        self.cellule_cliquee.emit(col, row)
        self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Néonaure - Résolution & Jeu (SAÉ Graphes)")
        self.resize(800, 600)
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {COLOR_BG_DARK}; }}
            QLabel {{ color: {COLOR_TEXT_MAIN}; font-family: 'Segoe UI', Arial, sans-serif; }}
            QPushButton {{
                background-color: {COLOR_ACCENT}; color: white; border: none;
                border-radius: 6px; padding: 10px 16px; font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {COLOR_ACCENT_HOVER}; }}
            QPushButton:pressed {{ background-color: #4d3eb0; }}
            QStatusBar {{ background-color: {COLOR_SIDEBAR_BG}; color: {COLOR_TEXT_MUTED}; }}
            QMenuBar {{ background-color: {COLOR_SIDEBAR_BG}; color: {COLOR_TEXT_MAIN}; }}
            QMenuBar::item:selected {{ background-color: {COLOR_ACCENT}; }}
        """)
        self._creer_interface()
        # self._creer_menus()

    def _creer_interface(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)

        self.grid_widget = GridWidget()
        layout_principal.addWidget(self.grid_widget, stretch=3)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setStyleSheet("color: #2e2e3a;")
        layout_principal.addWidget(line)

        sidebar = QWidget()
        sidebar.setStyleSheet(f"QWidget {{ background-color: {COLOR_SIDEBAR_BG}; border-radius: 10px; }}")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(15)

        title_label = QLabel("NÉONAURE")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 26px; font-weight: 800; letter-spacing: 2px; color: #ffffff; background: transparent;")
        sidebar_layout.addWidget(title_label)

        subtitle_label = QLabel("Jeu de Grille & Graphes")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px; font-weight: bold; background: transparent;")
        sidebar_layout.addWidget(subtitle_label)

        info_widget = QWidget()
        info_widget.setStyleSheet("background: transparent;")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setSpacing(6)

        self.timer_label = QLabel("⏱️ 00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #f1c40f; font-family: 'Consolas', monospace; background: transparent;")
        info_layout.addWidget(self.timer_label)

        line_sep = QFrame()
        line_sep.setFrameShape(QFrame.Shape.HLine)
        line_sep.setStyleSheet("color: #2a2a35; max-height: 1px;")
        info_layout.addWidget(line_sep)

        self.level_label = QLabel("📄 -")
        self.level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.level_label.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_MUTED}; background: transparent;")
        info_layout.addWidget(self.level_label)

        self.size_label = QLabel("📐 -")
        self.size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.size_label.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_MUTED}; background: transparent;")
        info_layout.addWidget(self.size_label)

        sidebar_layout.addWidget(info_widget)
        sidebar_layout.addSpacing(10)
        
        self.btn_charger = QPushButton("Charger une Grille")
        sidebar_layout.addWidget(self.btn_charger)

        self.btn_aleatoire = QPushButton("Grille Aléatoire")
        self.btn_aleatoire.setStyleSheet("background-color: #4b6584; color: white;")
        sidebar_layout.addWidget(self.btn_aleatoire)

        self.btn_verifier = QPushButton("Règles du Jeu")
        self.btn_verifier.setStyleSheet(f"background-color: #2bcbba; color: {COLOR_BG_DARK};")
        sidebar_layout.addWidget(self.btn_verifier)

        self.btn_indice = QPushButton("Obtenir un Indice (3 restants)")
        self.btn_indice.setStyleSheet("background-color: #fa8231; color: white;")
        sidebar_layout.addWidget(self.btn_indice)

        self.btn_resoudre = QPushButton("Résoudre Directement")
        self.btn_resoudre.setStyleSheet("background-color: #fc5c65; color: white;")
        self.btn_resoudre.setVisible(False)
        sidebar_layout.addWidget(self.btn_resoudre)

        self.btn_reset = QPushButton("Réinitialiser")
        self.btn_reset.setStyleSheet("background-color: #4b6584; color: white;")
        sidebar_layout.addWidget(self.btn_reset)

        sidebar_layout.addStretch()

        help_tip = QLabel("Astuce : Cliquez sur une case puis tapez un chiffre. 0 pour effacer.")
        help_tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        help_tip.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-style: italic; background: transparent;")
        sidebar_layout.addWidget(help_tip)

        layout_principal.addWidget(sidebar, stretch=1)
        self.statusBar = self.statusBar()
        self.statusBar.showMessage("Bienvenue !")

    def _creer_menus(self):
        menubar = self.menuBar()
        menu_fichier = menubar.addMenu("Fichier")
        self.action_charger = menu_fichier.addAction("Charger Grille (JSON)...")
        self.action_sauvegarder = menu_fichier.addAction("Sauvegarder Partie...")
        menu_fichier.addSeparator()
        self.action_quitter = menu_fichier.addAction("Quitter")

        menu_jeu = menubar.addMenu("Jeu")
        self.action_verifier = menu_jeu.addAction("Vérifier la grille")
        self.action_indice = menu_jeu.addAction("Révéler un indice")
        self.action_resoudre = menu_jeu.addAction("Résolution automatique")
        self.action_resoudre.setEnabled(False)
        self.action_reset = menu_jeu.addAction("Réinitialiser la grille")

        menu_aide = menubar.addMenu("Aide")
        self.action_regles = menu_aide.addAction("Règles du jeu...")
        self.action_a_propos = menu_aide.addAction("À propos...")