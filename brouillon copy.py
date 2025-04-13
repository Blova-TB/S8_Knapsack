import numpy as np
import pyopencl as cl

# Paramètres
n = 10  # Taille du problème
capacity = 10000
overflow_cost = 100

# Données simulées
rng = np.random.default_rng(42)
solution = rng.integers(0, 2, size=n).astype(np.int8)
item_weights = rng.integers(1, 100, size=n).astype(np.int32)
item_fitnesses = rng.integers(1, 100, size=n).astype(np.int32)
tabu_list = np.zeros(n, dtype=np.int8)  # Mettre certains éléments à 1 pour les rendre tabous
poids = sum(item_weights[solution == 1])
print("poids sad",poids,"/",capacity)
# Initialisation OpenCL
ctx = cl.create_some_context(False)
gpu =  ctx.get_info(cl.context_info.DEVICES)[0]
print("mem of gpu ",gpu.global_mem_size)
print("max group size",gpu.max_work_group_size)



queue = cl.CommandQueue(ctx)
mf = cl.mem_flags


# Buffers
solution_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=solution)
weights_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=item_weights)
fitnesses_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=item_fitnesses)

tabu_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=tabu_list)
temp_buf = cl.Buffer(ctx, mf.WRITE_ONLY, item_weights.nbytes)

kernel_max = """
__kernel void find_max_index(
    __global const int *arr, 
    const int size, 
    __global int *max_index) 
{
    int i = get_global_id(0);
    int local_id = get_local_id(0);
    int group_id = get_group_id(0);

    // Initialisation locale pour les comparaisons
    __local int local_max[64];  // Nombre de threads par groupe, à ajuster selon la taille du GPU

    // Charger les valeurs dans la mémoire locale
    if (i < size) {
        local_max[local_id] = arr[i];
    } else {
        local_max[local_id] = -32768;  // Valeur très basse si en dehors des limites
    }

    barrier(CLK_LOCAL_MEM_FENCE);

    // Réduction dans le groupe de threads
    for (int stride = get_local_size(0) / 2; stride > 0; stride /= 2) {
        if (local_id < stride) {
            local_max[local_id] = max(local_max[local_id], local_max[local_id + stride]);
        }
        barrier(CLK_LOCAL_MEM_FENCE);
    }

    // L'indice du maximum est envoyé par le thread 0 de chaque groupe
    if (local_id == 0) {
        atomic_max(max_index, local_max[0]);
    }
}
"""

# Kernel OpenCL
kernel_code = """
__kernel void compute_temp(
    __global const char *solution,
    __global const int *item_weights,
    __global const int *item_fitnesses,
    __global const char *tabu_list,
    const int poids,
    const int capacity,
    const float overflow_cost,  // overflow_cost reste en float pour la précision
    __global int *temp_out)
{
    int i = get_global_id(0);
    
    // Calcul de flip
    int flip = 1;
    if (solution[i]) {
        //si on est dans la solution, on retire.
        flip = -1;
    }

    // Calcul du poids après "flip" en entier
    int new_weight = flip * item_weights[i] + poids;

    // Calcul initial de temp en entier
    int temp = flip * item_fitnesses[i];

    // Gestion de l'overflow en gardant tout en entier
    if (new_weight > capacity) {
        temp -= (int)((new_weight - capacity) * overflow_cost);
    }

    // Application de la condition tabu
    if (tabu_list[i]) {
        temp = -32768;  // Utilisation d'une valeur minimale pour neutraliser les mouvements tabous
    }

    // Affectation du résultat dans temp_out
    temp_out[i] = temp;
}
"""

# Compilation et exécution
program = cl.Program(ctx, kernel_code).build()
program.compute_temp(
    queue, (n,), None,
    solution_buf, weights_buf, fitnesses_buf, tabu_buf,
    np.int32(poids), np.int32(capacity), np.int32(overflow_cost),
    temp_buf
)

# Récupération du résultat
temp_result = np.empty_like(item_weights)
cl.enqueue_copy(queue, temp_result, temp_buf)
best_id = np.argmax(temp_result)
best_id = -1 if temp_result[best_id] == -32768 else best_id
print(solution)
print(temp_result)
print(best_id,solution[best_id])

solution[best_id] = 1 - solution[best_id]
print("ns :",solution)
# on teste l'itération suivante (part du principe que tabu bouge pas)
cl.enqueue_copy(queue,solution_buf,solution)
poids += item_weights[best_id]
program.compute_temp(
    queue, (n,), None,
    solution_buf, weights_buf, fitnesses_buf, tabu_buf,
    np.int32(poids), np.int32(capacity), np.int32(overflow_cost),
    temp_buf
)
cl.enqueue_copy(queue, temp_result, temp_buf)
best_id = np.argmax(temp_result)
best_id = -1 if temp_result[best_id] == -32768 else best_id
print(solution)
print(temp_result)
print(best_id,solution[best_id])
queue.finish()
