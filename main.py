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
    grille_defaut = os.path.join(chemin_courant, "grille", "grille7.json")
    
    if os.path.exists(grille_defaut):
        succes = model.charger_json(grille_defaut)
        if succes:
            view.grid_widget.set_grille(model)
            view.level_label.setText(f"📄 {os.path.basename(grille_defaut)}")
            view.size_label.setText(f"📐 {model.largeur} × {model.hauteur} ({len(model.motifs)} motifs)")
            controller.timer.start(1000)
            controller._mettre_a_jour_boutons_aide()
            view.statusBar.showMessage(f"Grille de démarrage chargée : {os.path.basename(grille_defaut)}")
    else:
        # Tenter de charger un autre fichier si grille7.json n'est pas trouvé
        dossier_exemples = os.path.join(chemin_courant, "grille")
        if os.path.exists(dossier_exemples):
            fichiers = [f for f in os.listdir(dossier_exemples) if f.endswith(".json")]
            fichiers_solubles = [f for f in fichiers if f != "grille6.json"]
            if not fichiers_solubles:
                fichiers_solubles = fichiers
            if fichiers_solubles:
                grille_alternative = os.path.join(dossier_exemples, fichiers_solubles[0])
                succes = model.charger_json(grille_alternative)
                if succes:
                    view.grid_widget.set_grille(model)
                    view.level_label.setText(f"📄 {os.path.basename(grille_alternative)}")
                    view.size_label.setText(f"📐 {model.largeur} × {model.hauteur} ({len(model.motifs)} motifs)")
                    controller.timer.start(1000)
                    controller._mettre_a_jour_boutons_aide()
                    view.statusBar.showMessage(f"Grille chargée par défaut : {os.path.basename(grille_alternative)}")

    # Affichage de la fenêtre principale
    view.show()
    
    # Boucle principale de l'interface
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
