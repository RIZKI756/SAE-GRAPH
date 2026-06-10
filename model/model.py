import json
import os

class Case:
    def __init__(self, col: int, row: int, valeur: int = 0, est_initiale: bool = False):
        self.col = col
        self.row = row
        self.valeur = valeur
        self.est_initiale = est_initiale
        self.motif = None

    def __repr__(self):
        return f"Case({self.col}, {self.row}, val={self.valeur})"


class Motif:
    def __init__(self, id_motif: str):
        self.id = id_motif
        self.cases = []

    @property
    def taille(self) -> int:
        return len(self.cases)

    def ajouter_case(self, case: Case):
        self.cases.append(case)
        case.motif = self


class Grille:
    def __init__(self):
        self.largeur = 0
        self.hauteur = 0
        self.motifs = []
        self.cases = {}

    def vider(self):
        self.largeur = 0
        self.hauteur = 0
        self.motifs = []
        self.cases = {}

    def charger_json(self, chemin_fichier: str):
        """Lit le fichier JSON pour construire la grille."""
        self.vider()
        if not os.path.exists(chemin_fichier):
            return

        with open(chemin_fichier, 'r') as f:
            data = json.load(f)

        self.largeur = data["dimensions"]["largeur"]
        self.hauteur = data["dimensions"]["hauteur"]

        # Création des motifs et des cases
        for id_motif, coord_list in data["motifs"].items():
            motif = Motif(id_motif)
            for c, r in coord_list:
                case = Case(c, r)
                self.cases[(c, r)] = case
                motif.ajouter_case(case)
            self.motifs.append(motif)

        # Remplissage des valeurs de départ
        for (c, r), val in data["initiales"].items():
            col, row = int(c), int(r)
            if (col, row) in self.cases:
                self.cases[(col, row)].valeur = val
                self.cases[(col, row)].est_initiale = True