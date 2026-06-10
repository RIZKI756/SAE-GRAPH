import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QFileDialog
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtCore import Qt, pyqtSignal

# Liste de couleurs pastels pour distinguer les zones
COULEURS_PASTELS = [
    QColor("#ffb8b8"), QColor("#ffd3b6"), QColor("#dff9fb"),
    QColor("#c7ecee"), QColor("#e0ccc2"), QColor("#ffcccc")
]

class GridWidget(QWidget):
    cellule_cliquee = pyqtSignal(int, int)
    chiffre_saisi = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grille = None
        self.selection = None
        self.couleurs_motifs = {}
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(400, 400)

    def set_grille(self, grille):
        self.grille = grille
        self.selection = None
        if grille:
            self.attribuer_couleurs_motifs()
        self.update()

    def attribuer_couleurs_motifs(self):
        self.couleurs_motifs = {}
        for i, motif in enumerate(self.grille.motifs):
            self.couleurs_motifs[motif.id] = COULEURS_PASTELS[i % len(COULEURS_PASTELS)]

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.grille or self.grille.largeur == 0:
            painter.fillRect(self.rect(), QColor("#dcdde1"))
            return

        # Calcul automatique de la taille des cellules pour que ça rentre dans la fenêtre
        taille_cellule = min(self.width() // self.grille.largeur, self.height() // self.grille.hauteur)

        # Dessin du fond des cases avec leurs couleurs de motif
        for (c, r), case in self.grille.cases.items():
            rect = Qt.QtCore.QRect(c * taille_cellule, r * taille_cellule, taille_cellule, taille_cellule)
            
            # On pioche la couleur associée au motif (déclenche le bug ou l'affichage bizarre selon l'utilisation)
            couleur_fond = self.couleurs_motifs.get(case.motif.id, QColor("#ffffff"))
            painter.fillRect(rect, couleur_fond)

            # Dessin des bordures fines par défaut
            painter.setPen(QPen(QColor("#7f8c8d"), 1))
            painter.drawRect(rect)

            # Dessin du texte/chiffre
            if case.valeur != 0:
                painter.setPen(QColor("#2c3e50"))
                painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold if case.est_initiale else QFont.Weight.Normal))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(case.valeur))

    def mousePressEvent(self, event):
        if not self.grille or self.grille.largeur == 0:
            return
        taille_cellule = min(self.width() // self.grille.largeur, self.height() // self.grille.hauteur)
        c = event.position().x() // taille_cellule
        r = event.position().y() // taille_cellule
        
        if 0 <= c < self.grille.largeur and 0 <= r < self.grille.hauteur:
            self.selection = (int(c), int(r))
            self.cellule_cliquee.emit(int(c), int(r))
            self.update()

    def keyPressEvent(self, event):
        if not self.selection:
            return
        texte = event.text()
        if texte.isdigit() and texte != "0":
            self.chiffre_saisi.emit(int(texte))
        elif event.key() == Qt.Key.Key_Backspace or event.key() == Qt.Key.Key_Delete:
            self.chiffre_saisi.emit(0)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Néonaure - SAÉ Graphes-IHM")
        self.resize(800, 600)
        self._creer_interface()

    def _creer_interface(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QHBoxLayout(widget_central)

        self.grid_widget = GridWidget()
        layout_principal.addWidget(self.grid_widget, stretch=3)
