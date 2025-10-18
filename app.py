import streamlit as st
import numpy as np
from monte_carlo import MonteCarloSimulator

def format_indian_number(num):
    """Format number in Indian numbering system (lakhs, crores) or international (thousands, millions, billions)"""
    if num >= 10000000:  # 1 crore or more
        crores = num / 10000000
        if crores >= 100:
            return f"{crores:.0f} Cr"
        elif crores >= 10:
            return f"{crores:.1f} Cr"
        else:
            return f"{crores:.2f} Cr"
    elif num >= 100000:  # 1 lakh or more
        lakhs = num / 100000
        if lakhs >= 10:
            return f"{lakhs:.0f} L"
        else:
            return f"{lakhs:.1f} L"
    elif num >= 1000:  # 1 thousand or more
        thousands = num / 1000
        if thousands >= 100:
            return f"{thousands:.0f}K"
        else:
            return f"{thousands:.1f}K"
    else:
        return f"{num:.0f}"

def format_with_commas(num):
    """Format number with comma separators"""
    return f"{int(num):,}"

def calculate_target_corpus(current_corpus, monthly_expenses, max_years, target_success_rate=0.80, max_iterations=12):
    """
    Use binary search to find the corpus amount needed to achieve target success rate.
    Returns the target corpus amount or None if not found within reasonable bounds.
    """
    # Realistic scenario parameters
    params = {
        'return': 0.10,
        'return_volatility': 0.16,
        'inflation': 0.06,
        'inflation_volatility': 0.03
    }
    
    # Set search bounds (0.5x to 5x current corpus)
    low = current_corpus * 0.5
    high = current_corpus * 5.0
    
    for _ in range(max_iterations):
        mid = (low + high) / 2
        
        # Run simulation with this corpus amount
        simulator = MonteCarloSimulator(
            current_corpus=mid,
            monthly_expenses=monthly_expenses,
            expected_inflation=params['inflation'],
            expected_return=params['return'],
            inflation_volatility=params['inflation_volatility'],
            return_volatility=params['return_volatility'],
            num_simulations=500,  # Reduced for speed
            max_years=max_years
        )
        results = simulator.run_simulation()
        years_lasted = np.array(results['years_lasted'])
        success_rate = (years_lasted >= max_years).sum() / len(years_lasted)
        
        # Check if we're close enough to target
        if abs(success_rate - target_success_rate) < 0.03:  # Within 3%
            return mid
        elif success_rate < target_success_rate:
            low = mid  # Need more corpus
        else:
            high = mid  # Can use less corpus
    
    # Return the midpoint of final range
    return (low + high) / 2

def calculate_target_spending(corpus, current_monthly_expenses, max_years, target_success_rate=0.80, max_iterations=12):
    """
    Use binary search to find the monthly spending amount that achieves target success rate.
    Returns the target monthly expenses or None if not found within reasonable bounds.
    """
    # Realistic scenario parameters
    params = {
        'return': 0.10,
        'return_volatility': 0.16,
        'inflation': 0.06,
        'inflation_volatility': 0.03
    }
    
    # Set search bounds (20% to 100% of current spending)
    low = current_monthly_expenses * 0.2
    high = current_monthly_expenses
    
    for _ in range(max_iterations):
        mid = (low + high) / 2
        
        # Run simulation with this spending amount
        simulator = MonteCarloSimulator(
            current_corpus=corpus,
            monthly_expenses=mid,
            expected_inflation=params['inflation'],
            expected_return=params['return'],
            inflation_volatility=params['inflation_volatility'],
            return_volatility=params['return_volatility'],
            num_simulations=500,  # Reduced for speed
            max_years=max_years
        )
        results = simulator.run_simulation()
        years_lasted = np.array(results['years_lasted'])
        success_rate = (years_lasted >= max_years).sum() / len(years_lasted)
        
        # Check if we're close enough to target
        if abs(success_rate - target_success_rate) < 0.03:  # Within 3%
            return mid
        elif success_rate < target_success_rate:
            high = mid  # Need to spend less
        else:
            low = mid  # Can spend more
    
    # Return the midpoint of final range
    return (low + high) / 2

def main():
    st.set_page_config(
        page_title="Retirement Corpus Calculator",
        page_icon="💰"
    )
    
    st.title("🌴 Are you ready to retire?")
    st.markdown("Find out how long your retirement savings will last. This calculator runs thousands of simulations to show you different scenarios based on varying market conditions. Get a realistic picture of your retirement readiness with median, optimistic, and conservative estimates.")
    
    st.divider()
    
    # Input Parameters Section
    st.header("📊 Input Parameters")
    
    # User inputs
    current_age = st.number_input(
        "Current Age", 
        min_value=18, 
        max_value=80, 
        value=30, 
        step=1,
        help="Your current age"
    )
    
    retirement_age = st.number_input(
        "When do you want to retire", 
        min_value=40, 
        max_value=100, 
        value=60, 
        step=1,
        help="Age at which you plan to retire"
    )
    
    life_expectancy = st.slider(
        "Expected Life Expectancy",
        min_value=70,
        max_value=100,
        value=80,
        step=1,
        help="Your expected life expectancy in years"
    )
    
    target_corpus = st.number_input(
        "Savings at retirement age", 
        min_value=100000, 
        max_value=1000000000, 
        value=10000000, 
        step=100000,
        help="Your total savings when you retire"
    )
    st.caption(f"💡 That's **{format_with_commas(target_corpus)}** ({format_indian_number(target_corpus)})")
    
    monthly_expenses = st.number_input(
        "Monthly Expenses at Retirement", 
        min_value=10000, 
        max_value=10000000, 
        value=50000, 
        step=5000,
        help="Expected monthly expenses when you retire (will be adjusted for inflation)"
    )
    st.caption(f"💡 That's **{format_with_commas(monthly_expenses)}** per month ({format_indian_number(monthly_expenses)})")
    
    run_simulation = st.button("🚀 Run Simulation", type="primary", use_container_width=True)
    
    st.divider()
    
    # Results Section
    if run_simulation:
        # Validate ages
        if current_age >= retirement_age:
            st.error("⚠️ Current age must be less than retirement age!")
        elif life_expectancy <= retirement_age:
            st.error("⚠️ Life expectancy must be greater than retirement age!")
        else:
            max_retirement_years = life_expectancy - retirement_age
            
            with st.spinner("Running Monte Carlo simulations for all scenarios..."):
                # Define three scenarios with hardcoded parameters
                scenarios = {
                    'Optimistic': {
                        'return': 0.12,
                        'return_volatility': 0.22,
                        'inflation': 0.05,
                        'inflation_volatility': 0.025
                    },
                    'Realistic': {
                        'return': 0.10,
                        'return_volatility': 0.16,
                        'inflation': 0.06,
                        'inflation_volatility': 0.03
                    },
                    'Pessimistic': {
                        'return': 0.07,
                        'return_volatility': 0.10,
                        'inflation': 0.08,
                        'inflation_volatility': 0.04
                    }
                }
                
                # Run simulation for each scenario
                scenario_results = {}
                for scenario_name, params in scenarios.items():
                    simulator = MonteCarloSimulator(
                        current_corpus=target_corpus,
                        monthly_expenses=monthly_expenses,
                        expected_inflation=params['inflation'],
                        expected_return=params['return'],
                        inflation_volatility=params['inflation_volatility'],
                        return_volatility=params['return_volatility'],
                        num_simulations=1000,
                        max_years=max_retirement_years
                    )
                    scenario_results[scenario_name] = simulator.run_simulation()
                
                # Display results
                display_results(scenario_results, retirement_age, life_expectancy, target_corpus, monthly_expenses, max_retirement_years)
    else:
        st.info("👆 Configure your parameters and click 'Run Simulation' to see results")

def display_results(scenario_results, retirement_age, life_expectancy, target_corpus, monthly_expenses, max_retirement_years):
    st.header("📈 Simulation Results")
    
    corpus_formatted = format_indian_number(target_corpus)
    
    # Calculate realistic scenario results first (for recommendations)
    real_results = scenario_results['Realistic']
    real_median_years = real_results['median_years']
    real_years = np.array(real_results['years_lasted'])
    real_success_rate = (real_years >= max_retirement_years).sum() / len(real_years) * 100
    
    # Display prominent recommendations first
    st.markdown("### 🎯 Your Retirement Readiness")
    
    if real_success_rate >= 75:
        st.success(f"""
        ## ✅ You're Ready to Retire!
        
        Based on our realistic scenario (balanced portfolio), your corpus has a **{real_success_rate:.1f}% success rate** of lasting your entire **{max_retirement_years}-year** retirement period (age {retirement_age} to {life_expectancy}).
        
        **Your retirement plan looks solid.** Check the pessimistic scenario below for extra safety planning.
        """)
    elif real_success_rate >= 50:
        # Calculate specific recommendations for borderline cases
        if real_median_years > 0:
            estimated_multiplier = max_retirement_years / real_median_years
            required_corpus = target_corpus * estimated_multiplier
            additional_savings_needed = required_corpus - target_corpus
            
            # Calculate reduced monthly expenses option
            # Rough approximation: reduce expenses proportionally
            reduced_expenses = monthly_expenses * (real_median_years / max_retirement_years)
            
            st.warning(f"""
            ## ⚠️ Your Corpus May Be Borderline
            
            Based on our realistic scenario, your corpus has only a **{real_success_rate:.1f}% success rate** of lasting your full retirement. The median duration is **{real_median_years:.1f} years** (vs {max_retirement_years} years needed).
            
            **Recommended Actions (choose one or combine):**
            - 💰 **Save ₹{format_with_commas(additional_savings_needed)}** more ({format_indian_number(additional_savings_needed)})
            - 📉 **Reduce spending to ₹{format_with_commas(reduced_expenses)}** per month ({format_indian_number(reduced_expenses)})
            - 📋 Have a backup plan for later retirement years
            """)
        else:
            st.warning(f"""
            ## ⚠️ Your Corpus May Be Borderline
            
            Based on our realistic scenario, your corpus has only a **{real_success_rate:.1f}% success rate** of lasting your full retirement.
            
            **Recommended Actions:**
            - 💰 Increase your retirement corpus
            - 📉 Reduce planned monthly expenses
            - 📋 Have a backup plan for later retirement years
            """)
    else:
        # Calculate specific recommendations for insufficient corpus
        if real_median_years > 0:
            estimated_multiplier = max_retirement_years / real_median_years
            required_corpus = target_corpus * estimated_multiplier
            additional_savings_needed = required_corpus - target_corpus
            
            # Calculate reduced monthly expenses option
            reduced_expenses = monthly_expenses * (real_median_years / max_retirement_years)
            
            st.error(f"""
            ## ⚠️ Your Corpus Is Likely Insufficient
            
            Based on our realistic scenario, your corpus has only a **{real_success_rate:.1f}% success rate**. The median duration is **{real_median_years:.1f} years** (vs {max_retirement_years} years needed).
            
            ### 🎯 Target Corpus: **₹{format_with_commas(required_corpus)}** ({format_indian_number(required_corpus)})
            
            **Recommended Actions (choose one or combine):**
            - 💰 **Save ₹{format_with_commas(additional_savings_needed)}** more ({format_indian_number(additional_savings_needed)})
            - 📉 **Reduce spending to ₹{format_with_commas(reduced_expenses)}** per month ({format_indian_number(reduced_expenses)})
            - ⏰ Delay retirement to save more and reduce the retirement period
            """)
        else:
            st.error(f"""
            ## ⚠️ Your Corpus Is Significantly Insufficient
            
            Your corpus depletes very quickly in the realistic scenario. You need a comprehensive review of your retirement strategy.
            
            **Recommended Actions:**
            - 💰 Substantially increase your retirement savings
            - 📉 Significantly reduce planned monthly expenses
            - ⏰ Delay retirement to accumulate more savings
            """)
    
    st.divider()
    
    # Display detailed scenario comparison below recommendations
    st.markdown("### 📊 Detailed Scenario Comparison")
    st.caption("See how your corpus performs under different market conditions")
    
    # Create three columns for the scenarios
    col1, col2, col3 = st.columns(3)
    
    # Optimistic Scenario
    with col1:
        st.markdown("#### 🌟 Optimistic")
        opt_results = scenario_results['Optimistic']
        opt_median_years = opt_results['median_years']
        opt_years = np.array(opt_results['years_lasted'])
        opt_success_rate = (opt_years >= max_retirement_years).sum() / len(opt_years) * 100
        
        # Color code success rate
        if opt_success_rate > 80:
            color = "green"
        elif opt_success_rate >= 50:
            color = "orange"
        else:
            color = "red"
        st.markdown(f"**Success Rate:** <span style='color:{color}; font-size:1.5em; font-weight:bold'>{opt_success_rate:.1f}%</span>", unsafe_allow_html=True)
        
        # Only show median years if success rate < 50%
        if opt_success_rate < 50:
            st.metric("Median depletion year (for failures)", f"{opt_median_years:.1f}", help="Median years until corpus depletion in failed simulations")
        
        st.caption("Return: 12% | Volatility: 22%")
        st.caption("Inflation: 5% | Volatility: 2.5%")
    
    # Realistic Scenario
    with col2:
        st.markdown("#### ⚖️ Realistic")
        
        # Color code success rate
        if real_success_rate > 80:
            color = "green"
        elif real_success_rate >= 50:
            color = "orange"
        else:
            color = "red"
        st.markdown(f"**Success Rate:** <span style='color:{color}; font-size:1.5em; font-weight:bold'>{real_success_rate:.1f}%</span>", unsafe_allow_html=True)
        
        # Only show median years if success rate < 50%
        if real_success_rate < 50:
            st.metric("Median depletion year (for failures)", f"{real_median_years:.1f}", help="Median years until corpus depletion in failed simulations")
        
        st.caption("Return: 10% | Volatility: 16%")
        st.caption("Inflation: 6% | Volatility: 3%")
    
    # Pessimistic Scenario
    with col3:
        st.markdown("#### 🌧️ Pessimistic")
        pess_results = scenario_results['Pessimistic']
        pess_median_years = pess_results['median_years']
        pess_years = np.array(pess_results['years_lasted'])
        pess_success_rate = (pess_years >= max_retirement_years).sum() / len(pess_years) * 100
        
        # Color code success rate
        if pess_success_rate > 80:
            color = "green"
        elif pess_success_rate >= 50:
            color = "orange"
        else:
            color = "red"
        st.markdown(f"**Success Rate:** <span style='color:{color}; font-size:1.5em; font-weight:bold'>{pess_success_rate:.1f}%</span>", unsafe_allow_html=True)
        
        # Only show median years if success rate < 50%
        if pess_success_rate < 50:
            st.metric("Median depletion year (for failures)", f"{pess_median_years:.1f}", help="Median years until corpus depletion in failed simulations")
        
        st.caption("Return: 7% | Volatility: 10%")
        st.caption("Inflation: 8% | Volatility: 4%")
    
    st.divider()
    
    # Methodology explanation
    with st.expander("🔍 Methodology & Assumptions"):
        st.markdown(f"""
        **Monte Carlo Simulation Details:**
        
        - **Number of Simulations per Scenario:** 1,000
        - **Total Simulations:** 3,000 (across all three scenarios)
        - **Distribution Model:** Log-normal distribution
        
        **Scenario Parameters:**
        
        **Optimistic (Aggressive, Equity-Heavy):** Best-case market conditions
        - Return: 12% (volatility: 22%)
        - Inflation: 5% (volatility: 2.5%)
        
        **Realistic (Balanced, 60/40 Stocks/Bonds):** Moderate market conditions  
        - Return: 10% (volatility: 16%)
        - Inflation: 6% (volatility: 3%)
        
        **Pessimistic (Conservative, Debt-Heavy):** Challenging market conditions
        - Return: 7% (volatility: 10%)
        - Inflation: 8% (volatility: 4%)
        
        **Why Log-Normal Distribution?**
        - Ensures rates are always positive
        - Better models compound returns
        - Standard in financial modeling
        
        **Key Assumptions:**
        - Monthly expenses increase with inflation each year
        - Investment returns are applied annually
        - No additional contributions during retirement
        - Corpus is depleted when it reaches zero
        
        **Success Rate:** Percentage of simulations where corpus lasted the full retirement period ({max_retirement_years} years)
        
        **Median Years:** The middle value across all simulations - half lasted longer, half lasted shorter
        """)
    
    # Footer with LinkedIn link
    st.markdown("---")
    st.markdown(
        "Built by Nikunj - [Connect on LinkedIn](https://www.linkedin.com/in/parikhnikunj/)",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
