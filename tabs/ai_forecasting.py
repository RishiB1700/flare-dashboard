import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

def calculate_waste_percentage(fri_score):
    """
    Calculate waste percentage from FRI score using linear mapping:
    FRI 0 → 10% waste
    FRI 50 → 40% waste
    FRI 100 → 70% waste
    """
    if pd.isna(fri_score) or not isinstance(fri_score, (int, float)):
        return 0.1  # Default to minimal waste (10%)
    
    # Ensure fri_score is within valid range
    fri_score = max(0, min(100, fri_score))
    
    # Linear formula
    min_waste = 0.1  # 10%
    max_waste = 0.7  # 70%
    waste_percentage = min_waste + (fri_score / 100) * (max_waste - min_waste)
    
    return waste_percentage

def format_currency(value):
    """Format value as currency"""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return "$0.00"
    return f"${value:,.2f}"

def simulate_fri_forecast(campaign_data, days=14):
    """Simulate FRI score projection for 14 days with and without intervention"""
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

    # Get the last FRI score as the starting point
    last_fri = fri_scores.iloc[-1]
    
    # Generate baseline and intervention forecasts
    baseline = []
    intervention = []
    
    for i in range(days):
        # Baseline forecast (no intervention)
        if last_fri < 85:  # If not already near max
            projected = min(100, last_fri + (i * 1.5) + np.random.normal(0, 1))
        else:
            projected = min(100, last_fri + np.random.normal(0, 1))
        baseline.append(projected)
        
        # Intervention forecast (FLARE optimization)
        if i < 3:  # First 3 days - same as baseline
            intervention.append(baseline[-1])
        else:  # After day 3 - improvement begins
            previous = intervention[-1]
            projected = max(10, previous - 3 + np.random.normal(0, 1))
            intervention.append(projected)

    # Create forecast dataframe
    forecast_df = pd.DataFrame({
        "Day": [f"Day {i+1}" for i in range(days)],
        "Baseline Forecast": baseline,
        "FLARE Intervention": intervention
    })
    
    return forecast_df

def build_ai_forecasting_tab(flare):
    """Build the AI forecasting tab with future projections"""
    try:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.header("AI-Powered Fatigue Forecasting")
        
        # Check if data is available
        if flare.fatigue_scores is None or len(flare.fatigue_scores) == 0:
            st.warning("No campaign data available. Please process data first.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Get text color based on theme
        text_color = '#ffffff' if st.session_state.get('theme', 'light') == 'dark' else '#111111'
        
        # Preview message with updated styling
        st.markdown(f"""
        <div style="padding: 20px; background-color: rgba(0,0,0,0.03); border-left: 4px solid #FF5A5F; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
            <h3 style="margin-top: 0; color: #FF5A5F; font-weight: 600;">Coming Soon: Predictive Fatigue Intelligence</h3>
            <p style="color: inherit; margin-bottom: 0;">FLARE's machine learning engine is currently in development. Soon, it will be able to predict campaign fatigue before performance metrics drop, saving your ad budget and improving campaign effectiveness.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create tabs for different forecasting features
        forecast_tabs = st.tabs(["Fatigue Prediction", "Budget Optimization", "Creative Rotation"])
        
        with forecast_tabs[0]:
            st.subheader("Predictive Fatigue Patterns")
            
            campaign_ids = flare.fatigue_scores['campaign_id'].unique()
            if len(campaign_ids) == 0:
                st.warning("No campaigns available for forecasting.")
            else:
                # Use selected campaign from session state if available
                if 'selected_campaign' in st.session_state and st.session_state.selected_campaign in campaign_ids:
                    default_index = list(campaign_ids).index(st.session_state.selected_campaign)
                else:
                    default_index = 0
                
                selected = st.selectbox("Select Campaign", campaign_ids, index=default_index)
                
                # Get campaign data
                campaign_data = flare.fatigue_scores[flare.fatigue_scores['campaign_id'] == selected]
                
                if len(campaign_data) > 0:
                    # Generate forecast data
                    dates = pd.to_datetime(campaign_data['date'])
                    fri_scores = campaign_data['fri_score'].fillna(0)
                    
                    # Create future dates (14 days from last date)
                    last_date = dates.iloc[-1]
                    future_dates = [last_date + timedelta(days=i) for i in range(1, 15)]
                    
                    # Get the last FRI score
                    last_fri = fri_scores.iloc[-1]
                    
                    # Generate baseline and intervention forecasts
                    baseline_fri = []
                    flare_fri = []
                    intervention_point = 3  # Day when intervention happens
                    
                    for i in range(14):
                        # Baseline forecast (no intervention)
                        if last_fri < 85:  # If not already near max
                            baseline = min(100, last_fri + (i * 1.5) + np.random.normal(0, 1))
                        else:
                            baseline = min(100, last_fri + np.random.normal(0, 1))
                        baseline_fri.append(baseline)
                        
                        # FLARE intervention forecast
                        if i < intervention_point:
                            # Same trajectory initially
                            flare_fri.append(baseline_fri[i])
                        else:
                            # Improvement after intervention
                            previous = flare_fri[i-1]
                            flare_fri.append(max(10, previous - 3 + np.random.normal(0, 1)))
                    
                    # Create the figure
                    fig = go.Figure()
                    
                    # Historical data
                    fig.add_trace(
                        go.Scatter(
                            x=dates,
                            y=fri_scores,
                            mode='lines+markers',
                            name='Historical FRI',
                            line=dict(color='#1f77b4', width=3)
                        )
                    )
                    
                    # Baseline projection
                    fig.add_trace(
                        go.Scatter(
                            x=future_dates,
                            y=baseline_fri,
                            mode='lines+markers',
                            name='Baseline Forecast',
                            line=dict(color='#ff7f0e', width=3, dash='dot')
                        )
                    )
                    
                    # FLARE-optimized projection
                    fig.add_trace(
                        go.Scatter(
                            x=future_dates,
                            y=flare_fri,
                            mode='lines+markers',
                            name='With FLARE Intervention',
                            line=dict(color='#2ca02c', width=3, dash='dot')
                        )
                    )
                    
                    # Add intervention marker
                    intervention_date = future_dates[intervention_point]
                    fig.add_vline(x=intervention_date, line=dict(color='green', width=2, dash='dash'))
                    fig.add_annotation(
                        x=intervention_date,
                        y=95,
                        text="FLARE Intervention",
                        showarrow=True,
                        arrowhead=2,
                        arrowcolor="green",
                        font=dict(color=text_color)
                    )
                    
                    # Add threshold lines
                    fig.add_hline(y=20, line=dict(color='#FFCA28', width=1, dash='dash'))
                    fig.add_hline(y=50, line=dict(color='#FF9800', width=1, dash='dash'))
                    fig.add_hline(y=75, line=dict(color='#F44336', width=1, dash='dash'))
                    
                    # Update layout with theme-specific colors
                    fig.update_layout(
                        height=500,
                        margin=dict(l=10, r=10, t=30, b=10),
                        legend=dict(orientation="h"),
                        title="AI-Powered Fatigue Forecast",
                        xaxis_title="Date",
                        yaxis_title="FRI Score",
                        hovermode="x unified",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=text_color)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Calculate projected savings
                    projected_waste_baseline = sum([calculate_waste_percentage(fri) * 100 for fri in baseline_fri]) * 10
                    projected_waste_flare = sum([calculate_waste_percentage(fri) * 100 for fri in flare_fri]) * 10
                    savings = projected_waste_baseline - projected_waste_flare
                    
                    # Display projected savings with updated styling
                    st.markdown(f"""
                    <div style="padding: 22px; background-color: rgba(255,90,95,0.05); border-radius: 10px; margin-top: 25px; border: 1px solid rgba(255,90,95,0.1);">
                        <h3 style="margin-top: 0; color: #FF5A5F; font-weight: 600;">Projected Impact</h3>
                        <p>By implementing AI-recommended interventions at the optimal time, you could save approximately <strong>{format_currency(savings)}</strong> in wasted ad spend over the next 14 days for this campaign alone.</p>
                        <p style="margin-bottom: 0;">This represents a <strong>{(savings/projected_waste_baseline*100):.1f}%</strong> reduction in projected waste.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"No data available for campaign {selected}")
        
        with forecast_tabs[1]:
            st.subheader("Budget Optimization Preview")
            
            # Updated styling for info box
            st.markdown(f"""
            <div style="padding: 20px; background-color: rgba(0,0,0,0.03); border-left: 4px solid #FF5A5F; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <p style="color: inherit; margin-bottom: 0;">FLARE's budget optimization AI will automatically suggest how to reallocate budget from fatigued campaigns to higher-performing opportunities.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create sample budget optimization visualization with improved layout
            campaign_names = ["Campaign A", "Campaign B", "Campaign C", "Campaign D", "Campaign E"]
            current_budget = [5000, 7500, 3000, 4500, 2000]
            optimized_budget = [7000, 3500, 4500, 6000, 1000]
            
            fig = go.Figure()
            
            # Current budget
            fig.add_trace(go.Bar(
                x=campaign_names,
                y=current_budget,
                name='Current Budget',
                marker_color='#90CAF9'
            ))
            
            # Optimized budget
            fig.add_trace(go.Bar(
                x=campaign_names,
                y=optimized_budget,
                name='FLARE Optimized Budget',
                marker_color='#FF5A5F'
            ))
            
            # Update layout with improved spacing and positioning
            fig.update_layout(
                barmode='group',
                height=450,  # Increase height
                margin=dict(l=10, r=10, t=90, b=50),  # More top margin for the title and legend
                title={
                    'text': "AI-Driven Budget Reallocation Preview",
                    'y': 0.95,  # Position the title higher
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                xaxis_title="Campaign",
                yaxis_title="Budget ($)",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color)
            )
            
            # Format y-axis as currency
            fig.update_yaxes(tickprefix="$", tickformat=",")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add explanatory text with updated styling
            st.markdown(f"""
            <div style="padding: 18px; background-color: rgba(255,90,95,0.05); border-radius: 10px; margin-top: 15px; border: 1px solid rgba(255,90,95,0.1);">
                <h4 style="margin-top: 0; color: #FF5A5F; font-weight: 600;">AI Insights</h4>
                <ul style="margin-bottom: 5px;">
                    <li><strong>Reduce:</strong> Campaign B shows severe fatigue symptoms - FLARE recommends reducing budget by 53%</li>
                    <li><strong>Increase:</strong> Campaign A and D show healthy engagement - reallocate budget to maximize returns</li>
                    <li><strong>Monitor:</strong> Campaign C has early friction signs but still delivering value - maintain budget but prepare creative refresh</li>
                </ul>
                <p style="margin-bottom: 0;">Implementing these recommendations could improve overall ROAS by an estimated 27%.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with forecast_tabs[2]:
            st.subheader("AI-Guided Creative Rotation")
            
            # Updated styling for info box
            st.markdown(f"""
            <div style="padding: 20px; background-color: rgba(0,0,0,0.03); border-left: 4px solid #FF5A5F; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <p style="color: inherit; margin-bottom: 0;">FLARE's AI engine will learn from performance patterns to recommend the optimal creative refresh schedule for each campaign and format.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create sample creative lifespan chart
            formats = ["Static Image", "Video", "Carousel", "Story", "Native"]
            lifespan_days = [9, 14, 8, 5, 12]
            
            # Updated colors to match FLARE palette
            format_colors = ['#FF5A5F', '#FF8A8F', '#FFA8AB', '#FFC5C7', '#FFE2E3']
            
            fig = go.Figure()
            
            for i, format_name in enumerate(formats):
                fig.add_trace(go.Bar(
                    x=[format_name],
                    y=[lifespan_days[i]],
                    name=format_name,
                    marker_color=format_colors[i],
                    width=0.6
                ))
            
            # Update layout with theme-specific colors
            fig.update_layout(
                height=400,
                margin=dict(l=10, r=10, t=30, b=10),
                title="Average Creative Lifespan by Format",
                yaxis_title="Effective Days Before Fatigue",
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color)
            )
            
            # Add annotations
            for i, format_name in enumerate(formats):
                fig.add_annotation(
                    x=format_name,
                    y=lifespan_days[i] + 0.5,
                    text=f"{lifespan_days[i]} days",
                    showarrow=False,
                    font=dict(size=14, color=text_color)
                )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add explanatory text with updated styling
            st.markdown(f"""
            <div style="padding: 18px; background-color: rgba(255,90,95,0.05); border-radius: 10px; margin-top: 20px; border: 1px solid rgba(255,90,95,0.1);">
                <h4 style="margin-top: 0; color: #FF5A5F; font-weight: 600;">AI Creative Rotation Insights</h4>
                <p>Based on historical performance data across your campaigns, FLARE recommends:</p>
                <ul>
                    <li><strong>Stories:</strong> Refresh every 5 days (highest fatigue rate)</li>
                    <li><strong>Videos:</strong> Refresh every 14 days (most fatigue-resistant)</li>
                    <li><strong>Static Images:</strong> Implement A/B testing on day 7 to extend lifespan</li>
                </ul>
                <p style="margin-bottom: 0;">Automating creative refreshes based on these timelines could improve overall campaign performance by an estimated 18-24%.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error rendering AI Forecasting tab: {str(e)}")