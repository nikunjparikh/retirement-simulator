import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from monte_carlo import MonteCarloSimulator
from visualization import create_corpus_chart, create_distribution_chart

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
        current_age = st.number_input(
            "Current Age", 
            min_value=18, 
            max_value=100, 
            value=50, 
            step=1,
            help="Your current age in years"
        )
        
        current_corpus = st.number_input(
            "Current Corpus (₹)", 
            min_value=100000, 
            max_value=100000000, 
            value=10000000, 
            step=100000,
            help="Your total retirement savings in Indian Rupees"
        )
        
        monthly_expenses = st.number_input(
            "Monthly Expenses (₹)", 
            min_value=10000, 
            max_value=1000000, 
            value=50000, 
            step=5000,
            help="Current monthly expenses (will be adjusted for inflation)"
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
            with st.spinner("Running Monte Carlo simulation..."):
                # Initialize simulator
                simulator = MonteCarloSimulator(
                    current_corpus=current_corpus,
                    monthly_expenses=monthly_expenses,
                    expected_inflation=expected_inflation / 100,
                    expected_return=expected_return / 100,
                    num_simulations=num_simulations
                )
                
                # Run simulation
                results = simulator.run_simulation()
                
                # Display results
                display_results(results, current_age, simulator)
        else:
            st.info("👆 Configure your parameters and click 'Run Simulation' to see results")

def display_results(results, current_age, simulator):
    st.header("📈 Simulation Results")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Median Years",
            f"{results['median_years']:.1f}",
            help="50% probability of lasting this long"
        )
    
    with col2:
        st.metric(
            "Conservative (25th %ile)",
            f"{results['pessimistic_years']:.1f}",
            help="75% probability of lasting at least this long"
        )
    
    with col3:
        st.metric(
            "Optimistic (75th %ile)",
            f"{results['optimistic_years']:.1f}",
            help="25% probability of lasting this long or more"
        )
    
    with col4:
        success_rate = results['success_rate']
        st.metric(
            "Success Rate (20+ years)",
            f"{success_rate:.1f}%",
            help="Probability corpus lasts 20+ years"
        )
    
    # Retirement age estimates
    st.subheader("🎯 Retirement Age Estimates")
    retirement_col1, retirement_col2, retirement_col3 = st.columns(3)
    
    with retirement_col1:
        st.info(f"**Conservative Scenario**\nRetire at age: {current_age + results['pessimistic_years']:.0f}")
    
    with retirement_col2:
        st.success(f"**Median Scenario**\nRetire at age: {current_age + results['median_years']:.0f}")
    
    with retirement_col3:
        st.warning(f"**Optimistic Scenario**\nRetire at age: {current_age + results['optimistic_years']:.0f}")
    
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
