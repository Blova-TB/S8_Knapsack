## Rapport Partie Génétique

### Introduction

#### Liens

**Tous les graphiques générés pour obtenir les résultats ci-dessous sont disponibles 👉 [ici](./graph/Genetique/)**  
**Le code permettant de générer ces graphiques est disponible 👉 [ici](./Genetique_generation_graph.ipynb)**  
**Un fichier prêt pour essayer l'algorithme facilement 👉 [ici](./Genetique_bac_a_sable.py)**

#### Fonctionnement de l'algorithme

Notre algorithme génétique fonctionne en 3 étapes :

- **Reproduction** : on réalise une roulette biaisée selon la fitness modifiée pour obtenir une nouvelle population.  
- **Croisement** : on croise les individus deux par deux selon un `cut_index` tiré aléatoirement pour obtenir une nouvelle population.  
- **Mutation** : on modifie légèrement et aléatoirement plusieurs solutions.

On répète ces 3 étapes un certain nombre de fois.

#### Liste des différents paramètres à faire varier

- nombre d’itérations avant d’arrêter le programme  
- nombre d’individus dans la population de solutions  
- taux de mutation par bit des solutions  

---

## Plusieurs évolutions du code

### Initialisation

**Contexte** : une première version du code utilisait une initialisation du sac à dos complètement aléatoire : chaque objet avait une chance sur deux d’être présent dans une solution.  
**Problème** : le poids des solutions de la première génération était bien trop élevé puisqu’elles contenaient en moyenne la moitié des éléments possibles. Le programme génétique n’arrivait alors pas à revenir sur des solutions réalisables, car la fitness de ces solutions était toujours égale à 0.  
**Solution** : nous avons donc rempli le sac à dos avec des objets aléatoires jusqu’à ce que le poids dépasse la capacité maximale.

### Déroulement

**Contexte** : la fitness du sac à dos se calcule en sommant les valeurs des objets qu’il contient, mais il ne faut pas dépasser le poids maximum autorisé.  
**Problème** : que faire si une solution dépasse ce poids ?  
**Solution** : si la solution permet tout de même de s’approcher d’un bon résultat, il serait dommage de lui attribuer une fitness de 0. Nous avons donc choisi de calculer une deuxième fitness (`calc_real_fitness()`) en fonction du poids et de la fitness :  
`max(fitness - 3 * max(weight - self.sad_capacity, 0), 1)`  
Les solutions dépassant légèrement la capacité pouvaient donc être conservées, mais elles n’étaient pas sélectionnées comme meilleurs solutions car invalides.

### Optimisation temporelle

**Contexte** : la fonction de mutation parcourait tous les bits de toutes les solutions en tirant un nombre aléatoire pour chaque bit.  
**Problème** : sur des fichiers à 10 000 objets avec une population de 100 individus, cela représentait 1 000 000 de tirages de nombres aléatoires par itération pour seulement une centaine de bits modifiés… Cela prenait environ 90 % du temps d’exécution.  
**Solution** : au lieu de parcourir tous les bits, on tire à l’avance le nombre de mutations à faire dans chaque solution grâce à des formules de probabilité (distribution binomiale/coefficients binomiaux). Ces calculs étant coûteux, nous avons pré-calculé une table de probabilités cumulées lors de l’initialisation du solver (grâce au triangle de Pascal).  
Lors de la mutation d’une solution, on tire un float entre 0 et 1 et on consulte la table `list_proba_mutation` pour déterminer le nombre de mutations à faire. Ensuite, on tire aléatoirement les objets concernés.  
Le temps d’exécution a été divisé par 10.

**Contexte** : les solutions étaient stockées sous forme de tableaux de bits representant une solution.
**Problème** : cela rendait le calcul de la fitness et les croisements très lents car obligé de tout parcourire même les zeros...
**Solution** : comme la majorité des bits sont à 0, on a changé le stockage des solutions pour utiliser un `set()` contenant uniquement les indices des objets sélectionnés. Cela permet des opérations tel que `.add()`, `.remove()` et `in` en temps O(1).  
Le temps d’exécution a encore été divisé par 10.

**Contexte** : sur les fichiers 12-10000 et 12-1000, de meilleurs résultats ont été obtenus avec un taux de mutation nul.  
**Problème** : pourquoi la mutation faisait-elle baisser la qualité des solutions ?  
**Solution** : la plupart des mutations ajoutaient un objet (car les solutions valides contiennent très peu d’objets).  
Nous avons donc créé une méthode de mutation (`new_mutation`) qui calcule le poids de la solution et décide s’il faut ajouter ou retirer un objet. Cette mutation reste aléatoire mais pousse la population à se rapprocher de la limite du sac.  
Cela a permis d'améliorer la moyenne sur le fichier 12-1000 de 4464 à 4500, avec un taux de mutation initialement nul devenu 0.0008.

---

## Recherche des meilleurs paramètres

### Lecture des graphiques

Il y a deux types de graphiques utilisés :

- **Courbes** (comme vu dans la partie TABU): on fait varier un paramètre et on observe l’évolution de la fitness. Chaque point correspond à une moyenne sur plusieurs runs avec différentes seeds.  
  - Moyenne : croix rouge  
  - Médiane : point bleu  
  - Intervalle intercentile (20e à 80e centile) : barre bleue  
  - Ligne horizontale : solution optimale (via une librairie externe)

- **Heatmaps** : font varier deux paramètres, affichent la moyenne des meilleures fitness dans chaque case, avec un code couleur pour visualiser facilement.

### Méthode

Pour identifier les parametres permetant d'obtenire de bon résultats dans un temps résonnable, nous avons fait varier 1 ou 2 parametres a la fois ce qui nous a alors permis de générer des graphs pour identifier les parametres les plus efficaces.
Dans la grande majorité des cas, les premiers graph généré on permis de trouver un bon taux de mutation en faisant varier le nombres d'individus et le taux de mutation.
Exemple (13-10000) :

![Graph](\graph\Genetique\10000\13\01.png)

On observe un pic de performance autour d’un taux de mutation de 0.00016. On peut donc regénérer un deuxieme graphique pour identifier plus precisement où se trouve le meilleur taux de mutation.
Une fois ce taux fixé, on observe l’évolution de la fitness selon la taille de la population.
Exemple (13-1000) :

![Graph](\graph\Genetique\1000\13\03.png)

Enfin, on observe quand commance la stagnation de la fitness pour déterminer combien d’itérations sont suffisantes en utilisant les parametre trouvé plus haut.
Exemple(15-1000) :

![Graph](\graph\Genetique\1000\15\03.png)

Une fois toutes les valeurs définies, on peut régénérer les premiers graphes, cette fois-ci avec des paramètres plus justes, pour vérifier que nos estimations sont correctes.


---

### Solutions optimales

Déterminées par `KNAPSACK_DIVIDE_AND_CONQUER_SOLVER` (librairie OR-Tools).

| Fichier      | Valeur optimale |
|--------------|-----------------|
| 12_100       | 970             |
| 13_100       | 1989            |
| 15_100       | 1011            |
| 12_1000      | 4514            |
| 13_1000      | 6513            |
| 15_1000      | 4950            |
| 12_10000     | 45105           |
| 13_10000     | 64077           |
| 15_10000     | 50622           |

---

## Résultats par taille de SAD

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
