# Rapport Partie Genetique

## introduction

### fonctionnement de l'algorithme

Notre algorithme fonctionne en 3 etapes :

reproduction : on réalise un roulette biaisé selon la fitness modifier pour obtenir une nouvelle population.
croisement : on croise les individues deux par deux selon un `cut_index` tiré aléatoirement pour obtenir une nouvelle population.
mutation : on modifie légèrement aleatoirement plusieurs solutions.

On repete ces 3 etapes un certain nombre de fois.

### Liste des different parametre a faire varier

- nombre d'iteration avant d'arreter le programme
- nombre d'individu dans la population de solutions
- chance de mutation par bit des solutions

## Plusieurs ameliorations

### Intialisation

__contexte__ : Une premiere version du code utilisait une initialisation du sac a dos completement aléatoire : chaque objet avait une chance sur 2 de se retrouver dans une solution.
__probleme__ : le poid des solutions de la premiere generation était donc bien trop elevée puissqu'elle contenait en moyenne la moitier des elements possible.
Le programe génetique n'arrivait alors pas a revenir sur des solutions réalisable puisque la fitness des solutions calculées etaient toute de 0.
__solution__ : nous avons donc remplis le sac a dos avec des objets aléatoire jusqu'a ce que le poid des objets selectionnés depasse le poid max du SAD. 

### Deroulement

__contexte__ : la fitness du sac a dos se calcule en sommant les fitness des objets qu'il contient mais il ne faut pas que le poid dépasse le poid maximum autorisé.
__probleme__ : que faire si une solution dépasse le poid max ?
__solution__ : Si la solution permet tout de meme de s'aprocher d'un bon resultat il serait dommage de lui atribué un fitness de 0. Nous avons donc choisie de calculer une deuxieme fitness (`calc_real_fitness()`) en fonction du poid et de la fitness : `max(fitness - 3 * max(weight - self.sad_capacity,0),1)`
Les solutions ayant une bonne fitness mais depassant de peu la capacité on donc pu être conservée. Mais pas pris en compte dans les meilleurs solution obtenu car invalide.

### Optimisation temporel

__contexte__ : la fonction réalisant les mutations sur la population choisisais de faire muter ou non chaque bit de chaque solution
__probleme__ : la fonction devais donc parcourire tout les bits de toute les solution en tirant un chiffre aleatoire a chaque fois. Sur les fichiers a 10 000 objets avec une population de 100 individus cela representait 1 000 000 tirages de nombres aleatoires a chaque iterations pour seulement un centaine de bits modifier... cela prenais environ 90% de notre temps d'exectution.
__solution__ : Ne pas parcourire les solutions en tirant a l'avance le nombre de mutation qui devais etre réalisée dans chaque solution grace a des formule de probabilité. Ces formule utilisent des coefficients binomiaux (tres lourd), nous avons donc calculer a l'initialisation du solver une liste cumulée de la probabilité d'avoir un certain nombre de mutation a partire du taux de mutation.
(Nous avons aussi optimisé la generation de cette liste grace au formule decoulant du Triangle de Pascal. Assez peut utile puisque cela n'est calculer qu'a l'initialisation mais tres amusant)
Lors de la mutation d'une solution il faut donc tiré un float aléatoire entre 0 et 1 et se referer à la list_proba_mutation pour connaitre le nombre de mutation a réaliser sur cette solution. Ensuit, il ne reste plus qu'a tirer des objet aléatoire.
Le temps d'execution a été divisé par 10.

__contexte__ : les solutions était stocké sous la forme d'un tableau de bits permettant de savoir si un objet etait pris ou non dans le sac.
__probleme__ : la fonction de calcule de la fitness d'une solution devais alors parcourire la totalité de la solution. De meme lors des croisements, les 1 et 0 etait recopier un à un. C'etait les deux fonctions largement plus longue.
__solution__ : modifier la facons de stocker les solutions : nos solutions contenaient un ecrasante majoritée de 0, nous avons donc decidé de stocker les solutions sous la forme d'un numpy.set() contenant les index des objets.
Nous avons donc pus réaliser des `.add()`, `.remove()` et des `in` en temps O(1).
Le temps d'execution a été divisé par 10.

## Recherche des meilleurs parametres

__lecture des graph__ :

il y a deux type de graph differents utilisé dans cette partie :

- les courbes (rappel): permet de faire varier un parametre et d'observer l'evolution de la fitness en fonction de ce dernier. Pour chaque point du graphique l'algorithme est calculer un certain nombre de fois en incrementant la seed de Random. Cela permet d'avoir plusieurs données que nous affichons de la sorte : la moyenne avec un + rouge, la medianne avec un point bleu, l'espace entre la solution du 20eme centile et le 80eme centile par un barre bleu vertical et finalement un ligne horizontal pour placer la solution optimal (calculer par un lib externe).
- les heatmap : permet de faire varier deux parametres. Affiche la moyenne des meilleurs solutions obtenu dans chaque case et collore la case pour pouvoir la comparer facilement à ses voisines.

__methode__ :

Pour identifier les parametres permetant d'obtenire de bon resultats dans un temps résonnable, nous avons calculé la fitness moyenne des resultat pour des parametre donné.
Nous avons fait varier 1 ou 2 parametres a la fois ce qui nous a alors permis de generer des graphs pour identifier les parametres les plus efficaces.
Dans la grande majorité des cas, les premiers graph généré on permis de trouver un bon taux de mutation en faisant varier le nombres d'individus et le taux de mutation. (exemple sur 13-10000):

![Graph](\graph\Genetique\10000\13\01.png)

on peut clairement voir que l'on obtien de meilleurs resultat avec un taux de mutation proche de 0.00016. On peut donc regenerer un deuxieme graphique pour identifier plus precisement où se trouve le meilleur taux de mutation.
Une foi le taux de mutation fixé, on affiche une courbe de la fitness en fonction de la taille de la population pour voir jusqu'a où la l'augmentation de la population permet une amélioration significative du resultat. (exemple sur 13-1000):

![Graph](\graph\Genetique\1000\13\03.png)

Il reste alors a trouver a partire de combien d'iteration le resultat ne sameliore presque plus en partant des resultats determiné precedement. On calcule donc la courbe de la meilleurs fitness en fonction du nombre d'iteration. (exemple sur 15-1000):

![Graph](\graph\Genetique\1000\15\03.png)

Une fois toute les valeurs definis, on peut regenerer les premiers graphes avec cette fois ci des parametre plus juste pour verifier que nos estimation sont correcte.

### Solution optimal

determinées par KNAPSACK_DIVIDE_AND_CONQUER_SOLVER de la librairie ortools
sert de refferance pour evaluer la valeur des resultats.

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

A plusieurs reprise 
