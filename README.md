# S8_Knapsack

Polytech 4A INFO project

1. #### Résultat TABU pour pi-12-1000-1000-001 :

- NB_ITEMS: 1000
- MAX_CAPACITY: 4556

21 batchs de 10 tests.

- paramètres :
  - max itération/résolution : 1502
  - variation taille liste tabou
  - toujours ok pour 1.2x capacité max du sac.

![Courbe susdécrite](/results/1_pi12_1000_20batch_of10_1500iter_varTABU.png)
\*résultat en valeur du sac.
temps de clacul multi-thread chez Antonin (avec 1 thread par batch, 8 threads au total) : 4 minutes 46secondes

il semble que l'augmentation de la taille de la liste tabou est plutôt positive pour le résultat de l'algorithme, jusqu'à ce que l'on dépasse les ~990, comme on peut le voir dans la prochaine figure, avec des paramètres fixes identiques, mais un zoom entre 985 et 1001.
![mêmes tests entre 900 et 1000](/results/1_zoomed2.png)
Le constat : mieux vaut éviter d'avoir autant d'interdits que d'objets à choisir
