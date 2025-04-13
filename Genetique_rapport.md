# Rapport Partie Genetique

## introduction

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

## Resultat

pour le 12_100 :    970
pour le 13_100 :    1989
pour le 15_100 :    1011

pour le 12_1000 :   4514
pour le 13_1000 :   6513
pour le 15_1000 :   4950

pour le 12_10000 :  45105
pour le 13_10000 :  64077
pour le 15_10000 :  50622

### Pour les petits SAD

pour __"pi-12-100-1000-001.kna"__ :

- classic_solve :
  - nombre d'iteration : 30
  - nombre d'individus : 70
  - mutation_rate : 0.007
  - temps d'exectution : 0.024s
  - fitness moyenne : 927.3 (95.6% de l'optimal)

pour __"pi-13-100-1000-001.kna"__ :

- classic_solve :
  - nombre d'iteration : 30
  - nombre d'individus : 40
  - mutation_rate : 0.006
  - temps d'exectution : 0.031 s
  - fitness moyenne : 1972 (99% de l'optimal) (pour 60 iteration on atteind 1987,5 (99.9% de l'optimal))

pour __"pi-15-100-1000-001.kna"__ :

- classic_solve :
  - nombre d'iteration : 30
  - nombre d'individus : 25
  - mutation_rate : 0.01
  - temps d'exectution : 0.010 s
  - fitness moyenne : 997.7 (98.7% de l'optimal)

### Pour les moyen SAD

pour __"pi-12-1000-1000-001.kna"__ :

- classic_solve :
  - nombre d'iteration : 30
  - nombre d'individus : 85
  - mutation_rate : 0
  - temps d'exectution : 0.034 s
  - fitness moyenne : 4464.91 (98.9% de l'optimal)

pour __"pi-13-1000-1000-001.kna"__ :

- classic_solve :
  - nombre d'iteration : 100
  - nombre d'individus : 200
  - mutation_rate : 0.00055
  - temps d'exectution : 0.460 s
  - fitness moyenne : 6489.6 (99.6% de l'optimal) (avec une population de 400 on atteind 6509.88 (99.95% de l'optimal) mais on passe a 1.192 s d'execution)

pour __"pi-15-1000-1000-001.kna"__ :

- classic_solve :
  - nombre d'iteration : 230
  - nombre d'individus : 60
  - mutation_rate : 0.003
  - temps d'exectution : 0.332 s
  - fitness moyenne : 4838.52 (97.7% de l'optimal)

### Pour les Grand SAD

pour __"pi-12-10000-1000-001.kna"__ :

- classic_solve :
  - nombre d'iteration : 300
  - nombre d'individus : 300
  - mutation_rate : 0
  - temps d'exectution : 4.058 s
  - fitness moyenne : 43299.14 (96.0% de l'optimal)

pour __"pi-13-10000-1000-001.kna"__ :

- classic_solve :
  - nombre d'iteration : 200
  - nombre d'individus : 500
  - mutation_rate : 0.00017
  - temps d'exectution : 8.142
  - fitness moyenne : 53703 (83.8% de l'optimal)

pour __"pi-15-10000-1000-001.kna"__ :

- classic_solve :
  - nombre d'iteration : 100
  - nombre d'individus : 100
  - mutation_rate : 0.0002
  - temps d'exectution : 0.529 s
  - fitness moyenne : 49408.35 (97.6% de l'optimal)

### commentaire

- le classic_solve donne de bon resultat plutot rapidement. Pour avoir d'encore meilleurs resultats (en moyenne) on peut utiliser le new_mutation_solve avec un nombre d'iteration superieur a 45. Il est plus long, mais contrairement au classic_solve qui va stagner a partire de 45 iteration, new_mutation_solve va continué a s'amelioré légerement.
