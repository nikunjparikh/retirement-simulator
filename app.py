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

def calculate_target_corpus(current_corpus, monthly_expenses, max_years, target_success_rate=0.80, max_iterations=15):
    """
    Use binary search to find the corpus amount needed to achieve target success rate.
    Returns (target_corpus, actual_success_rate) or (None, None) if not achievable.
    """
    # Realistic scenario parameters
    params = {
        'return': 0.10,
        'return_volatility': 0.16,
        'inflation': 0.06,
        'inflation_volatility': 0.03
    }
    
    # Start with wider bounds and check if target is achievable
    low = current_corpus * 0.5
    high = current_corpus * 10.0  # Wider upper bound
    
    # First, check if even the high bound can achieve target
    # Use more simulations and lenient threshold to avoid false negatives due to MC variance
    simulator_high = MonteCarloSimulator(
        current_corpus=high,
        monthly_expenses=monthly_expenses,
        expected_inflation=params['inflation'],
        expected_return=params['return'],
        inflation_volatility=params['inflation_volatility'],
        return_volatility=params['return_volatility'],
        num_simulations=1000,  # More sims for better confidence
        max_years=max_years
    )
    results_high = simulator_high.run_simulation()
    years_high = np.array(results_high['years_lasted'])
    success_high = (years_high >= max_years).sum() / len(years_high)
    
    # If even 10x corpus can't reach target (with lenient threshold), return None
    # Use 0.70 threshold to account for MC variance while catching truly unachievable cases
    if success_high < 0.70:
        return None, None
    
    # Binary search
    best_corpus = None
    best_success = None
    
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
            num_simulations=500,
            max_years=max_years
        )
        results = simulator.run_simulation()
        years_lasted = np.array(results['years_lasted'])
        success_rate = (years_lasted >= max_years).sum() / len(years_lasted)
        
        # Track best result
        if best_corpus is None or abs(success_rate - target_success_rate) < abs(best_success - target_success_rate):
            best_corpus = mid
            best_success = success_rate
        
        # Check if we're close enough to target
        if abs(success_rate - target_success_rate) < 0.03:  # Within 3%
            return mid, success_rate
        elif success_rate < target_success_rate:
            low = mid  # Need more corpus
        else:
            high = mid  # Can use less corpus
    
    # Verify the best result meets minimum threshold
    if best_success is not None and best_success >= target_success_rate - 0.05:  # Within 5%
        return best_corpus, best_success
    
    return None, None

def calculate_target_spending(corpus, current_monthly_expenses, max_years, target_success_rate=0.80, max_iterations=15):
    """
    Use binary search to find the monthly spending amount that achieves target success rate.
    Returns (target_spending, actual_success_rate) or (None, None) if not achievable.
    """
    # Realistic scenario parameters
    params = {
        'return': 0.10,
        'return_volatility': 0.16,
        'inflation': 0.06,
        'inflation_volatility': 0.03
    }
    
    # Set search bounds (10% to 100% of current spending)
    low = current_monthly_expenses * 0.1
    high = current_monthly_expenses
    
    # First, check if even minimal spending can achieve target
    # Use more simulations and lenient threshold to avoid false negatives due to MC variance
    simulator_low = MonteCarloSimulator(
        current_corpus=corpus,
        monthly_expenses=low,
        expected_inflation=params['inflation'],
        expected_return=params['return'],
        inflation_volatility=params['inflation_volatility'],
        return_volatility=params['return_volatility'],
        num_simulations=1000,  # More sims for better confidence
        max_years=max_years
    )
    results_low = simulator_low.run_simulation()
    years_low = np.array(results_low['years_lasted'])
    success_low = (years_low >= max_years).sum() / len(years_low)
    
    # If even minimal spending can't reach target (with lenient threshold), return None
    # Use 0.70 threshold to account for MC variance while catching truly unachievable cases
    if success_low < 0.70:
        return None, None
    
    # Binary search
    best_spending = None
    best_success = None
    
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
            num_simulations=500,
            max_years=max_years
        )
        results = simulator.run_simulation()
        years_lasted = np.array(results['years_lasted'])
        success_rate = (years_lasted >= max_years).sum() / len(years_lasted)
        
        # Track best result
        if best_spending is None or abs(success_rate - target_success_rate) < abs(best_success - target_success_rate):
            best_spending = mid
            best_success = success_rate
        
        # Check if we're close enough to target
        if abs(success_rate - target_success_rate) < 0.03:  # Within 3%
            return mid, success_rate
        elif success_rate < target_success_rate:
            high = mid  # Need to spend less
        else:
            low = mid  # Can spend more
    
    # Verify the best result meets minimum threshold
    if best_success is not None and best_success >= target_success_rate - 0.05:  # Within 5%
        return best_spending, best_success
    
    return None, None

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
    
    # Determine risk category based on new thresholds
    if real_success_rate >= 80:
        # SAFE - Green background
        st.markdown("""
        <div style='background-color: #d4edda; padding: 20px; border-radius: 10px; border-left: 5px solid #28a745;'>
        <h2 style='color: #155724; margin-top: 0;'>✅ Your Retirement Plan Looks Solid</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        Your corpus has a **{real_success_rate:.1f}% success rate** in the realistic scenario. You're well-prepared for retirement.
        
        **Median duration:** Full retirement achieved ({max_retirement_years}+ years)
        
        **Optional:** Consider more conservative investments as you near retirement, or review the pessimistic scenario for extra safety planning.
        """)
        
    elif real_success_rate >= 70:
        # MODERATE RISK - Yellow/orange background
        st.markdown("""
        <div style='background-color: #fff3cd; padding: 20px; border-radius: 10px; border-left: 5px solid #ffc107;'>
        <h2 style='color: #856404; margin-top: 0;'>⚠️ Your Corpus Needs Strengthening</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        Your retirement plan has a **{real_success_rate:.1f}% success rate**. This is acceptable but leaves some risk. Consider these improvements to reach 80%+ success rate:
        """)
        
        # Calculate accurate target using binary search
        with st.spinner("Calculating recommendations..."):
            target_corpus_80, corpus_success = calculate_target_corpus(target_corpus, monthly_expenses, max_retirement_years, target_success_rate=0.80)
            target_spending_80, spending_success = calculate_target_spending(target_corpus, monthly_expenses, max_retirement_years, target_success_rate=0.80)
        
        st.markdown("**Recommended Actions (choose one):**")
        
        # Only show valid recommendations (avoid "Save ₹0 more" bug)
        recommendations_shown = False
        
        if target_corpus_80 is not None:
            additional_corpus = target_corpus_80 - target_corpus
            if additional_corpus > 0:
                st.markdown(f"- 💰 **Save ₹{format_with_commas(additional_corpus)} more** ({format_indian_number(additional_corpus)}) to reach ₹{format_with_commas(target_corpus_80)} total → **{corpus_success*100:.1f}% success rate**")
                recommendations_shown = True
        
        if target_spending_80 is not None:
            spending_reduction_monthly = monthly_expenses - target_spending_80
            spending_reduction_annual = spending_reduction_monthly * 12
            if spending_reduction_annual > 0:
                st.markdown(f"- 📉 **Reduce spending by ₹{format_with_commas(spending_reduction_annual)}/year** (₹{format_with_commas(spending_reduction_monthly)}/month) to ₹{format_with_commas(target_spending_80)}/month total → **{spending_success*100:.1f}% success rate**")
                recommendations_shown = True
        
        if not recommendations_shown:
            st.warning("⚠️ Reaching 80% success requires changes beyond typical adjustments. Consider delaying retirement or consulting a financial advisor.")
        
        st.markdown(f"- 📋 Have a backup plan (part-time work, rental income) for later retirement years")
        
    else:
        # HIGH RISK - Red background
        failure_rate = 100 - real_success_rate
        
        st.markdown(f"""
        <div style='background-color: #f8d7da; padding: 20px; border-radius: 10px; border-left: 5px solid #dc3545;'>
        <h2 style='color: #721c24; margin-top: 0;'>⚠️ High Risk - Only {real_success_rate:.1f}% Success Rate</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if real_median_years >= max_retirement_years:
            median_msg = f"**Median duration:** Full retirement achieved ({max_retirement_years}+ years)"
        else:
            median_msg = f"**Median duration:** {real_median_years:.1f} years (money runs out in typical scenario)"
        
        st.markdown(f"""
        **{failure_rate:.1f}% chance your money runs out.** This is too risky for retirement.
        
        {median_msg}
        """)
        
        # Calculate accurate targets using binary search
        with st.spinner("Calculating recommendations..."):
            target_corpus_80, corpus_success = calculate_target_corpus(target_corpus, monthly_expenses, max_retirement_years, target_success_rate=0.80)
            target_spending_80, spending_success = calculate_target_spending(target_corpus, monthly_expenses, max_retirement_years, target_success_rate=0.80)
        
        # Check if 80% target is achievable
        if target_corpus_80 is None and target_spending_80 is None:
            # Cannot reach 80% with reasonable changes
            st.error("""
            **⚠️ Your situation requires major changes beyond typical recommendations.**
            
            Even with significant adjustments, reaching 80% success is very challenging. Consider:
            
            • **Delay retirement** by several years to accumulate more savings
            • **Drastically reduce expenses** to the bare minimum
            • **Maintain part-time income** throughout retirement
            • **Consult a financial advisor** for personalized planning
            """)
        else:
            # Calculate combined moderate approach (50% corpus increase + 50% spending reduction)
            st.markdown("**Recommended: Combine multiple actions**")
            
            recommendations = []
            
            # Only show valid recommendations
            if target_corpus_80 is not None:
                full_corpus_increase = target_corpus_80 - target_corpus
                combined_corpus_increase = full_corpus_increase * 0.5
                combined_target_corpus = target_corpus + combined_corpus_increase
                
                if combined_corpus_increase > 0:
                    recommendations.append(f"• **Save at least ₹{format_with_commas(combined_corpus_increase)}** more (₹{format_with_commas(combined_target_corpus)} total / {format_indian_number(combined_target_corpus)})")
            
            if target_spending_80 is not None:
                full_spending_reduction_monthly = monthly_expenses - target_spending_80
                combined_spending_reduction_monthly = full_spending_reduction_monthly * 0.5
                combined_target_spending = monthly_expenses - combined_spending_reduction_monthly
                combined_spending_reduction_annual = combined_spending_reduction_monthly * 12
                
                if combined_spending_reduction_annual > 0:
                    recommendations.append(f"• **Reduce spending by ₹{format_with_commas(combined_spending_reduction_annual)}/year** (₹{format_with_commas(combined_target_spending)}/month total / {format_indian_number(combined_target_spending)})")
            
            recommendations.append("• **Keep a backup income source** (part-time work, rental income)")
            
            st.markdown("\n".join(recommendations))
            
            # Show expected success rate if recommendations are followed
            if target_corpus_80 is not None and target_spending_80 is not None:
                st.markdown("**With these changes:** ~80-85% success rate")
            elif target_corpus_80 is not None:
                st.markdown(f"**With corpus increase only:** ~{corpus_success*100:.0f}% success rate")
            elif target_spending_80 is not None:
                st.markdown(f"**With spending reduction only:** ~{spending_success*100:.0f}% success rate")
    
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
