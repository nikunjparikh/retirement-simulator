import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

class MonteCarloSimulator:
    def __init__(self, current_corpus: float, monthly_expenses: float, 
                 expected_inflation: float, expected_return: float, 
                 inflation_volatility: float = 0.03, return_volatility: float = 0.12,
                 num_simulations: int = 1000, max_years: int = 50):
        """
        Initialize the Monte Carlo simulator for retirement planning.
        
        Args:
            current_corpus: Starting retirement corpus
            monthly_expenses: Current monthly expenses
            expected_inflation: Expected inflation rate (as decimal, e.g., 0.06 for 6%)
            expected_return: Expected return rate (as decimal, e.g., 0.10 for 10%)
            inflation_volatility: Volatility (std dev) of inflation (as decimal, e.g., 0.03 for 3%)
            return_volatility: Volatility (std dev) of returns (as decimal, e.g., 0.12 for 12%)
            num_simulations: Number of Monte Carlo simulations to run
            max_years: Maximum years to simulate (defaults to 50)
        """
        self.current_corpus = current_corpus
        self.monthly_expenses = monthly_expenses
        self.expected_inflation = expected_inflation
        self.expected_return = expected_return
        self.num_simulations = num_simulations
        
        # Volatility parameters (user-configurable)
        self.inflation_volatility = inflation_volatility
        self.return_volatility = return_volatility
        
        # Maximum years to simulate (to prevent infinite loops)
        self.max_years = max_years
    
    def generate_random_rates(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate random inflation and return rates using log-normal distribution.
        
        Log-normal distribution ensures rates are always positive and better models
        the multiplicative nature of compound returns.
        
        Returns:
            Tuple of (inflation_rates, return_rates) arrays
        """
        # Convert to log-normal parameters (mu, sigma)
        # For log-normal: if we want mean=m and std=s, then:
        # mu = ln(m^2 / sqrt(m^2 + s^2))
        # sigma = sqrt(ln(1 + (s/m)^2))
        
        # Inflation rates
        m_inf = self.expected_inflation
        s_inf = self.inflation_volatility
        mu_inf = np.log(m_inf**2 / np.sqrt(m_inf**2 + s_inf**2))
        sigma_inf = np.sqrt(np.log(1 + (s_inf/m_inf)**2))
        
        inflation_rates = np.random.lognormal(
            mu_inf, 
            sigma_inf, 
            (self.num_simulations, self.max_years)
        )
        
        # Return rates
        m_ret = self.expected_return
        s_ret = self.return_volatility
        mu_ret = np.log(m_ret**2 / np.sqrt(m_ret**2 + s_ret**2))
        sigma_ret = np.sqrt(np.log(1 + (s_ret/m_ret)**2))
        
        return_rates = np.random.lognormal(
            mu_ret, 
            sigma_ret, 
            (self.num_simulations, self.max_years)
        )
        
        # Log-normal naturally produces positive values, no need to floor them
        return inflation_rates, return_rates
    
    def simulate_single_scenario(self, inflation_rates: np.ndarray, 
                               return_rates: np.ndarray) -> Tuple[float, List[float], float]:
        """
        Simulate a single retirement scenario with monthly precision.
        
        Args:
            inflation_rates: Array of inflation rates for each year
            return_rates: Array of return rates for each year
            
        Returns:
            Tuple of (years_lasted, corpus_trajectory, final_corpus)
        """
        corpus = self.current_corpus
        monthly_expenses = self.monthly_expenses
        corpus_trajectory = [corpus]
        
        for year in range(self.max_years):
            # Calculate annual rates for this year
            annual_inflation = inflation_rates[year]
            annual_return = return_rates[year]
            
            # Convert to monthly rates (approximate)
            monthly_return = (1 + annual_return) ** (1/12) - 1
            monthly_inflation = (1 + annual_inflation) ** (1/12) - 1
            
            # Track corpus through each month of the year
            year_start_corpus = corpus
            for month in range(12):
                # Apply monthly return
                corpus = corpus * (1 + monthly_return)
                
                # Inflate monthly expenses
                monthly_expenses = monthly_expenses * (1 + monthly_inflation)
                
                # Subtract monthly expenses
                corpus = corpus - monthly_expenses
                
                # Check if corpus is depleted
                if corpus <= 0:
                    # Return fractional year (year + month/12)
                    fractional_year = year + (month + 1) / 12
                    corpus_trajectory.append(0)
                    return fractional_year, corpus_trajectory, 0
            
            # End of year - record corpus
            corpus_trajectory.append(max(corpus, 0))
        
        # If we made it through max_years, return final corpus value
        return self.max_years, corpus_trajectory, max(corpus, 0)
    
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
        final_corpus_values = []
        for i in range(self.num_simulations):
            years, trajectory, final_corpus = self.simulate_single_scenario(
                inflation_rates[i], return_rates[i]
            )
            years_lasted.append(years)
            all_trajectories.append(trajectory)
            final_corpus_values.append(final_corpus)
        
        # Calculate statistics
        years_array = np.array(years_lasted)
        final_corpus_array = np.array(final_corpus_values)
        
        pessimistic_years = np.percentile(years_array, 25)
        median_years = np.median(years_array)
        optimistic_years = np.percentile(years_array, 75)
        
        # Check if key scenarios all survive the full retirement period
        # Use the conservative (25th percentile) as the threshold
        all_scenarios_survive = pessimistic_years >= self.max_years
        
        results = {
            'years_lasted': years_lasted,
            'mean_years': np.mean(years_array),
            'median_years': median_years,
            'pessimistic_years': pessimistic_years,
            'optimistic_years': optimistic_years,
            'min_years': np.min(years_array),
            'max_years': np.max(years_array),
            'std_years': np.std(years_array),
            'success_rate': np.sum(years_array >= 20) / len(years_array) * 100,
            'final_corpus_conservative': np.percentile(final_corpus_array, 25),
            'final_corpus_median': np.percentile(final_corpus_array, 50),
            'final_corpus_optimistic': np.percentile(final_corpus_array, 75),
            'all_scenarios_survive': all_scenarios_survive,
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
