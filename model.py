import json
import os

class Case:
    # Une case de la grille
    def __init__(self, col: int, row: int, valeur: int = 0, est_initiale: bool = False):
        self.col = col
        self.row = row
        self.valeur = valeur
        self.est_initiale = est_initiale
        self.motif = None  # Référence vers l'objet Motif contenant cette case

    def __repr__(self):
        return f"Case({self.col}, {self.row}, val={self.valeur}, init={self.est_initiale})"


class Motif:
    # Un motif (les zones de couleur)
    def __init__(self, id_motif: str):
        self.id = id_motif
        self.cases = []

    @property
    def taille(self) -> int:
        return len(self.cases)

    def ajouter_case(self, case: Case):
        self.cases.append(case)
        case.motif = self

    def verifier_validite_partielle(self) -> bool:
        # Regarde vite fait si y'a pas de doublons
        valeurs = [c.valeur for c in self.cases if c.valeur != 0]
        # Vérification des doublons
        if len(valeurs) != len(set(valeurs)):
            return False
        # Vérification que les valeurs ne dépassent pas la taille N du motif
        for val in valeurs:
            if val < 1 or val > self.taille:
                return False
        return True

    def verifier_complet(self) -> bool:
        # Vérifie si le motif est fini et bon
        valeurs = [c.valeur for c in self.cases]
        if len(valeurs) != self.taille:
            return False
        return sorted(valeurs) == list(range(1, self.taille + 1))

    def __repr__(self):
        return f"Motif(id={self.id}, taille={self.taille})"


class Grille:
    # La grosse grille qui contient tout
    def __init__(self):
        self.largeur = 0
        self.hauteur = 0
        self.motifs = []  # Liste des objets Motif
        self.cases = {}   # Dictionnaire {(col, row): Case}

    def vider(self):
        # On vide tout
        self.largeur = 0
        self.hauteur = 0
        self.motifs = []
        self.cases = {}

    def charger_json(self, chemin_fichier: str) -> bool:
        # Charge le fichier JSON
        if not os.path.exists(chemin_fichier):
            return False

        try:
            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.vider()
            
            # Étape 1 : Déterminer la taille de la grille
            max_col = 0
            max_row = 0
            for motif_id, cellules in data.items():
                for cellule in cellules:
                    x, y, val = cellule
                    if x > max_col:
                        max_col = x
                    if y > max_row:
                        max_row = y
            
            self.largeur = max_col + 1
            self.hauteur = max_row + 1

            # Étape 2 : Créer les motifs et les cases
            for motif_id, cellules in data.items():
                motif = Motif(motif_id)
                self.motifs.append(motif)
                
                for cellule in cellules:
                    x, y, val = cellule
                    # val > 0 signifie que c'est une case pré-remplie
                    est_initiale = (val > 0)
                    case = Case(x, y, val, est_initiale)
                    self.cases[(x, y)] = case
                    motif.ajouter_case(case)
            
            return True
        except Exception as e:
            print(f"Erreur lors du chargement de la grille : {e}")
            return False

    def sauvegarder_json(self, chemin_fichier: str) -> bool:
        # Sauvegarde en JSON
        try:
            data = {}
            for motif in self.motifs:
                data[motif.id] = []
                for case in motif.cases:
                    data[motif.id].append([case.col, case.row, case.valeur])

            with open(chemin_fichier, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la grille : {e}")
            return False

    def get_case(self, col: int, row: int) -> Case:
        # Chopper une case
        return self.cases.get((col, row), None)

    def get_voisins(self, case: Case) -> list[Case]:
        # Donne les 8 voisins de la case
        voisins = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = case.col + dx, case.row + dy
                voisin = self.get_case(nx, ny)
                if voisin is not None:
                    voisins.append(voisin)
        return voisins

    def est_valeur_valide_pour_case(self, case: Case, val: int) -> bool:
        # Est-ce qu'on a le droit de mettre ce chiffre là ?
        if val == 0:
            return True  # 0 correspond à vider la case, toujours autorisé

        # Règle 1 : La valeur ne doit pas dépasser la taille du motif
        if case.motif and (val < 1 or val > case.motif.taille):
            return False

        # Règle 2 : Unicité dans le motif (hors la case elle-même)
        if case.motif:
            for c in case.motif.cases:
                if c != case and c.valeur == val:
                    return False

        # Règle 3 : Unicité parmi les voisins (les 8 cases adjacentes)
        voisins = self.get_voisins(case)
        for v in voisins:
            if v.valeur == val:
                return False

        return True

    def trouver_conflits(self) -> list[Case]:
        # Trouve les erreurs/conflits
        conflits = set()
        
        for case in self.cases.values():
            if case.valeur == 0:
                continue
            
            # Vérifier motif
            if case.motif:
                # Si valeur invalide pour la taille
                if case.valeur > case.motif.taille:
                    conflits.add(case)
                # Si doublon dans le motif
                for c in case.motif.cases:
                    if c != case and c.valeur == case.valeur:
                        conflits.add(case)
                        conflits.add(c)
                        
            # Vérifier voisins
            voisins = self.get_voisins(case)
            for v in voisins:
                if v.valeur == case.valeur:
                    conflits.add(case)
                    conflits.add(v)
                    
        return list(conflits)

    def reset(self):
        # Remet la grille à zéro
        for case in self.cases.values():
            if not case.est_initiale:
                case.valeur = 0

    def est_complete_et_valide(self) -> bool:
        # C'est gagné ?
        # 1. Vérifier que toutes les cases sont remplies
        for case in self.cases.values():
            if case.valeur == 0:
                return False
                
        # 2. Vérifier que tous les motifs sont complets (chiffres 1..N)
        for motif in self.motifs:
            if not motif.verifier_complet():
                return False
                
        # 3. Vérifier les voisins (aucune case voisine n'a la même valeur)
        for case in self.cases.values():
            voisins = self.get_voisins(case)
            for v in voisins:
                if v.valeur == case.valeur:
                    return False
                    
        return True
