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
        "Retirement Age", 
        min_value=40, 
        max_value=90, 
        value=60, 
        step=1,
        help="Age at which you plan to retire"
    )
    
    life_expectancy = st.slider(
        "Expected Life Expectancy",
        min_value=70,
        max_value=90,
        value=80,
        step=1,
        help="Your expected life expectancy in years"
    )
    
    target_corpus = st.number_input(
        "Retirement Corpus", 
        min_value=100000, 
        max_value=1000000000, 
        value=10000000, 
        step=100000,
        help="Your retirement corpus amount"
    )
    st.caption(f"💡 That's **{format_indian_number(target_corpus)}**")
    
    monthly_expenses = st.number_input(
        "Monthly Expenses at Retirement", 
        min_value=10000, 
        max_value=10000000, 
        value=50000, 
        step=5000,
        help="Expected monthly expenses when you retire (will be adjusted for inflation)"
    )
    st.caption(f"💡 That's **{format_indian_number(monthly_expenses)}** per month")
    
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
                display_results(scenario_results, retirement_age, life_expectancy, target_corpus, max_retirement_years)
    else:
        st.info("👆 Configure your parameters and click 'Run Simulation' to see results")

def display_results(scenario_results, retirement_age, life_expectancy, target_corpus, max_retirement_years):
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
        st.warning(f"""
        ## ⚠️ Your Corpus May Be Borderline
        
        Based on our realistic scenario, your corpus has only a **{real_success_rate:.1f}% success rate** of lasting your full retirement. The median duration is **{real_median_years:.1f} years** (vs {max_retirement_years} years needed).
        
        **Recommended Actions:**
        - 💰 Increase your retirement corpus
        - 📉 Reduce planned monthly expenses
        - 📋 Have a backup plan for later retirement years
        """)
    else:
        # Calculate rough estimate of required corpus based on realistic scenario
        if real_median_years > 0:
            estimated_multiplier = max_retirement_years / real_median_years
            required_corpus = target_corpus * estimated_multiplier
            required_corpus_formatted = format_indian_number(required_corpus)
            shortage_formatted = format_indian_number(required_corpus - target_corpus)
            
            st.error(f"""
            ## ⚠️ Your Corpus Is Likely Insufficient
            
            Based on our realistic scenario, your corpus has only a **{real_success_rate:.1f}% success rate**. The median duration is **{real_median_years:.1f} years** (vs {max_retirement_years} years needed).
            
            ### 🎯 Target Corpus: **{required_corpus_formatted}**  
            *(You need an additional **{shortage_formatted}**)*
            
            **Recommended Actions:**
            - 💰 Substantially increase your retirement savings
            - 📉 Significantly reduce monthly expenses  
            - ⏰ Delay retirement to save more
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
        
        st.metric("Success Rate", f"{opt_success_rate:.1f}%", help="% of simulations where money lasted full retirement")
        st.metric("Median Years", f"{opt_median_years:.1f}", help="Median years until corpus depletion across all simulations")
        
        st.caption("Return: 12% | Volatility: 22%")
        st.caption("Inflation: 5% | Volatility: 2.5%")
    
    # Realistic Scenario
    with col2:
        st.markdown("#### ⚖️ Realistic")
        
        st.metric("Success Rate", f"{real_success_rate:.1f}%", help="% of simulations where money lasted full retirement")
        st.metric("Median Years", f"{real_median_years:.1f}", help="Median years until corpus depletion across all simulations")
        
        st.caption("Return: 10% | Volatility: 16%")
        st.caption("Inflation: 6% | Volatility: 3%")
    
    # Pessimistic Scenario
    with col3:
        st.markdown("#### 🌧️ Pessimistic")
        pess_results = scenario_results['Pessimistic']
        pess_median_years = pess_results['median_years']
        pess_years = np.array(pess_results['years_lasted'])
        pess_success_rate = (pess_years >= max_retirement_years).sum() / len(pess_years) * 100
        
        st.metric("Success Rate", f"{pess_success_rate:.1f}%", help="% of simulations where money lasted full retirement")
        st.metric("Median Years", f"{pess_median_years:.1f}", help="Median years until corpus depletion across all simulations")
        
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
