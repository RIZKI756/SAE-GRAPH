================================================================================
                        NOTICE D'UTILISATION - SAE GRAPHES
================================================================================

Titre du Projet : Néonaure
Cadre : SAE Graphes

1. PRÉSENTATION DU PROJET
-------------------------
Ce projet est une application permettant de jouer et de résoudre automatiquement 
des grilles de type Suguru. Ce jeu de logique repose sur des contraintes 
spatiales (les cases voisines ne peuvent pas avoir la même valeur) et de 
groupement (chaque région/motif de taille N doit contenir les chiffres de 1 à N),
ce qui modélise parfaitement un problème de coloration et de graphes.

2. LANCEMENT DE L'APPLICATION
-----------------------------
- Point d'entrée : `main.py`
- Pour lancer le jeu, exécutez simplement la commande `python main.py` depuis 
  la racine du projet.
- L'application utilise l'interface graphique PyQt6.

3. ARCHITECTURE DU CODE (Modèle-Vue-Contrôleur)
-----------------------------------------------
Le projet est organisé de manière modulaire (MVC) pour une lecture facile :
- `model.py` (Modèle) : Contient les données brutes. Gère les Cases, les Motifs 
  (régions) et la Grille globale. S'occupe de valider les règles et trouver les 
  conflits.
- `view.py` (Vue) : Gère uniquement l'affichage (fenêtre, boutons, dessin de 
  la grille) grâce à PyQt6.
- `controller.py` (Contrôleur) : Fait le lien entre les actions de l'utilisateur 
  (clics, saisies) et le Modèle. Gère aussi le chronomètre et les indices.
- `resolver.py` (Solveur) : Contient l'algorithme de résolution automatique 
  (`SolveurSuguru`) capable de terminer la grille si l'utilisateur est bloqué.

4. FONCTIONNALITÉS POUR L'UTILISATEUR (LE JOUEUR)
-------------------------------------------------
- Remplissage interactif : Cliquez sur une case et tapez un chiffre. 
  Les erreurs (conflits avec les voisins ou doublons dans un motif) 
  s'affichent automatiquement en rouge.
- Chargement / Sauvegarde : Les grilles sont stockées au format JSON. Vous 
  pouvez sauvegarder votre partie en cours et la reprendre plus tard.
- Grilles aléatoires : Permet de charger rapidement une autre grille depuis 
  le dossier "grille".
- Indices : Le joueur dispose de 3 indices par partie. Un indice remplit 
  correctement une case vide.
- Résolution automatique : Si vous bloquez trop longtemps ou utilisez tous vos 
  indices, un bouton "Résoudre" apparaît. Il utilise notre algorithme pour 
  trouver la solution finale.
- Vérification : Un bouton permet de s'assurer à tout moment que la grille ne 
  comporte pas d'erreur cachée.

5. RÈGLES DU JEU IMPLÉMENTÉES
-----------------------------
Notre `model.py` vérifie strictement :
1. Règle des motifs : Un motif de taille N doit contenir des valeurs de 1 à N.
2. Règle des voisins : Deux cases voisines (même en diagonale, soit les 8 cases
   autour) ne peuvent JAMAIS contenir le même chiffre.

BAELDEN Tom (TP-B)
MAILLARD Noaïm (TP-D)
JOURNEE Gabriel (TP-D)