import sys
from PyQt6.QtWidgets import QApplication
from model import Grille
from view import MainWindow
from controller import GameController

def main():
    app = QApplication(sys.argv)
    
    # 1. On instancie le modèle (les données de la grille)
    model = Grille()
    
    # 2. On instancie la vue principale (l'IHM)
    view = MainWindow()
    
    # 3. On crée le contrôleur qui connecte le modèle et la vue
    controller = GameController(model, view)
    
    # 4. On affiche la fenêtre et on lance la boucle d'exécution PyQt
    view.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()