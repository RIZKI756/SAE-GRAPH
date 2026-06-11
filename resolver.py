from model import Grille, Case

class GrapheGrille:
    # representation contraintes par graphe
    def __init__(self, grille: Grille):
        self.grille = grille
        self.sommets = list(grille.cases.values())
        self.adj = {case: set() for case in self.sommets}
        self.construire_graphe()

    def ajouter_arete(self, c1: Case, c2: Case):
        if c1 in self.adj and c2 in self.adj:
            self.adj[c1].add(c2)
            self.adj[c2].add(c1)

    def construir_graphe(self):
        # C1: aretes voisins physiques
        for case in self.sommets:
            voisins = self.grille.get_voisins(case)
            for voisin in voisins:
                self.ajouter_arete(case, voisin)

        # C2: aretes meme motif
        for motif in self.grille.motifs:
            n = len(motif.cases)
            for i in range(n):
                for j in range(i + 1, n):
                    self.ajouter_arete(motif.cases[i], motif.cases[j])

    def get_voisins_graphe(self, case: Case) -> set[Case]:
        return self.adj.get(case, set())


class SolveurSuguru:
    def __init__(self, grille: Grille):
        self.grille = grille
        self.graphe = GrapheGrille(grille)

    def resoudre(self) -> bool:
        return self._backtrack()

    def _obtenir_domaines_possibles(self, case: Case) -> list[int]:
        if case.est_initiale:
            return [case.valeur]
            
        n = case.motif.taille
        valeurs_interdites = set()
        
        for voisin in self.graphe.get_voisins_graphe(case):
            if voisin.valeur != 0:
                valeurs_interdites.add(voisin.valeur)
                
        return [val for val in range(1, n + 1) if val not in valeurs_interdites]

    def _backtrack(self) -> bool:
        # bruteforce / backtrack seq classique
        cases_vides = [c for c in self.graphe.sommets if c.valeur == 0]
        
        if not cases_vides:
            return self.grille.est_complete_et_valide()

        case = cases_vides[0]
        domaine = self._obtenir_domaines_possibles(case)

        for val in domaine:
            case.valeur = val
            if self._backtrack():
                return True
            case.valeur = 0 # reset / backtrack

        return False