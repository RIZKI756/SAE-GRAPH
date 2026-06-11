import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from resolver import SolveurSuguru

class GameController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        # triggers btns
        self.view.btn_charger.clicked.connect(self.ouvrir_fichier_grille)
        self.view.btn_verifier.clicked.connect(self.verifier_grille)
        self.view.btn_resoudre.clicked.connect(self.resoudre_grille)
        
        # triggers grid UI
        self.view.grid_widget.cellule_cliquee.connect(self.on_case_selectionnee)
        self.view.grid_widget.chiffre_saisi.connect(self.on_chiffre_entre)

    def ouvrir_fichier_grille(self):
        dossier_defaut = os.path.join(os.getcwd(), "exemple_grille")
        if not os.path.exists(dossier_defaut):
            dossier_defaut = os.getcwd()

        chemin_fichier, _ = QFileDialog.getOpenFileName(
            self.view, "Sélectionner une grille", dossier_defaut, "Fichiers JSON (*.json)"
        )
        if chemin_fichier:
            nom_fichier = os.path.basename(chemin_fichier)
            self.model.charger_json(chemin_fichier)
            self.view.grid_widget.set_grille(self.model)
            self.view.level_label.setText(f"📄 {nom_fichier}")

    def verifier_grille(self):
        conflits = self.model.trouver_conflits()
        if len(conflits) > 0:
            QMessageBox.warning(self.view, "Erreur", "Des conflits sont presents sur la grille.")
        else:
            if self.model.est_complete_et_valide():
                QMessageBox.information(self.view, "Gagne", "Grille terminee sans fautes !")
            else:
                QMessageBox.information(self.view, "OK", "Pas d'erreurs, continuez.")

    def resoudre_grille(self):
        # exec solver
        solveur = SolveurSuguru(self.model)
        if solveur.resoudre():
            self.view.grid_widget.update()
            QMessageBox.information(self.view, "Solver", "Resolution OK.")
        else:
            QMessageBox.critical(self.view, "Solver", "Grille insoluble.")

    def on_case_selectionnee(self, col, row):
        pass

    def on_chiffre_entre(self, valeur):
        selection = self.view.grid_widget.selection
        if selection:
            case = self.model.cases.get(selection)
            if case and not case.est_initiale:
                case.valeur = valeur
                self.view.grid_widget.update()