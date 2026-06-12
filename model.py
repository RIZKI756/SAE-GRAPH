from model import Grille, Case

class GrapheGrille:
    # Le graphe pour la grille. Chaque case est un sommet.
    # Les arêtes relient les cases qui peuvent pas avoir la même valeur.
    def __init__(self, grille: Grille):
        self.grille = grille
        self.sommets = list(grille.cases.values())
        self.adj = {case: set() for case in self.sommets}
        self.construire_graphe()

    def ajouter_arete(self, c1: Case, c2: Case):
        # Ajoute une arête entre c1 et c2
        if c1 in self.adj and c2 in self.adj:
            self.adj[c1].add(c2)
            self.adj[c2].add(c1)

    def construire_graphe(self):
        # On construit le graphe :
        # 1. Cases adjacentes reliées
        # 2. Cases du même motif reliées entre elles
        # 1. Contrainte d'adjacence physique
        for case in self.sommets:
            voisins = self.grille.get_voisins(case)
            for voisin in voisins:
                self.ajouter_arete(case, voisin)

        # 2. Contrainte de motif (toutes les cases d'un motif s'excluent mutuellement)
        for motif in self.grille.motifs:
            n = len(motif.cases)
            for i in range(n):
                for j in range(i + 1, n):
                    self.ajouter_arete(motif.cases[i], motif.cases[j])

    def get_voisins_graphe(self, case: Case) -> set[Case]:
        # Renvoie les voisins de la case
        return self.adj.get(case, set())


class SolveurSuguru:
    # L'algo pour résoudre la grille
    def __init__(self, grille: Grille):
        self.grille = grille
        self.graphe = GrapheGrille(grille)

    def resoudre(self) -> bool:
        # Lance la résolution. Renvoie True si c'est bon.
        return self._backtrack()

    def _obtenir_domaines_possibles(self, case: Case) -> list[int]:
        # Trouve les valeurs possibles pour une case (ce qui reste)
        if case.est_initiale:
            return [case.valeur]
            
        n = case.motif.taille
        valeurs_interdites = set()
        
        # Parcourir les voisins dans le graphe de contraintes
        for voisin in self.graphe.get_voisins_graphe(case):
            if voisin.valeur != 0:
                valeurs_interdites.add(voisin.valeur)
                
        # Le domaine est l'ensemble {1..N} privé des valeurs interdites
        domaine = [val for val in range(1, n + 1) if val not in valeurs_interdites]
        return domaine

    def _backtrack(self) -> bool:
        # Fonction qui teste toutes les possibilités
        # Liste des cases qui restent à remplir
        cases_vides = [c for c in self.graphe.sommets if c.valeur == 0]
        
        # Si plus aucune case n'est vide, la grille est résolue !
        if not cases_vides:
            return self.grille.est_complete_et_valide()

        # Backtracking classique séquentiel
        # On prend juste la première case vide qu'on trouve
        case = cases_vides[0]

        # Récupérer les valeurs possibles pour cette case
        domaine = self._obtenir_domaines_possibles(case)
        if not domaine:
            return False  # Pas de couleur valide disponible, échec de cette branche

        # Essayer chaque valeur du domaine
        for val in domaine:
            case.valeur = val
            
            # Appel récursif
            if self._backtrack():
                return True
                
            # Annulation en cas d'échec
            case.valeur = 0

        return False
