import streamlit as st
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
    
    expected_inflation = st.slider(
        "Expected Inflation Rate (%)", 
        min_value=1.0, 
        max_value=15.0, 
        value=6.0, 
        step=0.1,
        help="Expected average annual inflation rate"
    )
    
    inflation_volatility = st.slider(
        "Inflation Volatility (%)", 
        min_value=0.5, 
        max_value=10.0, 
        value=3.0, 
        step=0.5,
        help="Uncertainty in inflation rate - higher values mean more variable inflation"
    )
    
    expected_return = st.slider(
        "Expected Return Rate (%)", 
        min_value=1.0, 
        max_value=20.0, 
        value=10.0, 
        step=0.1,
        help="Expected average annual return on investment"
    )
    
    return_volatility = st.slider(
        "Return Volatility (%)", 
        min_value=0.5, 
        max_value=20.0, 
        value=12.0, 
        step=0.5,
        help="Uncertainty in returns - higher values mean more variable returns (typical stock market ~15%)"
    )
    
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
            
            with st.spinner("Running Monte Carlo simulation..."):
                # Initialize simulator with target corpus
                simulator = MonteCarloSimulator(
                    current_corpus=target_corpus,
                    monthly_expenses=monthly_expenses,
                    expected_inflation=expected_inflation / 100,
                    expected_return=expected_return / 100,
                    inflation_volatility=inflation_volatility / 100,
                    return_volatility=return_volatility / 100,
                    num_simulations=2500,
                    max_years=max_retirement_years
                )
                
                # Run simulation
                results = simulator.run_simulation()
                
                # Display results
                display_results(results, retirement_age, life_expectancy, simulator, target_corpus)
    else:
        st.info("👆 Configure your parameters and click 'Run Simulation' to see results")

def display_results(results, retirement_age, life_expectancy, simulator, target_corpus):
    st.header("📈 Simulation Results")
    
    # Primary summary sentence
    median_years = results['median_years']
    optimistic_years = results['optimistic_years']
    conservative_years = results['pessimistic_years']
    corpus_formatted = format_indian_number(target_corpus)
    max_retirement_years = life_expectancy - retirement_age
    
    # Check if corpus survives the full retirement period in all scenarios
    if results.get('all_scenarios_survive', False):
        # Show remaining corpus values instead of years
        final_conservative = format_indian_number(results['final_corpus_conservative'])
        final_median = format_indian_number(results['final_corpus_median'])
        final_optimistic = format_indian_number(results['final_corpus_optimistic'])
        
        st.markdown(f"""
        ### Summary
        🎉 **Great News!** Your retirement corpus of **{corpus_formatted}** is sufficient to cover your entire retirement period of **{max_retirement_years} years** (from age {retirement_age} to {life_expectancy}) in all scenarios. 
        
        At the end of your retirement period, your remaining corpus would be:
        - **{final_median}** in the median scenario
        - **{final_optimistic}** in the optimistic scenario  
        - **{final_conservative}** in the conservative scenario
        """)
    else:
        # Show years lasted (original behavior)
        # Check if values are very close (within 0.5 years) - if so, show more precision
        year_range = max(median_years, optimistic_years, conservative_years) - min(median_years, optimistic_years, conservative_years)
        if year_range < 0.5:
            # Values are very close, show 2 decimal places for clarity
            st.markdown(f"""
            ### Summary
            Based on the data you shared, your retirement corpus of **{corpus_formatted}** is expected to last **{median_years:.2f} years** in the median scenario, **{optimistic_years:.2f} years** in the optimistic scenario, and **{conservative_years:.2f} years** in the conservative scenario.
            """)
        else:
            # Values differ meaningfully, show 1 decimal place
            st.markdown(f"""
            ### Summary
            Based on the data you shared, your retirement corpus of **{corpus_formatted}** is expected to last **{median_years:.1f} years** in the median scenario, **{optimistic_years:.1f} years** in the optimistic scenario, and **{conservative_years:.1f} years** in the conservative scenario.
            """)
    
    st.markdown("---")
    
    # Explanation of scenarios
    st.subheader("📖 Understanding the Scenarios")
    
    st.markdown("""
    **Conservative Scenario**  
    This represents a cautious outlook where investment returns are lower than expected and inflation is higher. 
    There's a 75% chance your corpus will last at least this long. Use this for safe planning.
    """)
    
    st.markdown("""
    **Median Scenario**  
    This is the middle outcome - half of all simulations show better results, half show worse. 
    It's the most likely scenario based on your assumptions. A balanced view for planning.
    """)
    
    st.markdown("""
    **Optimistic Scenario**  
    This represents favorable conditions with higher returns and lower inflation. 
    There's a 25% chance your corpus will last this long or more. Don't rely on this alone.
    """)
    
    st.markdown("---")
    
    # Recommendations Section
    st.subheader("💡 Recommendations")
    
    # Check if corpus is sufficient for full retirement
    if conservative_years >= max_retirement_years:
        st.success(f"""
        ✅ **Your corpus is sufficient!** 
        
        Your retirement corpus of **{corpus_formatted}** is enough to cover your entire retirement period of **{max_retirement_years} years** (age {retirement_age} to {life_expectancy}) even in the conservative scenario.
        
        You can retire with confidence knowing your savings will likely last throughout your retirement.
        """)
    elif conservative_years < max_retirement_years * 0.25:
        # Corpus lasts less than 25% of retirement period - too large a deficit for meaningful estimate
        st.error(f"""
        ⚠️ **Your corpus is significantly insufficient!**
        
        In the conservative scenario, your corpus of **{corpus_formatted}** will only last **{conservative_years:.1f} years** out of the **{max_retirement_years} years** you need (age {retirement_age} to {life_expectancy}).
        
        **The gap is too large to provide a reliable estimate of required corpus.**
        
        Your corpus covers less than 25% of your retirement period. Consider a comprehensive review of your retirement strategy:
        - Substantially increase your retirement savings
        - Significantly reduce planned monthly expenses
        - Delay retirement to accumulate more savings
        - Re-evaluate your retirement timeline and goals
        """)
    else:
        # Calculate required corpus for full retirement
        # Proportional scaling based on conservative scenario
        years_shortage = max_retirement_years - conservative_years
        required_corpus = target_corpus * (max_retirement_years / conservative_years)
        required_corpus_formatted = format_indian_number(required_corpus)
        shortage = required_corpus - target_corpus
        shortage_formatted = format_indian_number(shortage)
        
        st.error(f"""
        ⚠️ **Your corpus may not be sufficient!**
        
        In the conservative scenario, your current corpus of **{corpus_formatted}** will only last **{conservative_years:.1f} years** out of the **{max_retirement_years} years** you need (age {retirement_age} to {life_expectancy}).
        
        **You may face a shortage of approximately {years_shortage:.1f} years.**
        
        **Estimated Target Corpus Required:** **{required_corpus_formatted}**  
        (Additional **{shortage_formatted}** needed)
        
        Consider:
        - Increasing your retirement corpus
        - Reducing monthly expenses
        - Delaying retirement
        - Adjusting your investment strategy for better returns
        """)
    
    st.markdown("---")
    
    # Methodology explanation
    with st.expander("🔍 Methodology & Assumptions"):
        st.markdown(f"""
        **Monte Carlo Simulation Details:**
        
        - **Number of Simulations:** {simulator.num_simulations:,}
        - **Expected Inflation:** {simulator.expected_inflation*100:.1f}% (volatility: {simulator.inflation_volatility*100:.1f}%)
        - **Expected Return:** {simulator.expected_return*100:.1f}% (volatility: {simulator.return_volatility*100:.1f}%)
        - **Distribution Model:** Log-normal distribution
        
        **Why Log-Normal Distribution?**
        - Ensures rates are always positive (no impossible negative returns)
        - Better models the multiplicative nature of compound returns
        - Standard in financial modeling (Black-Scholes, stock prices, etc.)
        - Realistic asymmetry: +50% and -50% returns are NOT equivalent
        
        **Key Assumptions:**
        - Monthly expenses increase with inflation each year
        - Investment returns are applied annually
        - No additional contributions to corpus during retirement
        - Corpus is depleted when it reaches zero
        
        **Confidence Intervals:**
        - Conservative (25th percentile): 75% chance corpus lasts at least this long
        - Median (50th percentile): Most likely scenario
        - Optimistic (75th percentile): 25% chance corpus lasts this long or more
        
        **Risk Assessment:**
        - Success rate shows probability of corpus lasting 20+ years
        - Higher volatility = wider range of possible outcomes
        - Consider conservative estimates for retirement planning
        """)
    
    # Footer with LinkedIn link
    st.markdown("---")
    st.markdown(
        "Built by Nikunj - [Connect on LinkedIn](https://www.linkedin.com/in/parikhnikunj/)",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
