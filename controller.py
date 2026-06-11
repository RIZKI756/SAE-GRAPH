import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QApplication
from PyQt6.QtCore import QTimer
from model import Grille, Case
from resolver import SolveurSuguru

class GameController:
    def __init__(self, model: Grille, view):
        self.model = model
        self.view = view
        
        self.temps_ecoule = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._mettre_a_jour_chronometre)
        
        self.indices_restants = 3
        self._connecter_signaux()

    def _connecter_signaux(self):
        self.view.grid_widget.cellule_cliquee.connect(self.on_cellule_cliquee)
        self.view.grid_widget.chiffre_saisi.connect(self.on_chiffre_saisi)
        
        self.view.btn_charger.clicked.connect(self.charger_grille)
        self.view.btn_aleatoire.clicked.connect(self.charger_grille_aleatoire)
        self.view.btn_verifier.clicked.connect(self.view.afficher_regles)
        self.view.btn_indice.clicked.connect(self.donner_indice)
        self.view.btn_resoudre.clicked.connect(self.resoudre_grille)
        self.view.btn_reset.clicked.connect(self.reset_grille)
        
        # self.view.action_charger.triggered.connect(self.charger_grille)
        # self.view.action_sauvegarder.triggered.connect(self.sauvegarder_grille)
        # self.view.action_quitter.triggered.connect(self.quitter_application)
        
        # self.view.action_verifier.triggered.connect(self.verifier_grille)
        # self.view.action_indice.triggered.connect(self.donner_indice)
        # self.view.action_resoudre.triggered.connect(self.resoudre_grille)
        # self.view.action_reset.triggered.connect(self.reset_grille)
        
        # self.view.action_regles.triggered.connect(self.view.afficher_regles)
        # self.view.action_a_propos.triggered.connect(self.view.afficher_a_propos)

    def charger_grille(self):
        dossier_defaut = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grille")
        if not os.path.exists(dossier_defaut):
            dossier_defaut = os.path.expanduser("~")

        fichier, _ = QFileDialog.getOpenFileName(
            self.view, "Charger une grille Néonaure", dossier_defaut, "Fichiers JSON (*.json)"
        )
        
        if fichier:
            succes = self.model.charger_json(fichier)
            if succes:
                self.view.grid_widget.set_grille(self.model)
                self.view.level_label.setText(f"📄 {os.path.basename(fichier)}")
                self.view.size_label.setText(f"📐 {self.model.largeur} × {self.model.hauteur} ({len(self.model.motifs)} motifs)")
                
                self.indices_restants = 3
                self.temps_ecoule = 0
                self.view.timer_label.setText("⏱️ 00:00")
                self.timer.start(1000)
                
                self._mettre_a_jour_boutons_aide()
                self.view.statusBar.showMessage(f"Grille chargée : {os.path.basename(fichier)}")
            else:
                QMessageBox.critical(self.view, "Erreur", "Impossible de charger le fichier JSON.")

    def sauvegarder_grille(self):
        if self.model.largeur == 0:
            QMessageBox.warning(self.view, "Sauvegarde impossible", "Aucune grille chargée.")
            return
        fichier, _ = QFileDialog.getSaveFileName(self.view, "Sauvegarder la partie", "", "Fichiers JSON (*.json)")
        if fichier:
            if not fichier.endswith(".json"): fichier += ".json"
            if self.model.sauvegarder_json(fichier):
                self.view.statusBar.showMessage(f"Partie sauvegardée : {os.path.basename(fichier)}")

    def on_cellule_cliquee(self, col: int, row: int):
        case = self.model.get_case(col, row)
        if case and case.motif:
            type_case = "Initiale" if case.est_initiale else "Joueur"
            self.view.statusBar.showMessage(f"Case ({col + 1}, {row + 1}) | {type_case} | Motif : {case.motif.id}")

    def on_chiffre_saisi(self, valeur: int):
        selection = self.view.grid_widget.selection
        if not selection: return
        col, row = selection
        case = self.model.get_case(col, row)
        if not case or case.est_initiale: return

        case.valeur = valeur
        conflits = self.model.trouver_conflits()
        self.view.grid_widget.set_conflits(conflits)
        self.view.grid_widget.update()
        
        if self.model.est_complete_et_valide():
            self.timer.stop()
            QMessageBox.information(self.view, "Victoire !", f"Bravo ! Gagné en {self._formater_temps(self.temps_ecoule)}.")

    def verifier_grille(self):
        if self.model.largeur == 0: return
        conflits = self.model.trouver_conflit()
        self.view.grid_widget.set_conflits(conflits)
        self.view.grid_widget.update()
        if conflits:
            QMessageBox.warning(self.view, "Erreurs", f"Attention, il y a {len(conflits)} cellules en anomalie (rouge).")
        elif self.model.est_complete_et_valide():
            self.timer.stop()
            QMessageBox.information(self.view, "Gagné", "La grille est complète et correcte !")
        else:
            QMessageBox.information(self.view, "Valide", "Aucune erreur détectée. Continuez !")

    def resoudre_grille(self):
        if self.model.largeur == 0: return
        backup_vals = {coords: case.valeur for coords, case in self.model.cases.items() if not case.est_initiale}
        solveur = SolveurSuguru(self.model)
        if not solveur.resoudre():
            for coords, val in backup_vals.items(): self.model.get_case(*coords).valeur = val
            reponse = QMessageBox.question(self.view, "Insoluble", "Vos saisies bloquent le solveur. Reset et résoudre depuis le début ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reponse == QMessageBox.StandardButton.Yes:
                self.model.reset()
                solveur = SolveurSuguru(self.model)
                if solveur.resoudre():
                    self.timer.stop()
                    self.view.grid_widget.set_conflits([])
                    self.view.grid_widget.update()
        else:
            self.timer.stop()
            self.view.grid_widget.set_conflits([])
            self.view.grid_widget.update()

    def reset_grille(self):
        if self.model.largeur == 0: return
        reponse = QMessageBox.question(self.view, "Reset", "Voulez-vous tout effacer ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reponse == QMessageBox.StandardButton.Yes:
            self.model.reset()
            self.view.grid_widget.set_conflits([])
            self.view.grid_widget.update()
            self.temps_ecoule = 0
            self.view.timer_label.setText("⏱️ 00:00")
            self.timer.start(1000)
            self.indices_restants = 3
            self._mettre_a_jour_boutons_aide()

    def donner_indice(self):
        if self.model.largeur == 0 or self.indices_restants <= 0: return
        backup_vals = {coords: case.valeur for coords, case in self.model.cases.items()}
        self.model.reset()
        solveur = SolveurSuguru(self.model)
        if solveur.resoudre():
            solution = {coords: case.valeur for coords, case in self.model.cases.items()}
            for coords, val in backup_vals.items(): self.model.get_case(*coords).valeur = val
            cases_vides = [c for c in self.model.cases.values() if c.valeur == 0]
            if not cases_vides: return
            
            case_indice = cases_vides[0]
            case_indice.valeur = solution[(case_indice.col, case_indice.row)]
            self.indices_restants -= 1
            self._mettre_a_jour_boutons_aide()
            self.view.grid_widget.update()
            
            if self.model.est_complete_et_valide(): self.timer.stop()
        else:
            for coords, val in backup_vals.items(): self.model.get_case(*coords).valeur = val

    def _mettre_a_jour_chronometre(self):
        self.temps_ecoule += 1
        self.view.timer_label.setText(f"⏱️ {self._formater_temps(self.temps_ecoule)}")
        self._mettre_a_jour_boutons_aide()

    def charger_grille_aleatoire(self):
        dossier = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grille")
        if not os.path.exists(dossier): return
        fichiers = [f for f in os.listdir(dossier) if f.endswith(".json") and f != "grille6.json"]
        if fichiers:
            import random
            choix = random.choice(fichiers)
            if self.model.charger_json(os.path.join(dossier, choix)):
                self.view.grid_widget.set_grille(self.model)
                self.view.level_label.setText(f"📄 {choix}")
                self.indices_restants = 3
                self.temps_ecoule = 0
                self.timer.start(1000)
                self._mettre_a_jour_boutons_aide()

    def _mettre_a_jour_boutons_aide(self):
        self.view.btn_indice.setText(f"Obtenir un Indice ({self.indices_restants} restants)")
        # self.view.action_indice.setText(f"Révéler un indice ({self.indices_restants} restants)")
        self.view.btn_indice.setEnabled(self.indices_restants > 0)
        # self.view.action_indice.setEnabled(self.indices_restants > 0)
        devoiler = (self.indices_restants <= 1) or (self.temps_ecoule >= 600)
        self.view.btn_resoudre.setVisible(devoiler)
        # self.view.action_resoudre.setEnabled(devoiler)

    def _formater_temps(self, secondes: int) -> str:
        return f"{secondes // 60:02d}:{secondes % 60:02d}"

    def quitter_application(self):
        QApplication.quit()
