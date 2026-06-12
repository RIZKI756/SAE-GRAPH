import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QIcon
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal

# Couleurs
COLOR_BG_DARK = "#121214"
COLOR_SIDEBAR_BG = "#1a1a22"
COLOR_TEXT_MAIN = "#ffffff"
COLOR_TEXT_MUTED = "#8e8e9f"
COLOR_ACCENT = "#6c5ce7"
COLOR_ACCENT_HOVER = "#5b4bc4"

# Couleurs pour le dessin
QCOLOR_GRID_BG = QColor("#16161c")
QCOLOR_BORDER_THIN = QColor("#2e2e3a")
QCOLOR_BORDER_THICK = QColor("#ffffff")
QCOLOR_TEXT_INITIAL = QColor("#f1c40f")  # Or pour les chiffres fixes
QCOLOR_TEXT_USER = QColor("#ffffff")     # Blanc pour le joueur
QCOLOR_SELECT = QColor(108, 92, 231, 80) # Violet translucide
QCOLOR_CONFLICT = QColor(231, 76, 60, 95) # Rouge translucide pour les erreurs

# Liste de couleurs
COULEURS_PASTELS = [
    QColor(43, 50, 75),   # Indigo feutré
    QColor(25, 60, 65),   # Vert canard sombre
    QColor(70, 45, 60),   # Prune doux
    QColor(75, 55, 40),   # Cuivre/Châtain
    QColor(35, 60, 45),   # Vert forêt sombre
    QColor(40, 55, 75),   # Bleu ardoise
    QColor(55, 45, 70),   # Violet profond
    QColor(60, 60, 65)    # Gris anthracite
]

class GridWidget(QWidget):
    # On gère le dessin de la grille ici
    # Signaux pour communiquer avec le contrôleur
    cellule_cliquee = pyqtSignal(int, int) # (col, row)
    chiffre_saisi = pyqtSignal(int)        # valeur (0 pour effacer)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grille = None
        self.selection = None  # Tuple (col, row) ou None
        self.conflits = []     # Liste d'objets Case en conflit
        self.couleurs_motifs = {} # Dictionnaire {motif_id: QColor}
        
        # Propriétés d'affichage
        self.margin = 15
        self.cell_size = 50
        self.x_offset = 0
        self.y_offset = 0
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(300, 300)

    def set_grille(self, grille):
        # Associe la grille et recalcule les couleurs
        self.grille = grille
        self.selection = None
        self.conflits = []
        if grille:
            self.attribuer_couleurs_motifs()
        self.update()

    def set_conflits(self, conflits):
        # Met à jour les erreurs
        self.conflits = conflits
        self.update()

    def attribuer_couleurs_motifs(self):
        # Gère les couleurs des motifs
        self.couleurs_motifs = {}
        if not self.grille:
            return

        # On donne juste une couleur à chaque motif selon son ordre dans la liste
        # Tant pis si deux motifs à côté ont la même couleur, c'est trop compliqué sinon
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

        # Calculer la taille optimale des cases pour qu'elles restent carrées
        w_dispo = self.width() - 2 * self.margin
        h_dispo = self.height() - 2 * self.margin
        
        self.cell_size = min(w_dispo // self.grille.largeur, h_dispo // self.grille.hauteur)
        # Éviter des cases trop petites
        self.cell_size = max(self.cell_size, 30)

        # Calculer le décalage pour centrer la grille
        self.x_offset = self.margin + (w_dispo - self.cell_size * self.grille.largeur) // 2
        self.y_offset = self.margin + (h_dispo - self.cell_size * self.grille.hauteur) // 2

        # 1. Remplissage du fond de la grille
        rect_grille = QRect(self.x_offset, self.y_offset, 
                            self.cell_size * self.grille.largeur, 
                            self.cell_size * self.grille.hauteur)
        painter.fillRect(rect_grille, QCOLOR_GRID_BG)

        # 2. Dessiner le fond des motifs, la sélection et les conflits
        for (col, row), case in self.grille.cases.items():
            cx = self.x_offset + col * self.cell_size
            cy = self.y_offset + row * self.cell_size
            rect_case = QRect(cx, cy, self.cell_size, self.cell_size)

            # Couleur du motif associé
            couleur_fond = QColor("#1f1f26")
            if case.motif and case.motif.id in self.couleurs_motifs:
                couleur_idx = self.couleurs_motifs[case.motif.id]
                couleur_fond = COULEURS_PASTELS[couleur_idx]
            
            painter.fillRect(rect_case, couleur_fond)

            # Dessiner la surbrillance de sélection
            if self.selection == (col, row):
                painter.fillRect(rect_case, QCOLOR_SELECT)

            # Dessiner la surbrillance de conflit
            if case in self.conflits:
                painter.fillRect(rect_case, QCOLOR_CONFLICT)

        # 3. Dessiner les valeurs
        for (col, row), case in self.grille.cases.items():
            if case.valeur > 0:
                cx = self.x_offset + col * self.cell_size
                cy = self.y_offset + row * self.cell_size
                rect_case = QRect(cx, cy, self.cell_size, self.cell_size)

                # Style de police
                font = QFont("Segoe UI", int(self.cell_size * 0.45))
                if case.est_initiale:
                    font.setBold(True)
                    painter.setPen(QPen(QCOLOR_TEXT_INITIAL))
                else:
                    painter.setPen(QPen(QCOLOR_TEXT_USER))
                
                painter.setFont(font)
                painter.drawText(rect_case, Qt.AlignmentFlag.AlignCenter, str(case.valeur))

        # 4. Dessiner les bordures (fines d'abord, puis épaisses)
        pen_thin = QPen(QCOLOR_BORDER_THIN, 1, Qt.PenStyle.SolidLine)
        pen_thick = QPen(QCOLOR_BORDER_THICK, 3, Qt.PenStyle.SolidLine)

        # Bordures fines pour séparer les cases du même motif
        painter.setPen(pen_thin)
        for (col, row), case in self.grille.cases.items():
            cx = self.x_offset + col * self.cell_size
            cy = self.y_offset + row * self.cell_size
            
            # Droite
            c_droite = self.grille.get_case(col + 1, row)
            if c_droite and c_droite.motif == case.motif:
                painter.drawLine(cx + self.cell_size, cy, cx + self.cell_size, cy + self.cell_size)
            
            # Bas
            c_bas = self.grille.get_case(col, row + 1)
            if c_bas and c_bas.motif == case.motif:
                painter.drawLine(cx, cy + self.cell_size, cx + self.cell_size, cy + self.cell_size)

        # Bordures épaisses pour séparer des motifs différents ou pour le cadre extérieur
        painter.setPen(pen_thick)
        for (col, row), case in self.grille.cases.items():
            cx = self.x_offset + col * self.cell_size
            cy = self.y_offset + row * self.cell_size
            
            # Bordure haut
            c_haut = self.grille.get_case(col, row - 1)
            if not c_haut or c_haut.motif != case.motif:
                painter.drawLine(cx, cy, cx + self.cell_size, cy)
                
            # Bordure gauche
            c_gauche = self.grille.get_case(col - 1, row)
            if not c_gauche or c_gauche.motif != case.motif:
                painter.drawLine(cx, cy, cx, cy + self.cell_size)

            # Bordure droite
            c_droite = self.grille.get_case(col + 1, row)
            if not c_droite or c_droite.motif != case.motif:
                painter.drawLine(cx + self.cell_size, cy, cx + self.cell_size, cy + self.cell_size)

            # Bordure bas
            c_bas = self.grille.get_case(col, row + 1)
            if not c_bas or c_bas.motif != case.motif:
                painter.drawLine(cx, cy + self.cell_size, cx + self.cell_size, cy + self.cell_size)

    def mousePressEvent(self, event):
        if not self.grille or self.grille.largeur == 0:
            return

        # Coordonnées du clic locales
        pos = event.position().toPoint()
        
        # Calculer à quelle cellule correspond le clic
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
            # Empêcher l'édition des cases de départ mais permettre la navigation par flèches
            self._gerer_navigation(event.key())
            return

        key = event.key()
        
        # Saisie de chiffres
        if Qt.Key.Key_1 <= key <= Qt.Key.Key_9:
            valeur = key - Qt.Key.Key_0
            self.chiffre_saisi.emit(valeur)
        # Effacement
        elif key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete, Qt.Key.Key_0):
            self.chiffre_saisi.emit(0)
        # Touches directionnelles de navigation
        else:
            self._gerer_navigation(key)

    def _gerer_navigation(self, key):
        # Déplacement avec les flèches
        if not self.selection or not self.grille:
            return
            
        col, row = self.selection
        if key == Qt.Key.Key_Up:
            row = max(0, row - 1)
        elif key == Qt.Key.Key_Down:
            row = min(self.grille.hauteur - 1, row + 1)
        elif key == Qt.Key.Key_Left:
            col = max(0, col - 1)
        elif key == Qt.Key.Key_Right:
            col = min(self.grille.largeur - 1, col + 1)
        else:
            return
            
        self.selection = (col, row)
        self.cellule_cliquee.emit(col, row)
        self.update()


class MainWindow(QMainWindow):
    # La fenêtre principale
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Néonaure - Résolution & Jeu (SAÉ Graphes : Maillard Noaïm, Baelden Tom et Journée Gabriel)")
        self.resize(800, 600)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLOR_BG_DARK};
            }}
            QLabel {{
                color: {COLOR_TEXT_MAIN};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background-color: #4d3eb0;
            }}
            QStatusBar {{
                background-color: {COLOR_SIDEBAR_BG};
                color: {COLOR_TEXT_MUTED};
            }}
            QMenuBar {{
                background-color: {COLOR_SIDEBAR_BG};
                color: {COLOR_TEXT_MAIN};
            }}
            QMenuBar::item:selected {{
                background-color: {COLOR_ACCENT};
            }}
        """)

        self._creer_interface()
        self._creer_menus()

    def _creer_interface(self):
        # Widget principal
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)

        # Zone de gauche : La Grille de Jeu
        self.grid_widget = GridWidget()
        layout_principal.addWidget(self.grid_widget, stretch=3)

        # Séparateur vertical visuel
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #2e2e3a;")
        layout_principal.addWidget(line)

        # Zone de droite : Panneau latéral de contrôle
        sidebar = QWidget()
        sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {COLOR_SIDEBAR_BG};
                border-radius: 10px;
            }}
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(15)

        # Titre stylisé
        title_label = QLabel("NÉONAURE")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 26px;
            font-weight: 800;
            letter-spacing: 2px;
            color: #ffffff;
            background: transparent;
        """)
        sidebar_layout.addWidget(title_label)

        subtitle_label = QLabel("Jeu de Grille & Graphes")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px; font-weight: bold; background: transparent;")
        sidebar_layout.addWidget(subtitle_label)

        # Informations de jeu épurées et élégantes
        info_widget = QWidget()
        info_widget.setStyleSheet("background: transparent;")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 5, 0, 5)
        info_layout.setSpacing(6)

        # Affichage du chronomètre (style digital chic)
        self.timer_label = QLabel("00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet(f"""
            font-size: 24px; 
            font-weight: 700; 
            color: #f1c40f; 
            font-family: 'Consolas', 'Courier New', monospace;
            background: transparent;
            margin-bottom: 2px;
        """)
        info_layout.addWidget(self.timer_label)

        # Séparateur subtil
        line_sep = QFrame()
        line_sep.setFrameShape(QFrame.Shape.HLine)
        line_sep.setFrameShadow(QFrame.Shadow.Plain)
        line_sep.setStyleSheet("color: #2a2a35; max-height: 1px;")
        info_layout.addWidget(line_sep)

        # Détails du niveau (icône + nom de fichier)
        self.level_label = QLabel("-")
        self.level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.level_label.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_MUTED}; background: transparent;")
        info_layout.addWidget(self.level_label)

        # Détails des dimensions
        self.size_label = QLabel("-")
        self.size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.size_label.setStyleSheet(f"font-size: 12px; color: {COLOR_TEXT_MUTED}; background: transparent;")
        info_layout.addWidget(self.size_label)

        sidebar_layout.addWidget(info_widget)

        # Section des boutons d'actions
        sidebar_layout.addSpacing(10)
        
        self.btn_charger = QPushButton("Charger une Grille")
        self.btn_charger.setCursor(Qt.CursorShape.PointingHandCursor)
        sidebar_layout.addWidget(self.btn_charger)

        self.btn_aleatoire = QPushButton("Grille Aléatoire")
        self.btn_aleatoire.setStyleSheet("background-color: #4b6584; color: white;")
        self.btn_aleatoire.setCursor(Qt.CursorShape.PointingHandCursor)
        sidebar_layout.addWidget(self.btn_aleatoire)

        self.btn_verifier = QPushButton("Règles du Jeu")
        self.btn_verifier.setStyleSheet(f"background-color: #2bcbba; color: {COLOR_BG_DARK};")
        self.btn_verifier.setCursor(Qt.CursorShape.PointingHandCursor)
        sidebar_layout.addWidget(self.btn_verifier)

        self.btn_indice = QPushButton("Obtenir un Indice (3 restants)")
        self.btn_indice.setStyleSheet("background-color: #fa8231; color: white;")
        self.btn_indice.setCursor(Qt.CursorShape.PointingHandCursor)
        sidebar_layout.addWidget(self.btn_indice)

        self.btn_resoudre = QPushButton("Résoudre Directement")
        self.btn_resoudre.setStyleSheet("background-color: #fc5c65; color: white;")
        self.btn_resoudre.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_resoudre.setVisible(False)  # Masqué par défaut
        sidebar_layout.addWidget(self.btn_resoudre)

        self.btn_reset = QPushButton("Réinitialiser")
        self.btn_reset.setStyleSheet("background-color: #4b6584; color: white;")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        sidebar_layout.addWidget(self.btn_reset)

        sidebar_layout.addStretch()

        # Footer / Info d'aide rapide
        help_tip = QLabel("Astuce : Cliquez sur une case puis tapez un chiffre au clavier. 0 ou Ret.Arr. pour effacer.")
        help_tip.setWordWrap(True)
        help_tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        help_tip.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 11px; font-style: italic; background: transparent;")
        sidebar_layout.addWidget(help_tip)

        layout_principal.addWidget(sidebar, stretch=1)

        # Barre d'état
        self.statusBar = self.statusBar()
        self.statusBar.showMessage("Bienvenue ! Chargez une grille pour commencer à jouer.")

    def _creer_menus(self):
        menubar = self.menuBar()

        # Menu Fichier
        menu_fichier = menubar.addMenu("Fichier")
        
        self.action_charger = menu_fichier.addAction("Charger Grille (JSON)...")
        self.action_sauvegarder = menu_fichier.addAction("Sauvegarder Partie...")
        menu_fichier.addSeparator()
        self.action_quitter = menu_fichier.addAction("Quitter")

        # Menu Jeu / Aide
        menu_jeu = menubar.addMenu("Jeu")
        self.action_verifier = menu_jeu.addAction("Vérifier la grille")
        self.action_indice = menu_jeu.addAction("Révéler un indice")
        self.action_resoudre = menu_jeu.addAction("Résolution automatique")
        self.action_resoudre.setEnabled(False)  # Désactivé par défaut
        self.action_reset = menu_jeu.addAction("Réinitialiser la grille")

        # Menu À propos
        menu_aide = menubar.addMenu("Aide")
        self.action_regles = menu_aide.addAction("Règles du jeu...")
        self.action_a_propos = menu_aide.addAction("À propos...")

    def afficher_regles(self):
        QMessageBox.information(
            self, 
            "Règles du Néonaure",
            "1. Chaque case doit contenir un chiffre.\n"
            "2. Un motif contenant N cases doit être rempli avec les chiffres de 1 à N.\n"
            "3. Deux cases adjacentes (horizontalement, verticalement, ou diagonalement) "
            "ne peuvent pas contenir le même chiffre.\n\n"
            "Comment jouer :\n"
            "- Cliquez sur une cellule pour la sélectionner.\n"
            "- Saisissez un chiffre sur votre clavier pour l'inscrire.\n"
            "- Appuyez sur Retour Arrière ou Suppr pour effacer une case."
        )

    def afficher_a_propos(self):
        QMessageBox.about(
            self,
            "À propos - Néonaure",
            "Application Néonaure\n"
            "Développée dans le cadre de la SAÉ Graphes-IHM.\n\n"
            "Fonctionnalités :\n"
            "- Modélisation de la grille par graphe de contraintes\n"
            "- Interface utilisateur moderne en PyQt6"
        )