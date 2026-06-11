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
        self.vider()
        if not os.path.exists(chemin_fichier):
            return
        with open(chemin_fichier, 'r') as f:
            data = json.load(f)
        self.largeur = data["dimensions"]["largeur"]
        self.hauteur = data["dimensions"]["hauteur"]

        for id_motif, coord_list in data["motifs"].items():
            motif = Motif(id_motif)
            for c, r in coord_list:
                case = Case(c, r)
                self.cases[(c, r)] = case
                motif.ajouter_case(case)
            self.motifs.append(motif)

        for (c, r), val in data["initiales"].items():
            col, row = int(c), int(r)
            if (col, row) in self.cases:
                self.cases[(col, row)].valeur = val
                self.cases[(col, row)].est_initiale = True

    def get_voisins(self, case: Case) -> list[Case]:
        # check 8 directions autour
        voisons_list = []
        for dc in [-1, 0, 1]:
            for dr in [-1, 0, 1]:
                if dc == 0 and dr == 0:
                    continue
                c_v, r_v = case.col + dc, case.row + dr
                if (c_v, r_v) in self.cases:
                    voisons_list.append(self.cases[(c_v, r_v)])
        return voisons_list

    def est_complete_et_valide(self) -> bool:
        for case in self.cases.values():
            if case.valeur == 0:
                return False
        return len(self.trouver_conflits()) == 0

    def trouver_conflits(self) -> list[tuple[int, int]]:
        # check contraintes suguru
        conflits = set()
        for case in self.cases.values():
            if case.valeur == 0:
                continue
                
            # C1: doublons voisins
            for voisin in self.get_voisins(case):
                if voisin.valeur == case.valeur:
                    conflits.add((case.col, case.row))
                    conflits.add((voisin.col, voisin.row))
            
            # C2: doublons meme motif
            for autre in case.motif.cases:
                if autre != case and autre.valeur == case.valeur:
                    conflits.add((case.col, case.row))
                    conflits.add((autre.col, autre.row))
        return list(conflits)