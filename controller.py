from model import Grille
from view import MainWindow

class GameController:
    def __init__(self, model: Grille, view: MainWindow):
        self.model = model
        self.view = view
        # Les connexions entre signaux de la vue et actions du modèle seront ajoutées ici