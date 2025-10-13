import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import Dict, List

def create_corpus_chart(simulation_data: Dict) -> go.Figure:
    """
    Create an interactive line chart showing corpus trajectory over time with confidence intervals.
    
    Args:
        simulation_data: Dictionary containing simulation results and percentiles
        
    Returns:
        Plotly figure object
    """
    percentiles = simulation_data['percentiles']
    years = simulation_data['years']
    
    # Extract data for plotting
    p10_values = [percentiles[year]['p10'] for year in years]
    p25_values = [percentiles[year]['p25'] for year in years]
    p50_values = [percentiles[year]['p50'] for year in years]
    p75_values = [percentiles[year]['p75'] for year in years]
    p90_values = [percentiles[year]['p90'] for year in years]
    mean_values = [percentiles[year]['mean'] for year in years]
    
    # Create figure
    fig = go.Figure()
    
    # Add confidence intervals
    fig.add_trace(go.Scatter(
        x=years + years[::-1],
        y=p90_values + p10_values[::-1],
        fill='tonexty',
        fillcolor='rgba(0,100,80,0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=True,
        name='80% Confidence Interval (10th-90th percentile)',
        hovertemplate='<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=years + years[::-1],
        y=p75_values + p25_values[::-1],
        fill='tonexty',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=True,
        name='50% Confidence Interval (25th-75th percentile)',
        hovertemplate='<extra></extra>'
    ))
    
    # Add median line
    fig.add_trace(go.Scatter(
        x=years,
        y=p50_values,
        mode='lines',
        name='Median Scenario',
        line=dict(color='#1f77b4', width=3),
        hovertemplate='Year: %{x}<br>Corpus: %{y:,.0f}<extra></extra>'
    ))
    
    # Add mean line
    fig.add_trace(go.Scatter(
        x=years,
        y=mean_values,
        mode='lines',
        name='Mean Scenario',
        line=dict(color='#ff7f0e', width=2, dash='dash'),
        hovertemplate='Year: %{x}<br>Corpus: %{y:,.0f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title='Retirement Corpus Trajectory Over Time',
        xaxis_title='Years from Now',
        yaxis_title='Corpus Value',
        hovermode='x unified',
        showlegend=True,
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Update axes
    fig.update_xaxes(
        gridcolor='lightgray',
        gridwidth=1,
        zeroline=True,
        zerolinecolor='gray',
        zerolinewidth=2
    )
    
    fig.update_yaxes(
        gridcolor='lightgray',
        gridwidth=1,
        tickformat='.0s',
        zeroline=True,
        zerolinecolor='gray',
        zerolinewidth=2
    )
    
    return fig

def create_distribution_chart(years_lasted: List[float]) -> go.Figure:
    """
    Create a histogram showing the distribution of corpus longevity across simulations.
    
    Args:
        years_lasted: List of years each simulation lasted
        
    Returns:
        Plotly figure object
    """
    fig = go.Figure()
    
    # Create histogram
    fig.add_trace(go.Histogram(
        x=years_lasted,
        nbinsx=30,
        name='Simulation Results',
        marker_color='rgba(0,100,80,0.7)',
        marker_line_color='rgba(0,100,80,1)',
        marker_line_width=1,
        hovertemplate='Years: %{x}<br>Count: %{y}<extra></extra>'
    ))
    
    # Add vertical lines for key percentiles
    percentiles = np.percentile(years_lasted, [25, 50, 75])
    colors = ['red', 'blue', 'green']
    names = ['25th Percentile (Conservative)', '50th Percentile (Median)', '75th Percentile (Optimistic)']
    
    for i, (perc, color, name) in enumerate(zip(percentiles, colors, names)):
        fig.add_vline(
            x=perc, 
            line_dash="dash", 
            line_color=color,
            annotation_text=f"{name}<br>{perc:.1f} years",
            annotation_position="top"
        )
    
    # Update layout
    fig.update_layout(
        title='Distribution of Corpus Longevity Across Simulations',
        xaxis_title='Years Lasted',
        yaxis_title='Number of Simulations',
        showlegend=False,
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Update axes
    fig.update_xaxes(
        gridcolor='lightgray',
        gridwidth=1
    )
    
    fig.update_yaxes(
        gridcolor='lightgray',
        gridwidth=1
    )
    
    return fig

def create_success_probability_chart(success_rates: Dict[str, float]) -> go.Figure:
    """
    Create a gauge chart showing success probability for different time horizons.
    
    Args:
        success_rates: Dictionary mapping time horizons to success rates
        
    Returns:
        Plotly figure object
    """
    # Create subplots for multiple gauges
    fig = make_subplots(
        rows=1, 
        cols=len(success_rates),
        subplot_titles=list(success_rates.keys()),
        specs=[[{"type": "indicator"}] * len(success_rates)]
    )
    
    colors = ['red', 'yellow', 'green']
    
    for i, (horizon, rate) in enumerate(success_rates.items()):
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=rate,
                title={'text': f"{horizon} Years"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': colors[i % len(colors)]},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=1, 
            col=i+1
        )
    
    fig.update_layout(
        height=300,
        title_text="Success Probability by Time Horizon"
    )
    
    return fig
