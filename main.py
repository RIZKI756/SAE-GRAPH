import sys
from PyQt6.QtWidgets import QApplication
from view import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Initialisation de la vue seule
    view = MainWindow()
    view.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()