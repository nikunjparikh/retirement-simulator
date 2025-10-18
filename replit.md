# Retirement Corpus Calculator

## Overview

This project is a Streamlit-based Monte Carlo simulation application designed to help users estimate the longevity of their retirement savings. By inputting just five core parameters (current age, retirement age, life expectancy, retirement corpus, and monthly expenses), the app runs 3,000 simulations across three hardcoded scenarios (Optimistic, Realistic, Pessimistic). It provides side-by-side results showing success rates and median years, along with smart, actionable recommendations based on the realistic scenario, aiming to make complex financial planning accessible and intuitive.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### UI/UX Decisions
- **Technology**: Streamlit for rapid development and data-driven application UI.
- **Layout**: Mobile-first, single-column vertical layout for optimal responsiveness, removing all `st.columns()` and `layout="wide"`. Dividers improve visual hierarchy.
- **Number Formatting**: Implemented Indian numbering system (Crores, Lakhs, Thousands) for better regional relevance, with captions below inputs for clarity.
- **Currency Display**: Removed all explicit currency symbols for cleaner presentation.
- **Results Display**: Simplified to a single sentence summary, plain-language scenario explanations, and prominent, actionable recommendations with color-coded success rates. Conditional display of median depletion years for failed scenarios.
- **Simplification**: Removed complex visualizations (Corpus Trajectory and Distribution charts) and user-configurable volatility parameters based on user feedback to streamline the interface.

### Technical Implementations
- **Core Simulation**: Monte Carlo simulation utilizing NumPy for stochastic modeling.
- **Stochastic Modeling**: Employs a log-normal distribution for generating inflation and return rates, ensuring positive rates and realistic asymmetry in financial returns.
- **Scenarios**: Three hardcoded scenarios (Optimistic, Realistic, Pessimistic) with fixed return rates, inflation rates, and volatilities, each running 1,000 simulations (3,000 total).
  - Optimistic: Return 12% (volatility 22%), Inflation 5% (volatility 2.5%)
  - Realistic: Return 10% (volatility 16%), Inflation 6% (volatility 3%)
  - Pessimistic: Return 7% (volatility 10%), Inflation 8% (volatility 4%)
- **Simulation Precision**: Changed to monthly tracking for fractional year accuracy and enhanced scenario differentiation.
- **Recommendations Logic**: Smart recommendations based on the Realistic scenario using binary search algorithms to calculate precise targets for 80% success rate. Three risk categories: Safe (≥80%), Moderate (70-79%), High (<70%). Uses achievability pre-checks with Monte Carlo variance safeguards to ensure accurate guidance.

### System Design Choices
- **Modular Architecture**: Separates concerns into `app.py` (UI, input, recommendations) and `monte_carlo.py` (simulation logic, calculations) for maintainability.
- **Stateless Design**: All calculations are performed in-memory; no persistent data storage is used.
- **Deployment**: Designed for deployment on platforms like Replit, compatible with Streamlit applications.

## External Dependencies

- **Streamlit**: Web application framework for UI rendering and interaction.
- **NumPy**: For numerical computing, random number generation, and statistical operations within the simulation engine.