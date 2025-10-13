# Retirement Corpus Calculator

## Overview

This is a Monte Carlo simulation-based retirement planning application built with Streamlit. The application helps users estimate how long their retirement savings will last under varying market conditions by running multiple simulations with randomized inflation and return rates. Users can input their current corpus, monthly expenses, expected inflation, and expected return rates to generate probabilistic forecasts of their retirement fund longevity.

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
- **Decision**: Implement stochastic modeling with normal distribution for inflation and return rates
- **Rationale**: Monte Carlo methods provide probabilistic forecasts that account for market uncertainty
- **Implementation**: 
  - Default 1000 simulations for statistical reliability
  - Maximum 50-year simulation horizon to prevent infinite loops
  - ±3% standard deviation for both inflation and return rates
- **Pros**: Captures uncertainty, provides confidence intervals, realistic modeling
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
- **Decision**: Use normal distribution for inflation and return rate randomization
- **Parameters**: Mean = expected rate, Standard Deviation = 3%
- **Rationale**: Normal distribution is standard for financial modeling, captures market variability
- **Alternative Considered**: Historical bootstrap sampling (more data-dependent, less flexible)

**Result Aggregation**: Percentile-based analysis
- **Decision**: Calculate and display multiple percentiles (10, 25, 50, 75, 90) plus mean
- **Rationale**: Provides comprehensive view of outcome distribution from pessimistic to optimistic
- **Implementation**: Track corpus values across all simulations at each time step

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