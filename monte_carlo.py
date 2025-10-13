import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

class MonteCarloSimulator:
    def __init__(self, current_corpus: float, monthly_expenses: float, 
                 expected_inflation: float, expected_return: float, num_simulations: int = 1000,
                 max_years: int = 50):
        """
        Initialize the Monte Carlo simulator for retirement planning.
        
        Args:
            current_corpus: Starting retirement corpus
            monthly_expenses: Current monthly expenses
            expected_inflation: Expected inflation rate (as decimal, e.g., 0.06 for 6%)
            expected_return: Expected return rate (as decimal, e.g., 0.10 for 10%)
            num_simulations: Number of Monte Carlo simulations to run
            max_years: Maximum years to simulate (defaults to 50)
        """
        self.current_corpus = current_corpus
        self.monthly_expenses = monthly_expenses
        self.expected_inflation = expected_inflation
        self.expected_return = expected_return
        self.num_simulations = num_simulations
        
        # Variance parameters (±3%)
        self.inflation_std = 0.03
        self.return_std = 0.03
        
        # Maximum years to simulate (to prevent infinite loops)
        self.max_years = max_years
    
    def generate_random_rates(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate random inflation and return rates for all simulations.
        
        Returns:
            Tuple of (inflation_rates, return_rates) arrays
        """
        # Generate random rates using normal distribution
        inflation_rates = np.random.normal(
            self.expected_inflation, 
            self.inflation_std, 
            (self.num_simulations, self.max_years)
        )
        
        return_rates = np.random.normal(
            self.expected_return, 
            self.return_std, 
            (self.num_simulations, self.max_years)
        )
        
        # Ensure rates don't go negative (minimum 0.1%)
        inflation_rates = np.maximum(inflation_rates, 0.001)
        return_rates = np.maximum(return_rates, 0.001)
        
        return inflation_rates, return_rates
    
    def simulate_single_scenario(self, inflation_rates: np.ndarray, 
                               return_rates: np.ndarray) -> Tuple[float, List[float]]:
        """
        Simulate a single retirement scenario.
        
        Args:
            inflation_rates: Array of inflation rates for each year
            return_rates: Array of return rates for each year
            
        Returns:
            Tuple of (years_lasted, corpus_trajectory)
        """
        corpus = self.current_corpus
        monthly_expenses = self.monthly_expenses
        corpus_trajectory = [corpus]
        
        for year in range(self.max_years):
            # Apply inflation to expenses
            annual_expenses = monthly_expenses * 12 * (1 + inflation_rates[year])
            monthly_expenses = annual_expenses / 12
            
            # Apply investment returns
            corpus = corpus * (1 + return_rates[year])
            
            # Subtract annual expenses
            corpus = corpus - annual_expenses
            
            corpus_trajectory.append(max(corpus, 0))
            
            # Check if corpus is depleted
            if corpus <= 0:
                return year + 1, corpus_trajectory
        
        return self.max_years, corpus_trajectory
    
    def run_simulation(self) -> Dict:
        """
        Run the complete Monte Carlo simulation.
        
        Returns:
            Dictionary containing simulation results and statistics
        """
        # Generate random rates for all simulations
        inflation_rates, return_rates = self.generate_random_rates()
        
        # Storage for results
        years_lasted = []
        all_trajectories = []
        
        # Run simulations
        for i in range(self.num_simulations):
            years, trajectory = self.simulate_single_scenario(
                inflation_rates[i], return_rates[i]
            )
            years_lasted.append(years)
            all_trajectories.append(trajectory)
        
        # Calculate statistics
        years_array = np.array(years_lasted)
        
        results = {
            'years_lasted': years_lasted,
            'mean_years': np.mean(years_array),
            'median_years': np.median(years_array),
            'pessimistic_years': np.percentile(years_array, 25),
            'optimistic_years': np.percentile(years_array, 75),
            'min_years': np.min(years_array),
            'max_years': np.max(years_array),
            'std_years': np.std(years_array),
            'success_rate': np.sum(years_array >= 20) / len(years_array) * 100,
            'simulation_data': self._prepare_simulation_data(all_trajectories, years_lasted)
        }
        
        return results
    
    def _prepare_simulation_data(self, all_trajectories: List[List[float]], 
                               years_lasted: List[float]) -> Dict:
        """
        Prepare simulation data for visualization.
        
        Args:
            all_trajectories: List of corpus trajectories for each simulation
            years_lasted: List of years each simulation lasted
            
        Returns:
            Dictionary with processed simulation data
        """
        # Find the maximum length for padding
        max_length = max(len(trajectory) for trajectory in all_trajectories)
        
        # Pad trajectories and convert to DataFrame
        padded_trajectories = []
        for trajectory in all_trajectories:
            padded = trajectory + [0] * (max_length - len(trajectory))
            padded_trajectories.append(padded)
        
        df = pd.DataFrame(padded_trajectories).T
        
        # Calculate percentiles for confidence intervals
        percentiles = {}
        for year in range(min(30, max_length)):  # Show up to 30 years
            year_data = df.iloc[year].values
            # Only consider simulations that haven't depleted yet
            active_sims = year_data[year_data > 0] if len(year_data[year_data > 0]) > 0 else [0]
            
            percentiles[year] = {
                'p10': np.percentile(active_sims, 10) if len(active_sims) > 0 else 0,
                'p25': np.percentile(active_sims, 25) if len(active_sims) > 0 else 0,
                'p50': np.percentile(active_sims, 50) if len(active_sims) > 0 else 0,
                'p75': np.percentile(active_sims, 75) if len(active_sims) > 0 else 0,
                'p90': np.percentile(active_sims, 90) if len(active_sims) > 0 else 0,
                'mean': np.mean(active_sims) if len(active_sims) > 0 else 0
            }
        
        return {
            'percentiles': percentiles,
            'raw_trajectories': df,
            'years': list(range(len(percentiles)))
        }
