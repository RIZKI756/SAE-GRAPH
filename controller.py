import os
from PyQt6.QtWidgets import QFileDialog

class GameController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        
        # Liaison du bouton de chargement
        self.view.btn_charger.clicked.connect(self.ouvrir_fichier_grille)
        
        # Liaison des clics et de la saisie sur la grille
        self.view.grid_widget.cellule_cliquee.connect(self.on_case_selectionnee)
        self.view.grid_widget.chiffre_saisi.connect(self.on_chiffre_entre)

    def ouvrir_fichier_grille(self):
        # Ouvre la boîte de dialogue pour chercher un JSON dans exemple_grille
        dossier_defaut = os.path.join(os.getcwd(), "exemple_grille")
        if not os.path.exists(dossier_defaut):
            dossier_defaut = os.getcwd()

        chemin_fichier, _ = QFileDialog.getOpenFileName(
            self.view, "Sélectionner une grille", dossier_defaut, "Fichiers JSON (*.json)"
        )
        
        if chemin_fichier:
            nom_fichier = os.path.basename(chemin_fichier)
            self.model.charger_json(chemin_fichier)
            
            # Injection des données dans la vue pour déclencher le dessin
            self.view.grid_widget.set_grille(self.model)
            self.view.level_label.setText(f"📄 {nom_fichier}")

    def on_case_selectionnee(self, col, row):
        pass  # On mémorise la sélection dans le GridWidget directement pour le moment

    def on_chiffre_entre(self, valeur):
        # Permet de modifier le chiffre dans la grille si ce n'est pas une case fixe
        selection = self.view.grid_widget.selection
        if selection:
            case = self.model.cases.get(selection)
            if case and not case.est_initiale:
                case.valeur = valeur
                self.view.grid_widget.update()