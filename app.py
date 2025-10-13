import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from monte_carlo import MonteCarloSimulator
from visualization import create_corpus_chart, create_distribution_chart

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
        page_icon="💰",
        layout="wide"
    )
    
    st.title("💰 Retirement Corpus Calculator")
    st.markdown("### Monte Carlo Simulation for Retirement Planning")
    st.markdown("Estimate how long your savings will last under varying market conditions")
    
    # Create columns for input form
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📊 Input Parameters")
        
        # User inputs
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
        
        current_corpus = st.number_input(
            "Current Retirement Corpus", 
            min_value=100000, 
            max_value=1000000000, 
            value=10000000, 
            step=100000,
            help="Your total retirement savings"
        )
        
        monthly_expenses = st.number_input(
            "Monthly Expenses at Retirement", 
            min_value=10000, 
            max_value=10000000, 
            value=50000, 
            step=5000,
            help="Expected monthly expenses when you retire (will be adjusted for inflation)"
        )
        
        expected_inflation = st.slider(
            "Expected Inflation Rate (%)", 
            min_value=1.0, 
            max_value=15.0, 
            value=6.0, 
            step=0.1,
            help="Expected annual inflation rate (±3% variance will be applied)"
        )
        
        expected_return = st.slider(
            "Expected Return Rate (%)", 
            min_value=1.0, 
            max_value=20.0, 
            value=10.0, 
            step=0.1,
            help="Expected annual return on investment (±3% variance will be applied)"
        )
        
        num_simulations = st.selectbox(
            "Number of Simulations",
            [1000, 2500, 5000, 10000],
            index=1,
            help="Higher numbers provide more accurate results but take longer"
        )
        
        run_simulation = st.button("🚀 Run Simulation", type="primary")
    
    with col2:
        if run_simulation:
            # Validate that life expectancy is greater than retirement age
            if life_expectancy <= retirement_age:
                st.error("⚠️ Life expectancy must be greater than retirement age!")
            else:
                max_retirement_years = life_expectancy - retirement_age
                
                with st.spinner("Running Monte Carlo simulation..."):
                    # Initialize simulator
                    simulator = MonteCarloSimulator(
                        current_corpus=current_corpus,
                        monthly_expenses=monthly_expenses,
                        expected_inflation=expected_inflation / 100,
                        expected_return=expected_return / 100,
                        num_simulations=num_simulations,
                        max_years=max_retirement_years
                    )
                    
                    # Run simulation
                    results = simulator.run_simulation()
                    
                    # Display results
                    display_results(results, retirement_age, life_expectancy, simulator)
        else:
            st.info("👆 Configure your parameters and click 'Run Simulation' to see results")

def display_results(results, retirement_age, life_expectancy, simulator):
    st.header("📈 Simulation Results")
    
    # Primary summary sentence
    median_years = results['median_years']
    optimistic_years = results['optimistic_years']
    conservative_years = results['pessimistic_years']
    corpus_formatted = format_indian_number(simulator.current_corpus)
    
    st.markdown(f"""
    ### Summary
    Based on the data you shared, your current retirement corpus of **{corpus_formatted}** is expected to last **{median_years:.1f} years** in the median scenario, **{optimistic_years:.1f} years** in the optimistic scenario, and **{conservative_years:.1f} years** in the conservative scenario.
    """)
    
    st.markdown("---")
    
    # Explanation of scenarios
    st.subheader("📖 Understanding the Scenarios")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Conservative Scenario**  
        This represents a cautious outlook where investment returns are lower than expected and inflation is higher. 
        There's a 75% chance your corpus will last at least this long. Use this for safe planning.
        """)
    
    with col2:
        st.markdown("""
        **Median Scenario**  
        This is the middle outcome - half of all simulations show better results, half show worse. 
        It's the most likely scenario based on your assumptions. A balanced view for planning.
        """)
    
    with col3:
        st.markdown("""
        **Optimistic Scenario**  
        This represents favorable conditions with higher returns and lower inflation. 
        There's a 25% chance your corpus will last this long or more. Don't rely on this alone.
        """)
    
    st.markdown("---")
    
    # Age-based interpretation
    st.subheader("🎯 What This Means For You")
    
    max_possible_years = life_expectancy - retirement_age
    
    interpretation_col1, interpretation_col2 = st.columns([2, 1])
    
    with interpretation_col1:
        if conservative_years >= max_possible_years:
            st.success(f"""
            **Excellent News!** Even in the conservative scenario, your corpus is projected to last your entire retirement 
            (from age {retirement_age} to {life_expectancy}). Your retirement plan appears very solid.
            """)
        elif median_years >= max_possible_years:
            st.info(f"""
            **Good Position:** Your corpus is likely to last through retirement in the median scenario. However, the 
            conservative scenario suggests it may run out around age {retirement_age + conservative_years:.0f}. 
            Consider building a bit more cushion.
            """)
        elif conservative_years < max_possible_years * 0.6:
            st.error(f"""
            **Needs Attention:** In the conservative scenario, your corpus may only last until age {retirement_age + conservative_years:.0f}, 
            which is {max_possible_years - conservative_years:.0f} years short of your life expectancy. 
            You may need to increase savings, reduce expenses, or delay retirement.
            """)
        else:
            st.warning(f"""
            **Moderate Risk:** Your corpus shows reasonable sustainability in median scenarios, but conservative projections 
            suggest potential shortfall around age {retirement_age + conservative_years:.0f}. 
            Consider strengthening your retirement plan.
            """)
    
    with interpretation_col2:
        # Key metrics box
        st.metric("Retirement Age", f"{retirement_age} years")
        st.metric("Life Expectancy", f"{life_expectancy} years")
        st.metric("Retirement Period", f"{max_possible_years} years")
    
    # Charts
    st.subheader("📊 Corpus Trajectory Over Time")
    corpus_chart = create_corpus_chart(results['simulation_data'])
    st.plotly_chart(corpus_chart, use_container_width=True)
    
    st.subheader("📈 Distribution of Corpus Longevity")
    distribution_chart = create_distribution_chart(results['years_lasted'])
    st.plotly_chart(distribution_chart, use_container_width=True)
    
    # Methodology explanation
    with st.expander("🔍 Methodology & Assumptions"):
        st.markdown(f"""
        **Monte Carlo Simulation Details:**
        
        - **Number of Simulations:** {simulator.num_simulations:,}
        - **Inflation Rate Range:** {(simulator.expected_inflation - 0.03)*100:.1f}% to {(simulator.expected_inflation + 0.03)*100:.1f}%
        - **Return Rate Range:** {(simulator.expected_return - 0.03)*100:.1f}% to {(simulator.expected_return + 0.03)*100:.1f}%
        - **Distribution:** Normal distribution with ±3% standard deviation
        
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
        - Higher success rates indicate more sustainable retirement plans
        - Consider conservative estimates for retirement planning
        """)
    
    # Recommendations
    st.subheader("💡 Recommendations")
    
    if results['success_rate'] >= 80:
        st.success("""
        **Excellent Position!** Your retirement corpus shows high sustainability:
        - Your current savings plan appears very robust
        - Consider if you can retire earlier than planned
        - Monitor and rebalance your portfolio regularly
        """)
    elif results['success_rate'] >= 60:
        st.warning("""
        **Good but Room for Improvement:**
        - Your corpus shows reasonable sustainability
        - Consider increasing your corpus or reducing expenses
        - Diversify investments to manage risk better
        - Plan for conservative withdrawal rates
        """)
    else:
        st.error("""
        **Requires Attention:**
        - Current corpus may not sustain desired lifestyle
        - Strongly consider increasing savings rate
        - Explore ways to reduce monthly expenses
        - Consider delayed retirement or part-time income
        - Consult with a financial advisor
        """)

if __name__ == "__main__":
    main()
