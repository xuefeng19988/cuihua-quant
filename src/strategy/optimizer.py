"""
Phase 34: Strategy Optimizer
Automated strategy parameter optimization with genetic algorithm.
"""

import os
import sys
import random
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Callable

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class GeneticOptimizer:
    """
    Genetic algorithm for strategy parameter optimization.
    """
    
    def __init__(self, population_size: int = 50, generations: int = 30,
                 mutation_rate: float = 0.1, crossover_rate: float = 0.7):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
    def optimize(self, param_ranges: Dict[str, Tuple], fitness_func: Callable,
                 maximize: bool = True) -> Dict:
        """
        Optimize parameters using genetic algorithm.
        
        Args:
            param_ranges: Dict of {param_name: (min, max, step)}
            fitness_func: Function to evaluate fitness
            maximize: Whether to maximize or minimize fitness
            
        Returns:
            Optimization results
        """
        # Initialize population
        population = self._initialize_population(param_ranges)
        
        best_individual = None
        best_fitness = -float('inf') if maximize else float('inf')
        history = []
        
        for generation in range(self.generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                fitness = fitness_func(individual)
                fitness_scores.append(fitness)
                
                # Update best
                if maximize and fitness > best_fitness:
                    best_fitness = fitness
                    best_individual = individual.copy()
                elif not maximize and fitness < best_fitness:
                    best_fitness = fitness
                    best_individual = individual.copy()
                    
            history.append({
                'generation': generation,
                'best_fitness': best_fitness,
                'avg_fitness': np.mean(fitness_scores)
            })
            
            # Selection
            selected = self._select(population, fitness_scores, maximize)
            
            # Crossover
            offspring = self._crossover(selected, param_ranges)
            
            # Mutation
            population = self._mutate(offspring, param_ranges)
            
        return {
            'best_params': best_individual,
            'best_fitness': best_fitness,
            'history': history,
            'generations': self.generations
        }
        
    def _initialize_population(self, param_ranges: Dict) -> List[Dict]:
        """Initialize random population."""
        population = []
        for _ in range(self.population_size):
            individual = {}
            for param, (min_val, max_val, step) in param_ranges.items():
                steps = int((max_val - min_val) / step)
                individual[param] = min_val + random.randint(0, steps) * step
            population.append(individual)
        return population
        
    def _select(self, population: List[Dict], fitness_scores: List[float], 
                maximize: bool) -> List[Dict]:
        """Tournament selection."""
        selected = []
        tournament_size = 3
        
        for _ in range(len(population)):
            tournament = random.sample(list(zip(population, fitness_scores)), 
                                      min(tournament_size, len(population)))
            if maximize:
                winner = max(tournament, key=lambda x: x[1])
            else:
                winner = min(tournament, key=lambda x: x[1])
            selected.append(winner[0].copy())
            
        return selected
        
    def _crossover(self, selected: List[Dict], param_ranges: Dict) -> List[Dict]:
        """Single-point crossover."""
        offspring = []
        params = list(param_ranges.keys())
        
        for i in range(0, len(selected) - 1, 2):
            if random.random() < self.crossover_rate:
                # Crossover
                child1 = selected[i].copy()
                child2 = selected[i + 1].copy()
                
                crossover_point = random.randint(1, len(params) - 1)
                for param in params[crossover_point:]:
                    child1[param], child2[param] = child2[param], child1[param]
                    
                offspring.extend([child1, child2])
            else:
                offspring.extend([selected[i].copy(), selected[i + 1].copy()])
                
        return offspring
        
    def _mutate(self, offspring: List[Dict], param_ranges: Dict) -> List[Dict]:
        """Mutate individuals."""
        for individual in offspring:
            for param, (min_val, max_val, step) in param_ranges.items():
                if random.random() < self.mutation_rate:
                    steps = int((max_val - min_val) / step)
                    individual[param] = min_val + random.randint(0, steps) * step
        return offspring
        
    def generate_report(self, results: Dict) -> str:
        """Generate optimization report."""
        lines = []
        lines.append("=" * 60)
        lines.append("🧬 遗传算法优化报告")
        lines.append("=" * 60)
        
        lines.append(f"\n🏆 最优参数")
        for param, value in results['best_params'].items():
            lines.append(f"  {param}: {value}")
            
        lines.append(f"\n📊 最优适应度: {results['best_fitness']:.4f}")
        lines.append(f"📈 迭代次数: {results['generations']}")
        
        # Show convergence
        history = results['history']
        if history:
            lines.append(f"\n📉 收敛曲线")
            lines.append(f"  初始: {history[0]['avg_fitness']:.4f}")
            lines.append(f"  最终: {history[-1]['avg_fitness']:.4f}")
            lines.append(f"  提升: {((history[-1]['avg_fitness'] / history[0]['avg_fitness']) - 1) * 100:.1f}%")
            
        return "\n".join(lines)


class ParameterSweeper:
    """
    Grid search and random search for parameter optimization.
    """
    
    def __init__(self):
        pass
        
    def grid_search(self, param_grid: Dict[str, List], fitness_func: Callable,
                    maximize: bool = True) -> Dict:
        """
        Exhaustive grid search.
        
        Args:
            param_grid: Dict of {param_name: [values]}
            fitness_func: Function to evaluate
            maximize: Whether to maximize
            
        Returns:
            Search results
        """
        # Generate all combinations
        from itertools import product
        
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        best_params = None
        best_fitness = -float('inf') if maximize else float('inf')
        all_results = []
        
        for values in product(*param_values):
            params = dict(zip(param_names, values))
            fitness = fitness_func(params)
            
            all_results.append({**params, 'fitness': fitness})
            
            if maximize and fitness > best_fitness:
                best_fitness = fitness
                best_params = params.copy()
            elif not maximize and fitness < best_fitness:
                best_fitness = fitness
                best_params = params.copy()
                
        return {
            'best_params': best_params,
            'best_fitness': best_fitness,
            'all_results': all_results,
            'total_evaluations': len(all_results)
        }
        
    def random_search(self, param_ranges: Dict[str, Tuple], fitness_func: Callable,
                     n_iterations: int = 100, maximize: bool = True) -> Dict:
        """
        Random search.
        
        Args:
            param_ranges: Dict of {param_name: (min, max)}
            fitness_func: Function to evaluate
            n_iterations: Number of random samples
            maximize: Whether to maximize
            
        Returns:
            Search results
        """
        best_params = None
        best_fitness = -float('inf') if maximize else float('inf')
        all_results = []
        
        for _ in range(n_iterations):
            params = {}
            for param, (min_val, max_val) in param_ranges.items():
                params[param] = random.uniform(min_val, max_val)
                
            fitness = fitness_func(params)
            all_results.append({**params, 'fitness': fitness})
            
            if maximize and fitness > best_fitness:
                best_fitness = fitness
                best_params = params.copy()
            elif not maximize and fitness < best_fitness:
                best_fitness = fitness
                best_params = params.copy()
                
        return {
            'best_params': best_params,
            'best_fitness': best_fitness,
            'all_results': all_results,
            'total_evaluations': n_iterations
        }


if __name__ == "__main__":
    # Test genetic optimizer
    def fitness_func(params):
        # Simple mock fitness function
        return -(params['x'] - 3)**2 - (params['y'] + 2)**2 + 10
        
    optimizer = GeneticOptimizer(population_size=30, generations=20)
    
    param_ranges = {
        'x': (-10, 10, 0.5),
        'y': (-10, 10, 0.5)
    }
    
    results = optimizer.optimize(param_ranges, fitness_func, maximize=True)
    print(optimizer.generate_report(results))
