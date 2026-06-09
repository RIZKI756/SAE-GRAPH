class Case:
    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self.valeur = 0
        self.est_initiale = False
        self.motif = None

class Motif:
    def __init__(self, id_motif: str):
        self.id = id_motif
        self.cases = []

class Grille:
    def __init__(self):
        self.largeur = 0
        self.hauteur = 0
        self.motifs = []
        self.cases = {}