import sys
from PyQt6.QtWidgets import QApplication
from model import Grille
from view import MainWindow
from controller import GameController

def main():
    app = QApplication(sys.argv)
    
    model = Grille()
    
    view = MainWindow()
    
    controller = GameController(model, view)
    
    view.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()