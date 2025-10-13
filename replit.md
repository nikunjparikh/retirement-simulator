# Retirement Corpus Calculator

## Overview

This is a Monte Carlo simulation-based retirement planning application built with Streamlit. The application helps users estimate how long their retirement savings will last under varying market conditions by running multiple simulations with randomized inflation and return rates. Users can input their retirement age, life expectancy, corpus, monthly expenses, expected inflation, and expected return rates to generate probabilistic forecasts of their retirement fund longevity.

## Recent Changes (January 2025)

1. **Input Model Update**: Added dual-age input with direct corpus usage
   - **Current Age & Retirement Age**: Users now enter both current age and planned retirement age
   - **Retirement Corpus**: Users specify their retirement corpus amount directly
   - **No Inflation Adjustment**: Corpus value is used exactly as entered (no inflation calculation)
   - **Validation**: Ensures current age < retirement age < life expectancy
   - **Simplified Display**: Shows corpus amount as entered without qualifiers

2. **Number Formatting Enhancement**: Implemented Indian numbering system display
   - Added `format_indian_number()` helper function
   - Formats: Crores (Cr), Lakhs (L), and Thousands (K)
   - Examples: 10000000 → "1.00 Cr", 500000 → "5 L", 25000 → "25K"

3. **Currency Symbol Removal**: Removed all rupee (₹) symbols from the interface
   - Cleaner presentation for international users
   - Values displayed with formatted numbers only

4. **Results Presentation Redesign**:
   - **Summary**: Single sentence format showing median, optimistic, and conservative scenarios together
   - **Scenario Explanations**: "Understanding the Scenarios" section with plain-language explanations
   - **Streamlined Display**: Removed recommendations and personalized interpretation sections for cleaner presentation

5. **Mobile-First Layout Redesign**: Converted from wide two-column to vertical single-column layout
   - Removed `layout="wide"` configuration for default centered responsive layout
   - Eliminated all column-based layouts (`st.columns()`) throughout the application
   - All inputs and results now stack vertically for optimal mobile experience
   - Added dividers between sections for improved visual hierarchy
   - Run Simulation button now spans full container width
   - Charts are fully responsive (89% width on mobile, centered on desktop)
   - Metrics display inline with pipe separators instead of separate boxes
   - Tested and verified on both mobile (375px) and desktop (1280px) viewports

6. **Monte Carlo Simulation Enhancement**: Fixed scenario differentiation issue
   - **Problem**: All scenarios (median, optimistic, conservative) showed identical values when corpus lasted full retirement or depleted around same time
   - **Monthly Precision**: Changed simulation from annual to monthly tracking for fractional year accuracy
   - **Smart Survival Detection**: Changed from requiring all simulations to survive to checking if conservative (25th percentile) survives
   - **Final Corpus Tracking**: Now tracks remaining corpus when retirement period is fully covered
   - **Adaptive Display**: Shows remaining corpus values when corpus survives, fractional years when it depletes
   - **Precision Control**: Displays 2 decimals when scenarios are close (<0.5 year range), 1 decimal otherwise
   - **Result**: Scenarios now show meaningful differences (e.g., 5.3, 5.6, 5.8 years instead of all showing 6.0)

7. **Formatted Value Display**: Added caption helpers below input fields for easy comprehension
   - **Target Corpus Caption**: Shows formatted value below input (e.g., "💡 That's **1.00 Cr**")
   - **Monthly Expenses Caption**: Shows formatted value with context (e.g., "💡 That's **50.0K** per month")
   - **Auto-formatting**: Uses Indian numbering system (K for thousands, L for lakhs, Cr for crores)
   - **Dynamic Updates**: Captions update automatically when values change

8. **Log-Normal Distribution & Configurable Volatility**: Enhanced statistical modeling for more realistic simulations
   - **Log-Normal Distribution**: Switched from normal to log-normal distribution for rate generation
     - Ensures rates are always positive (no artificial flooring)
     - Better models multiplicative nature of compound returns
     - Standard in financial modeling (Black-Scholes, stock price models)
     - Realistic asymmetry: +50% and -50% returns are NOT symmetric
   - **Configurable Volatility Parameters**:
     - Inflation Volatility slider: 0.5% to 10% (default 3%)
     - Return Volatility slider: 0.5% to 20% (default 12%)
     - Higher volatility = wider range of possible outcomes
     - Users can model different market uncertainty scenarios
   - **Mathematical Implementation**:
     - Converts mean and volatility to log-normal parameters (mu, sigma)
     - mu = ln(m² / √(m² + s²))
     - sigma = √(ln(1 + (s/m)²))
     - Where m = expected rate, s = volatility

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
**Technology**: Streamlit web framework
- **Decision**: Use Streamlit for rapid development of data-driven applications
- **Rationale**: Streamlit provides built-in widgets, state management, and integrates seamlessly with data science libraries (NumPy, Pandas, Plotly)
- **Pros**: Quick prototyping, minimal boilerplate code, automatic UI updates on data changes
- **Cons**: Limited customization compared to traditional web frameworks, less control over layout

**Layout Strategy**: Wide layout with columnar design
- **Decision**: Two-column layout separating input parameters from visualizations
- **Rationale**: Improves user experience by keeping inputs accessible while displaying results
- **Alternative**: Single column layout would be simpler but less efficient for data visualization

### Data Processing & Simulation
**Core Engine**: Monte Carlo simulation using NumPy
- **Decision**: Implement stochastic modeling with log-normal distribution for inflation and return rates
- **Rationale**: Monte Carlo methods provide probabilistic forecasts that account for market uncertainty
- **Implementation**: 
  - Default 2500 simulations for statistical reliability
  - Maximum 50-year simulation horizon to prevent infinite loops
  - User-configurable volatility (inflation: 0.5-10%, returns: 0.5-20%)
  - Log-normal distribution ensures positive rates and realistic asymmetry
- **Pros**: Captures uncertainty, provides confidence intervals, realistic modeling, always positive rates
- **Cons**: Computationally intensive for large simulation counts

**Number Formatting**: Indian numbering system support
- **Decision**: Format large numbers using Lakhs (L) and Crores (Cr) notation
- **Rationale**: Target audience likely uses Indian numbering conventions
- **Implementation**: Cascading formatter that handles Crores (10M+), Lakhs (100K+), and thousands
- **Alternative**: International notation (K, M, B) also available in the formatter

### Visualization Architecture
**Technology**: Plotly for interactive charts
- **Decision**: Use Plotly Graph Objects for dynamic, interactive visualizations
- **Rationale**: Plotly provides rich interactivity (zoom, pan, hover), better than static matplotlib charts
- **Chart Types**:
  1. **Corpus Trajectory Chart**: Line chart with confidence intervals (10th, 25th, 50th, 75th, 90th percentiles)
  2. **Distribution Chart**: Shows probability distributions of outcomes
- **Design Pattern**: Separate visualization module for code organization and reusability

**Confidence Intervals**: Multi-percentile display
- **Decision**: Show 80% confidence interval (10th-90th percentile) and 50% interval (25th-75th)
- **Rationale**: Provides users with both optimistic and pessimistic scenarios
- **Visual Strategy**: Layered fill areas with transparency for easy interpretation

### Module Organization
**Separation of Concerns**:
1. **app.py**: Main application entry point, UI components, user input handling
2. **monte_carlo.py**: Simulation logic, statistical calculations, random rate generation
3. **visualization.py**: Chart creation, data transformation for plotting

- **Decision**: Modular architecture with clear separation
- **Rationale**: Improves maintainability, testability, and code reuse
- **Pros**: Easy to modify individual components, supports future extensions
- **Cons**: More files to manage, requires understanding of module interactions

### Statistical Methodology
**Stochastic Rate Generation**:
- **Decision**: Use log-normal distribution for inflation and return rate randomization
- **Parameters**: 
  - Mean = expected rate (user-configurable)
  - Volatility = user-configurable (inflation: 0.5-10%, returns: 0.5-20%)
  - Converts to log-normal parameters: mu = ln(m² / √(m² + s²)), sigma = √(ln(1 + (s/m)²))
- **Rationale**: 
  - Log-normal ensures rates are always positive (no artificial flooring)
  - Better models multiplicative compound returns (standard in Black-Scholes)
  - Captures realistic asymmetry in financial returns
  - User-configurable volatility allows modeling different market conditions
- **Alternative Considered**: Normal distribution (previous implementation, could produce negative rates)

**Result Aggregation**: Percentile-based analysis
- **Decision**: Calculate and display multiple percentiles (10, 25, 50, 75, 90) plus mean
- **Rationale**: Provides comprehensive view of outcome distribution from pessimistic to optimistic
- **Implementation**: Track corpus values across all simulations at each time step with monthly precision

## External Dependencies

### Core Libraries
1. **Streamlit**: Web application framework for data apps
   - Purpose: UI rendering, input widgets, layout management
   - Version: Not specified (recommend pinning in requirements.txt)

2. **NumPy**: Numerical computing library
   - Purpose: Random number generation, array operations, statistical calculations
   - Use case: Monte Carlo simulation engine, percentile calculations

3. **Pandas**: Data manipulation library
   - Purpose: Data structuring, time series handling
   - Use case: Organizing simulation results, data transformation

4. **Plotly**: Interactive visualization library
   - Purpose: Creating dynamic, web-based charts
   - Modules used: `plotly.graph_objects`, `plotly.subplots`, `plotly.express`
   - Use case: Corpus trajectory charts, distribution visualizations

### Data Storage
- **Current Implementation**: No persistent storage
- **Architecture**: All calculations performed in-memory during user session
- **Implication**: Results are not saved between sessions; purely computational application

### Deployment Considerations
- **Platform**: Designed for Replit deployment (Streamlit-compatible)
- **State Management**: Relies on Streamlit's session state (implicit)
- **Scalability**: Computation-bound by number of simulations; no database bottleneck