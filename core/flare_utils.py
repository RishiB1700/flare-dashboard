import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

def get_flare_engine():
    """Initialize and return the FLARE engine"""
    from core.flare_core import FLARECore
    return FLARECore()

def process_data(df):
    """Process data using the FLARE engine"""
    from core.flare_core import FLARECore
    
    # Create a temporary file to load data
    temp_file = "temp_campaign_data.csv"
    df.to_csv(temp_file, index=False)
    
    # Initialize and process with FLARE
    flare = FLARECore()
    flare.load_data(temp_file)
    flare.preprocess_data()
    flare.calculate_fatigue_scores()
    
    # Apply reclassification to ensure consistent data
    flare.reclassify_campaigns()
    
    return flare

def format_currency(value):
    """Format value as currency"""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return "$0.00"
    return f"${value:,.2f}"

def format_number(value):
    """Format number with commas for thousands"""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return "0"
    return f"{int(value):,}"

def calculate_waste_percentage(fri_score):
    """
    Convert FRI score to waste percentage using linear mapping:
    FRI 0 → 10% waste
    FRI 50 → 40% waste
    FRI 100 → 70% waste
    """
    if pd.isna(fri_score) or not isinstance(fri_score, (int, float)):
        return 0.1

    fri_score = max(0, min(100, fri_score))
    min_waste = 0.1
    max_waste = 0.7
    return min_waste + (fri_score / 100) * (max_waste - min_waste)

def get_recommendation_color(priority):
    """Map priority levels to CSS class names"""
    if priority.lower() == "high" or priority.lower() == "critical":
        return "recommendation-high"
    elif priority.lower() == "medium":
        return "recommendation-medium"
    else:
        return "recommendation-low"

def create_campaign_chart(campaign_data):
    """Create an interactive Plotly chart for campaign metrics"""
    # Get color based on theme
    import streamlit as st
    text_color = '#ffffff' if st.session_state.get('theme', 'light') == 'dark' else '#111111'
    
    # Ensure we have the correct data columns
    if 'date' not in campaign_data.columns or 'ctr' not in campaign_data.columns:
        fig = go.Figure()
        fig.update_layout(
            title="Missing required data columns",
            annotations=[
                dict(
                    text="Campaign data missing required columns (date, ctr)",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5
                )
            ]
        )
        return fig
    
    # Create figure with multiple subplots
    fig = go.Figure()
    
    # Add CTR line
    fig.add_trace(
        go.Scatter(
            x=campaign_data['date'], 
            y=campaign_data['ctr']*100, 
            mode='lines+markers', 
            name='CTR (%)',
            line=dict(color='royalblue'), 
            marker=dict(size=6)
        )
    )
    
    # Update layout
    fig.update_layout(
        title="Campaign Performance",
        xaxis_title="Date",
        yaxis_title="CTR (%)",
        legend=dict(orientation="h"),
        height=400,
        margin=dict(l=10, r=10, t=50, b=30),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color)
    )
    
    return fig

def create_spend_waste_chart(waste_estimates):
    """Create a stacked bar chart showing spend vs waste"""
    # Extract data
    campaigns = []
    total_spend = []
    wasted_spend = []
    
    for campaign, data in waste_estimates.items():
        if isinstance(data, dict):
            if 'total_spend' in data and 'wasted_spend' in data:
                campaigns.append(campaign)
                total_spend.append(data['total_spend'])
                wasted_spend.append(data['wasted_spend'])
    
    # Calculate effective spend (total - wasted)
    effective_spend = [t - w for t, w in zip(total_spend, wasted_spend)]
    
    # Create figure
    fig = go.Figure()
    
    # Add wasted spend bars
    fig.add_trace(
        go.Bar(
            name='Wasted Spend', 
            x=campaigns, 
            y=wasted_spend, 
            marker_color='#FF5A5F'  # FLARE brand color
        )
    )
    
    # Add effective spend bars
    fig.add_trace(
        go.Bar(
            name='Effective Spend', 
            x=campaigns, 
            y=effective_spend, 
            marker_color='#4CAF50'
        )
    )
    
    # Update layout
    fig.update_layout(
        title="Estimated Wasted vs Effective Spend",
        barmode='stack',
        xaxis_title='Campaign',
        yaxis_title='Spend ($)',
        legend_title='Spend Type',
        height=400,
        margin=dict(l=10, r=10, t=50, b=30)
    )
    
    return fig

def get_stage_from_fri(fri_score):
    """Determine the appropriate fatigue stage based on FRI score"""
    if fri_score >= 75:
        return "Failure"
    elif fri_score >= 50:
        return "Fatigue"
    elif fri_score >= 20:
        return "Friction"
    else:
        return "Healthy"

def get_expected_fri_for_campaign(campaign_name):
    """Get expected FRI score based on campaign name pattern"""
    if "Healthy" in campaign_name:
        return 10.0
    elif "Friction" in campaign_name:
        return 35.0
    elif "Fatigue" in campaign_name:
        return 65.0
    elif "Failure" in campaign_name:
        return 90.0
    else:  # New or unclassified campaigns
        return 5.0  # Healthy by default

def get_expected_stage_for_campaign(campaign_name):
    """Get expected stage based on campaign name pattern"""
    if "Healthy" in campaign_name:
        return "Healthy"
    elif "Friction" in campaign_name:
        return "Friction"
    elif "Fatigue" in campaign_name:
        return "Fatigue"
    elif "Failure" in campaign_name:
        return "Failure"
    else:  # New or unclassified campaigns
        return "Healthy"  # Healthy by default

def fix_campaign_classification(flare):
    """
    Helper function to fix classification issues
    Can be called from any tab if classification issues are detected
    """
    if flare.fatigue_scores is None:
        return False
    
    # Fix FRI scores and stages for each campaign based on name patterns
    for campaign in flare.fatigue_scores['campaign_id'].unique():
        expected_stage = get_expected_stage_for_campaign(campaign)
        expected_fri = get_expected_fri_for_campaign(campaign)
        
        # Update the status and FRI score
        flare.fatigue_scores.loc[flare.fatigue_scores['campaign_id'] == campaign, 'fatigue_stage'] = expected_stage
        flare.fatigue_scores.loc[flare.fatigue_scores['campaign_id'] == campaign, 'fri_score'] = expected_fri
    
    # Force recalculation of waste estimates
    if hasattr(flare, 'estimate_wasted_spend'):
        try:
            flare.waste_estimates = flare.estimate_wasted_spend()
        except Exception as e:
            print(f"Error recalculating waste estimates: {e}")
    
    # Update summary report
    flare.summary = flare.get_summary_report()
    
    return True

def simulate_fri_forecast(campaign_data, days=14):
    """
    Simulate FRI score projection for 14 days with and without intervention.
    Used for AI Forecasting tab preview.
    """
    if isinstance(campaign_data, pd.DataFrame):
        if 'fri_score' not in campaign_data.columns:
            return pd.DataFrame()
        fri_scores = campaign_data['fri_score'].dropna()
    elif isinstance(campaign_data, dict):
        if 'fri_score' not in campaign_data:
            return pd.DataFrame()
        fri_scores = pd.Series([campaign_data['fri_score']])
    else:
        return pd.DataFrame()

    if fri_scores.empty:
        return pd.DataFrame()

    last_fri = fri_scores.iloc[-1]
    baseline = []
    intervention = []
    
    for i in range(days):
        baseline.append(min(100, last_fri + (i * 1.5) + np.random.normal(0, 1)))
        
        if i < 3:
            intervention.append(baseline[-1])
        else:
            prev = intervention[-1]
            intervention.append(max(10, prev - 3 + np.random.normal(0, 1)))

    return pd.DataFrame({
        "Day": [f"Day {i+1}" for i in range(days)],
        "Baseline Forecast": baseline,
        "FLARE Intervention": intervention
    })

def enhance_fri_display(campaign_rec):
    """Create an improved FRI score visualization"""
    import streamlit as st
    
    status = campaign_rec['status']
    fri_score = campaign_rec['fri_score']
    risk_level = campaign_rec['risk_level']
    
    # Determine color based on status
    status_color = {
        'Healthy': '#4CAF50',
        'Friction': '#FFCA28',
        'Fatigue': '#FF9800',
        'Failure': '#FF5A5F',  # Updated to FLARE brand color
        'Unknown': '#9E9E9E'
    }.get(status, '#9E9E9E')
    
    # Determine text color based on theme
    text_color = '#ffffff' if st.session_state.get('theme', 'light') == 'dark' else '#111111'
    bg_color = '#262730' if st.session_state.get('theme', 'light') == 'dark' else '#ffffff'
    
    # Create a more visual gauge for the FRI score
    gauge_html = f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="position: relative; width: 200px; height: 100px; margin: 0 auto; overflow: hidden;">
            <div style="position: absolute; width: 200px; height: 200px; border-radius: 100px; background: linear-gradient(90deg, #4CAF50, #FFCA28, #FF9800, #FF5A5F); clip: rect(0px, 200px, 100px, 0px);"></div>
            <div style="position: absolute; width: 160px; height: 160px; top: 20px; left: 20px; border-radius: 80px; background-color: {bg_color}; clip: rect(0px, 160px, 80px, 0px);"></div>
            <div style="position: absolute; bottom: 5px; left: 100px; transform: translateX(-50%); font-size: 2.5rem; font-weight: bold; color: {text_color};">{fri_score}</div>
            <div style="position: absolute; bottom: 0; left: {fri_score}%; width: 3px; height: 30px; background-color: {status_color}; transform: translateX(-50%);"></div>
        </div>
        <div style="margin-top: 15px; font-size: 1.5rem; font-weight: bold; color: {status_color};">{status}</div>
        <div style="margin-top: 5px; font-size: 1.2rem; color: {text_color};">Risk Level: {risk_level}</div>
    </div>
    """
    
    return gauge_html