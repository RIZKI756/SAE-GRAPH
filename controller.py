import os
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QApplication
from PyQt6.QtCore import QTimer
from model import Grille, Case
from resolver import SolveurSuguru

class GameController:
    # Fait le lien entre la vue et le modèle (MVC vite fait)
    def __init__(self, model: Grille, view):
        self.model = model
        self.view = view
        
        # Chronomètre
        self.temps_ecoule = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._mettre_a_jour_chronometre)
        
        # Aide et Indices
        self.indices_restants = 3
        
        # Connexion des signaux de la vue
        self._connecter_signaux()

    def _connecter_signaux(self):
        # Interactions avec la grille
        self.view.grid_widget.cellule_cliquee.connect(self.on_cellule_cliquee)
        self.view.grid_widget.chiffre_saisi.connect(self.on_chiffre_saisi)
        
        # Boutons de l'interface latérale
        self.view.btn_charger.clicked.connect(self.charger_grille)
        self.view.btn_aleatoire.clicked.connect(self.charger_grille_aleatoire)
        self.view.btn_verifier.clicked.connect(self.view.afficher_regles)
        self.view.btn_indice.clicked.connect(self.donner_indice)
        self.view.btn_resoudre.clicked.connect(self.resoudre_grille)
        self.view.btn_reset.clicked.connect(self.reset_grille)
        
        # Actions du menu supérieur
        self.view.action_charger.triggered.connect(self.charger_grille)
        self.view.action_sauvegarder.triggered.connect(self.sauvegarder_grille)
        self.view.action_quitter.triggered.connect(self.quitter_application)
        
        self.view.action_verifier.triggered.connect(self.verifier_grille)
        self.view.action_indice.triggered.connect(self.donner_indice)
        self.view.action_resoudre.triggered.connect(self.resoudre_grille)
        self.view.action_reset.triggered.connect(self.reset_grille)
        
        self.view.action_regles.triggered.connect(self.view.afficher_regles)
        self.view.action_a_propos.triggered.connect(self.view.afficher_a_propos)

    # --- Actions de jeu ---

    def charger_grille(self):
        # Pop-up pour charger le JSON
        dossier_defaut = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grille")
        if not os.path.exists(dossier_defaut):
            dossier_defaut = os.path.expanduser("~")

        fichier, _ = QFileDialog.getOpenFileName(
            self.view, 
            "Charger une grille Néonaure", 
            dossier_defaut, 
            "Fichiers JSON (*.json)"
        )
        
        if fichier:
            succes = self.model.charger_json(fichier)
            if succes:
                # Mettre à jour l'affichage
                self.view.grid_widget.set_grille(self.model)
                self.view.level_label.setText(f"📄 {os.path.basename(fichier)}")
                self.view.size_label.setText(f"📐 {self.model.largeur} × {self.model.hauteur} ({len(self.model.motifs)} motifs)")
                
                # Réinitialiser les indices et le chronomètre
                self.indices_restants = 3
                self.temps_ecoule = 0
                self.view.timer_label.setText("⏱️ 00:00")
                self.timer.start(1000)
                
                self._mettre_a_jour_boutons_aide()
                self.view.statusBar.showMessage(f"Grille chargée : {os.path.basename(fichier)}")
            else:
                QMessageBox.critical(self.view, "Erreur de chargement", "Impossible de charger ou d'interpréter le fichier JSON.")

    def sauvegarder_grille(self):
        # Pop-up pour sauvegarder
        if self.model.largeur == 0:
            QMessageBox.warning(self.view, "Sauvegarde impossible", "Aucune grille n'est chargée actuellement.")
            return

        fichier, _ = QFileDialog.getSaveFileName(
            self.view, 
            "Sauvegarder la partie", 
            "", 
            "Fichiers JSON (*.json)"
        )
        
        if fichier:
            # S'assurer de l'extension .json
            if not fichier.endswith(".json"):
                fichier += ".json"
            succes = self.model.sauvegarder_json(fichier)
            if succes:
                self.view.statusBar.showMessage(f"Partie sauvegardée sous {os.path.basename(fichier)}")
            else:
                QMessageBox.critical(self.view, "Erreur de sauvegarde", "Impossible d'écrire dans le fichier.")

    def on_cellule_cliquee(self, col: int, row: int):
        # Quand on clique sur une case
        case = self.model.get_case(col, row)
        if case and case.motif:
            nom_motif = case.motif.id
            taille_motif = case.motif.taille
            type_case = "Initiale" if case.est_initiale else "Joueur"
            self.view.statusBar.showMessage(
                f"Case ({col + 1}, {row + 1}) | Type : {type_case} | Motif : {nom_motif} (taille {taille_motif})"
            )

    def on_chiffre_saisi(self, valeur: int):
        # Quand on tape un chiffre au clavier
        selection = self.view.grid_widget.selection
        if not selection:
            return
            
        col, row = selection
        case = self.model.get_case(col, row)
        if not case or case.est_initiale:
            return

        # Modifier la valeur dans le modèle
        case.valeur = valeur
        
        # Lancer la détection de conflits (coloration des erreurs en rouge)
        conflits = self.model.trouver_conflits()
        self.view.grid_widget.set_conflits(conflits)
        self.view.grid_widget.update()
        
        if valeur == 0:
            self.view.statusBar.showMessage(f"Case ({col + 1}, {row + 1}) effacée.")
        else:
            self.view.statusBar.showMessage(f"Chiffre {valeur} placé en case ({col + 1}, {row + 1}).")

        # Vérifier si la grille est entièrement et correctement complétée
        if self.model.est_complete_et_valide():
            self.timer.stop()
            self.view.statusBar.showMessage("Félicitations ! Vous avez résolu la grille.")
            QMessageBox.information(
                self.view, 
                "Victoire !", 
                f"Bravo ! Vous avez terminé la grille avec succès en {self._formater_temps(self.temps_ecoule)}."
            )

    def verifier_grille(self):
        # Bouton de vérification
        if self.model.largeur == 0:
            QMessageBox.warning(self.view, "Vérification impossible", "Aucune grille n'est chargée.")
            return

        conflits = self.model.trouver_conflits()
        self.view.grid_widget.set_conflits(conflits)
        self.view.grid_widget.update()

        if conflits:
            QMessageBox.warning(
                self.view, 
                "Contraintes violées", 
                f"Attention, il y a des erreurs dans votre grille ({len(conflits)} cellules en rouge).\n"
                "Rappel : pas de doublons dans un même motif et pas de chiffres identiques côte à côte (y compris en diagonale)."
            )
        elif self.model.est_complete_et_valide():
            self.timer.stop()
            QMessageBox.information(self.view, "Grille résolue", "Félicitations, la grille est complète et correcte !")
        else:
            QMessageBox.information(
                self.view, 
                "Grille valide", 
                "Aucune erreur n'a été détectée pour le moment. Continuez !"
            )

    def resoudre_grille(self):
        # Bouton pour que l'ordi résolve tout seul
        if self.model.largeur == 0:
            QMessageBox.warning(self.view, "Résolution impossible", "Aucune grille n'est chargée.")
            return

        # 1. Sauvegarde des saisies utilisateur actuelles au cas où
        backup_vals = {coords: case.valeur for coords, case in self.model.cases.items() if not case.est_initiale}
        
        # 2. Tenter de résoudre depuis l'état actuel de la grille
        solveur = SolveurSuguru(self.model)
        succes = solveur.resoudre()
        
        if not succes:
            # Restaurer les saisies utilisateur
            for coords, val in backup_vals.items():
                self.model.get_case(*coords).valeur = val
                
            # Proposer de résoudre à partir de la grille initiale
            reponse = QMessageBox.question(
                self.view, 
                "Conflit de saisie",
                "Vos saisies actuelles rendent la grille impossible à résoudre.\n"
                "Voulez-vous réinitialiser la grille et la résoudre automatiquement depuis le début ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reponse == QMessageBox.StandardButton.Yes:
                self.model.reset()
                solveur = SolveurSuguru(self.model)
                if solveur.resoudre():
                    self.timer.stop()
                    self.view.grid_widget.set_conflits([])
                    self.view.grid_widget.update()
                    self.view.statusBar.showMessage("Grille résolue automatiquement !")
                else:
                    QMessageBox.critical(self.view, "Échec", "Cette grille n'a aucune solution possible.")
        else:
            self.timer.stop()
            self.view.grid_widget.set_conflits([])
            self.view.grid_widget.update()
            self.view.statusBar.showMessage("Grille résolue automatiquement !")

    def reset_grille(self):
        # Bouton pour recommencer
        if self.model.largeur == 0:
            return
            
        reponse = QMessageBox.question(
            self.view, 
            "Réinitialiser", 
            "Voulez-vous effacer toutes vos réponses et recommencer cette grille ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reponse == QMessageBox.StandardButton.Yes:
            self.model.reset()
            self.view.grid_widget.set_conflits([])
            self.view.grid_widget.update()
            self.temps_ecoule = 0
            self.view.timer_label.setText("⏱️ 00:00")
            self.timer.start(1000)
            self.indices_restants = 3
            self._mettre_a_jour_boutons_aide()
            self.view.statusBar.showMessage("Grille réinitialisée.")

    def donner_indice(self):
        # Bouton Indice : donne un coup de pouce (limité à 3)
        if self.model.largeur == 0:
            QMessageBox.warning(self.view, "Indice impossible", "Aucune grille n'est chargée.")
            return

        if self.indices_restants <= 0:
            QMessageBox.warning(self.view, "Indices épuisés", "Vous avez épuisé vos 3 indices pour cette partie.")
            return

        # Obtenir la solution en résolvant une copie de la grille
        backup_vals = {coords: case.valeur for coords, case in self.model.cases.items()}
        self.model.reset()
        solveur = SolveurSuguru(self.model)
        succes = solveur.resoudre()
        
        if succes:
            solution = {coords: case.valeur for coords, case in self.model.cases.items()}
            # Restaurer
            for coords, val in backup_vals.items():
                self.model.get_case(*coords).valeur = val

            # On prend juste la première case vide et on donne la réponse
            cases_vides = [c for c in self.model.cases.values() if c.valeur == 0]
            if not cases_vides:
                QMessageBox.information(self.view, "Indice", "La grille est déjà remplie !")
                return

            case_indice = cases_vides[0]
            coords = (case_indice.col, case_indice.row)
            case_indice.valeur = solution[coords]
            
            self.indices_restants -= 1
            self._mettre_a_jour_boutons_aide()
            
            self.view.grid_widget.set_conflits([])
            self.view.grid_widget.update()
            
            QMessageBox.information(
                self.view,
                "Indice révélé",
                f"On a mis la bonne valeur en colonne {case_indice.col + 1}, ligne {case_indice.row + 1}."
            )
            
            # Vérifier victoire
            if self.model.est_complete_et_valide():
                self.timer.stop()
                self.view.statusBar.showMessage("Félicitations ! Vous avez résolu la grille.")
                QMessageBox.information(
                    self.view, 
                    "Victoire !", 
                    f"Bravo ! Vous avez terminé la grille avec succès en {self._formater_temps(self.temps_ecoule)}."
                )
        else:
            # Restaurer
            for coords, val in backup_vals.items():
                self.model.get_case(*coords).valeur = val
            QMessageBox.critical(
                self.view, 
                "Indice impossible", 
                "La grille n'a pas de solution."
            )

    # --- Chronomètre ---

    def _mettre_a_jour_chronometre(self):
        self.temps_ecoule += 1
        self.view.timer_label.setText(f"⏱️ {self._formater_temps(self.temps_ecoule)}")
        self._mettre_a_jour_boutons_aide()

    def charger_grille_aleatoire(self):
        # Charge une grille au pif
        dossier_exemples = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grille")
        if not os.path.exists(dossier_exemples):
            self.view.statusBar.showMessage("Dossier grille introuvable.")
            return

        fichiers = [f for f in os.listdir(dossier_exemples) if f.endswith(".json")]
        # On exclut grille6.json car elle est insoluble d'origine
        fichiers_jouables = [f for f in fichiers if f != "grille6.json"]
        
        if not fichiers_jouables:
            fichiers_jouables = fichiers

        if not fichiers_jouables:
            self.view.statusBar.showMessage("Aucune grille trouvée.")
            return

        import random
        choix = random.choice(fichiers_jouables)
        fichier = os.path.join(dossier_exemples, choix)

        succes = self.model.charger_json(fichier)
        if succes:
            self.view.grid_widget.set_grille(self.model)
            self.view.level_label.setText(f"📄 {choix}")
            self.view.size_label.setText(f"📐 {self.model.largeur} × {self.model.hauteur} ({len(self.model.motifs)} motifs)")
            
            # Réinitialiser les indices et le chronomètre
            self.indices_restants = 3
            self.temps_ecoule = 0
            self.view.timer_label.setText("⏱️ 00:00")
            self.timer.start(1000)
            
            self._mettre_a_jour_boutons_aide()
            self.view.statusBar.showMessage(f"Grille aléatoire chargée : {choix}")
        else:
            self.view.statusBar.showMessage("Erreur lors du chargement de la grille.")

    def _mettre_a_jour_boutons_aide(self):
        # Met à jour les boutons d'indices et de résolution
        self.view.btn_indice.setText(f"Obtenir un Indice ({self.indices_restants} restants)")
        self.view.action_indice.setText(f"Révéler un indice ({self.indices_restants} restants)")
        
        if self.indices_restants <= 0:
            self.view.btn_indice.setEnabled(False)
            self.view.action_indice.setEnabled(False)
        else:
            self.view.btn_indice.setEnabled(True)
            self.view.action_indice.setEnabled(True)

        # Afficher "Résoudre Directement" si l'utilisateur a utilisé au moins 2 indices (donc reste <= 1)
        # OU si le temps de jeu a dépassé 10 minutes (600 secondes)
        devoiler_resoudre = (self.indices_restants <= 1) or (self.temps_ecoule >= 600)
        self.view.btn_resoudre.setVisible(devoiler_resoudre)
        self.view.action_resoudre.setEnabled(devoiler_resoudre)

    def _formater_temps(self, secondes: int) -> str:
        minutes = secondes // 60
        sec = secondes % 60
        return f"{minutes:02d}:{sec:02d}"

    def quitter_application(self):
        QApplication.quit()