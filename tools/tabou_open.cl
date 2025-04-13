//code pour le premier solver openCL

 __kernel void compute_temp1(
    __global const char *solution,
    __global const int *item_weights,
    __global const int *item_fitnesses,
    __global const char *tabu_list,
    const int poids,
    const int capacity,
    const float overflow_cost,  // overflow_cost reste en float pour la précision
    __global float *temp_out)
{
    int i = get_global_id(0);
    
    // Calcul de flip
    int flip = 1 - 2 * solution[i];
    // Calcul du poids après "flip" en entier
    int flipped_weights = flip * item_weights[i] + poids;

    // Calcul initial de temp 
    float temp = flip * item_fitnesses[i];

    // Gestion de l'overflow
    if (flipped_weights > capacity) {
        temp -= (flipped_weights - capacity) * overflow_cost;
    }

    // Application de la condition tabu
    if (tabu_list[i]) {
        temp = -1048576.f;  // Utilisation d'une valeur minimale pour neutraliser les mouvements tabous
    }

    // Affectation du résultat dans temp_out
    temp_out[i] = temp;

}


//code pour le 2nd solver openCL
__kernel void compute_temp2(
    __global const char *solution,
    __global const int *item_weights,
    __global const int *item_fitnesses,
    __global const char *tabu_list,
    const int poids,
    const int capacity,
    const float overflow_cost,  // overflow_cost reste en float pour la précision
    __global float *best_vals,     // [nb_groups]
    __global int *best_indices   // [nb_groups]
) {
    int i = get_global_id(0);
    int lid = get_local_id(0);
    int group = get_group_id(0);
    int lsize = get_local_size(0);
    
    __local float local_vals[256]; //creation de variables interne à chaque groupes
    __local int local_indices[256];
    
    // Calcul de flip
    int flip = 1 - 2 * solution[i];
    // Calcul du poids après "flip" en entier
    int flipped_weights = flip * item_weights[i] + poids;


    float temp = flip * item_fitnesses[i];
    //pour overflow
    if (flipped_weights > capacity) {
        temp -= (flipped_weights - capacity) * overflow_cost;
    }

    if (tabu_list[i]) {
        // Utilisation d'une valeur minimale pour neutraliser les mouvements tabous
        //les éléments du derniers groupes hors bornes entrent dans ce cas.
        local_vals[lid] = -1048576.f; 
        local_indices[lid] = -1;//opération pas ok.
    } else {
        local_vals[lid] = temp;//valeur locale : self
        local_indices[lid] = i;//indice global
    }

    barrier(CLK_LOCAL_MEM_FENCE);//sync

    // Réduction dans le groupe
    for (int offset = lsize / 2; offset > 0; offset >>= 1) {
        if (lid < offset) {
            if (local_vals[lid] < local_vals[lid + offset]) {
                local_vals[lid] = local_vals[lid + offset];
                local_indices[lid] = local_indices[lid + offset];
            }
        }
        barrier(CLK_LOCAL_MEM_FENCE);
    }

    // Thread 0 écrit le résultat du groupe
    if (lid == 0) {
        best_vals[group] = local_vals[0];
        best_indices[group] = local_indices[0];
    }
    
}

__kernel void reduce_max_global(
    __global float *best_vals,  // Meilleures valeurs trouvées par chaque groupe
    __global int *best_indices,  // Indices correspondants de chaque groupe
    const int nbgroupes,
    __global int *final_best_idx  // Résultat : indice du meilleur élément global
) {
    int i = get_global_id(0);  // Indice global pour l'agrégation

    // Réduction des meilleures valeurs pour trouver le maximum global
    for (int offset = nbgroupes / 2; offset > 0; offset >>= 1) {
        if (i < offset) {
            if (best_vals[i] < best_vals[i + offset]) {
                best_vals[i] = best_vals[i + offset];
                best_indices[i] = best_indices[i + offset];
            }
        }
        barrier(CLK_GLOBAL_MEM_FENCE);  // Synchronisation après chaque étape
    }

    // Thread 0 écrit l'indice global du meilleur élément trouvé
    if (i == 0) {
        final_best_idx[0] = best_indices[0];
    }
}
