# Genetique

## premiere evolution du code

Liste des different parametre a faire varrier :

- nombre d'iteration avant d'arreter le programme
- nombre d'individu dans la population
- chance de mutation par bit des solutions
- type de la methode de resolution:
  - classic
  - mutation equitable

## historique des ameliorations du code

une premiere version du code utilisait une initialisation du sac a dos completement aléatoire : chaque objet avait une chance sur 2 de se retrouver dans une solution.
__probleme__ : le poid des solutions de la premiere generation était donc bien trop elevée puissqu'elle contenait en moyenne la moitier des elements possible.
Le programe génetique n'arrivait alors pas a revenir sur des solutions réalisable puisque la fitness des solutions calculées etaient toute de 0.
__solution__ : nous avons donc remplis le sac a dos avec des objets aléatoire jusqu'a ce que le poid des objet selectionné depasse le poid max du SAD.

-

-

-

Pour identifier les parametres permetant d'obtenire de bon resultat dans un temps résonnable, nous avons calculé la fitness moyenne du meilleurs resultat pour des parametre donné. Nous avons ensuite fait varier 1 ou 2 parametres ce qui nous a alors permis de generer des graphs (courbe pour 1 parametre et heatmap pour 2 parametres)

-

-

pour __"pi-12-100-1000-001.kna"__ :

- classic_solve :
  - nombre d'iteration :
  - nombre d'individus :
  - mutation_rate :

- new_mutation_solve :
  - nombre d'iteration :
  - nombre d'individus :
  - mutation_rate :

commentaire :

- TODO

pour __"pi-13-100-1000-001.kna"__ :

- classic_solve :
  - nombre d'iteration : 30-40
  - nombre d'individus : 50-60
  - mutation_rate : 0.0025

- new_mutation_solve :
  - nombre d'iteration : 50-60
  - nombre d'individus : 35-40
  - mutation_rate : 0.005

commentaire :

- le classic_solve donne de bon resultat plutot rapidement. Pour avoir d'encore meilleurs resultats (en moyenne) on peut utiliser le new_mutation_solve avec un nombre d'iteration superieur a 45. Il est plus long, mais contrairement au classic_solve qui va stagner a partire de 45 iteration, new_mutation_solve va continué a s'amelioré légerement.

pour __"pi-15-100-1000-001.kna"__ :

- classic_solve :
  - nombre d'iteration :
  - nombre d'individus :
  - mutation_rate :

- new_mutation_solve :
  - nombre d'iteration :
  - nombre d'individus :
  - mutation_rate :

commentaire :

- TODO
