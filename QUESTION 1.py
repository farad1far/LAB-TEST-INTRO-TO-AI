import numpy as np
import pandas as pd
import streamlit as st

# DEFINE ALGORITHM FUNCTIONS

def make_fitness(max_fitness, target_ones):
    """
    Creates a fitness function that peaks when number of ones == target_ones.
    """
    def fitness(x):
        n_ones = int(np.sum(x))
        
        penalty_per_diff = max_fitness / target_ones if target_ones != 0 else 0.0
        return float(max_fitness - abs(target_ones - n_ones) * penalty_per_diff)
    return fitness

def init_population(pop_size, dim, rng):
    return rng.integers(0, 2, size=(pop_size, dim), dtype=np.int8)

def tournament_selection(fitness_vals, k, rng):
    idxs = rng.integers(0, fitness_vals.size, size=k)
    return int(idxs[np.argmax(fitness_vals[idxs])])

def one_point_crossover(a, b, rng):
    if a.size < 2:
        return a.copy(), b.copy()
    point = rng.integers(1, a.size)
    return np.concatenate([a[:point], b[point:]]), np.concatenate([b[:point], a[point:]])

def bit_flip_mutation(ind, rate, rng):
    mask = rng.random(size=ind.shape) < rate
    ind[mask] = 1 - ind[mask]
    return ind

#MAIN APP

st.title("🧬 Question 1(b): Genetic Algorithm Bit Pattern")

# FIXED PARAMETERS (As per Question 1b)
POP_SIZE = 300
CHROMOSOME_LENGTH = 80
GENERATIONS = 50
TARGET_ONES = 40
MAX_FITNESS = 80

st.subheader("Configuration (Fixed)")
st.write(f"**Population:** {POP_SIZE}")
st.write(f"**Chromosome Length:** {CHROMOSOME_LENGTH}")
st.write(f"**Generations:** {GENERATIONS}")
st.write(f"**Target 'Ones' (Peak):** {TARGET_ONES}")
st.write(f"**Max Fitness:** {MAX_FITNESS}")

# Adjustable parameters for tuning (optional, but good for 'Web App' interactivity)
crossover_rate = st.slider("Crossover Rate", 0.0, 1.0, 0.8)
mutation_rate = st.slider("Mutation Rate", 0.0, 0.1, 0.01)

if st.button("Run Simulation"):
    # Setup
    rng = np.random.default_rng()
    fitness_fn = make_fitness(MAX_FITNESS, TARGET_ONES)
    population = init_population(POP_SIZE, CHROMOSOME_LENGTH, rng)
    
    # Tracking
    best_fitness_history = []
    
    progress_bar = st.progress(0)
    
    for gen in range(GENERATIONS):
        # 1. Evaluate Fitness
        fitness_vals = np.array([fitness_fn(ind) for ind in population])
        
        # Track stats
        current_best = np.max(fitness_vals)
        best_fitness_history.append(current_best)
        
        # 2. Selection & Next Gen
        new_pop = []
        for _ in range(POP_SIZE // 2):
            p1_idx = tournament_selection(fitness_vals, 3, rng)
            p2_idx = tournament_selection(fitness_vals, 3, rng)
            
            off1, off2 = one_point_crossover(population[p1_idx], population[p2_idx], rng)
            
            new_pop.append(bit_flip_mutation(off1, mutation_rate, rng))
            new_pop.append(bit_flip_mutation(off2, mutation_rate, rng))
        
        population = np.array(new_pop)
        progress_bar.progress((gen + 1) / GENERATIONS)

#INTERPRETATION AND RESULTS