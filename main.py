import sys
import os
from PyQt6.QtWidgets import QApplication
from model import Grille
from view import MainWindow
from controller import GameController

def main():
    # On lance l'app Qt
    app = QApplication(sys.argv)
    
    # On crée les objets de base
    model = Grille()
    view = MainWindow()
    
    # On lie tout ça avec le contrôleur
    controller = GameController(model, view)
    
    # Chargement d'une grille par défaut au démarrage
    chemin_courant = os.path.dirname(os.path.abspath(__file__))
    fichier_derniere_partie = os.path.join(chemin_courant, "derniere_partie.txt")
    
    grille_a_charger = None
    if os.path.exists(fichier_derniere_partie):
        with open(fichier_derniere_partie, 'r', encoding='utf-8') as f:
            chemin = f.read().strip()
        if os.path.exists(chemin):
            grille_a_charger = chemin

    if not grille_a_charger:
        grille_a_charger = os.path.join(chemin_courant, "grille", "grille7.json")
    
    if os.path.exists(grille_a_charger):
        succes = model.charger_json(grille_a_charger)
        if succes:
            view.grid_widget.set_grille(model)
            view.level_label.setText(f"{os.path.basename(grille_a_charger)}")
            view.size_label.setText(f"{model.largeur} × {model.hauteur} ({len(model.motifs)} motifs)")
            controller.timer.start(1000)
            controller._mettre_a_jour_boutons_aide()
            view.statusBar.showMessage(f"Grille de démarrage chargée : {os.path.basename(grille_a_charger)}")
            
            # if os.path.basename(grille_a_charger) == "grille6.json":
            #     from PyQt6.QtWidgets import QMessageBox
            #     QMessageBox.warning(view, "Grille impossible", "Désolé, cette grille ne contient aucune solution")
    else:
        # Tenter de charger un autre fichier si grille7.json n'est pas trouvé
        dossier_exemples = os.path.join(chemin_courant, "grille")
        if os.path.exists(dossier_exemples):
            fichiers = [f for f in os.listdir(dossier_exemples) if f.endswith(".json")]
            if fichiers:
                grille_alternative = os.path.join(dossier_exemples, fichiers[0])
                succes = model.charger_json(grille_alternative)
                if succes:
                    view.grid_widget.set_grille(model)
                    view.level_label.setText(f"{os.path.basename(grille_alternative)}")
                    view.size_label.setText(f"{model.largeur} × {model.hauteur} ({len(model.motifs)} motifs)")
                    controller.timer.start(1000)
                    controller._mettre_a_jour_boutons_aide()
                    view.statusBar.showMessage(f"Grille chargée par défaut : {os.path.basename(grille_alternative)}")
                    
                    # if os.path.basename(grille_alternative) == "grille6.json":
                    #     from PyQt6.QtWidgets import QMessageBox
                    #     QMessageBox.warning(view, "Grille impossible", "Désolé, cette grille ne contient aucune solution")

    # Affichage de la fenêtre principale
    view.show()
    
    # Boucle principale de l'interface
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
