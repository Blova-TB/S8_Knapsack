# Rapport projet optimisation discret : Probleme du Sac a dos

lien vers les rapports plus detaille pour les deux methodes implementées :

[TABU_rapport](./TABU_rapport.ipynb)
[Genetique_rapport](./Genetique_rapport.md)

Conclusion : Avec les parametres que nous avons choisie, les deux methodes s'execute en un temps relativement equivalent sur les même fichier. Par contre, le TABU 2 a de bien meilleurs resultat en moyenne.

**point faible du génétique** :

- les items dans la liste d'objet disponible dans le sac a dos n'ont aucun lien entre eux. La réalisation de croisement où l'on selection des morceau de solution pert donc une partie de son sens.
- aussi l'almgorithme génétique devrais mieux fonctionner sur des problemes plus "vague" et moins mathematique : Au finale des algorythmes comme le KNAPSACK_DIVIDE_AND_CONQUER_SOLVER de ortool fonctionne infiniment mieux (solution optimal en moins d'une seconde)

**point fort du Tabu** :

- Il trouve très rapidement des solutions convenables.
- La complexité en mémoire est relativement faible
- Trouve de très bon résultats sur tout les sacs (sauf le 15)
- Un certains nombre d'opérations peuvent être optimisées pour éviter de faire du python et aller plus rapidement
