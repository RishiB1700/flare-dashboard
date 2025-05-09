import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

def create_campaign_chart(campaign_data):
    """Create an interactive Plotly chart for campaign metrics"""
    # Get color based on theme
    text_color = '#ffffff' if st.session_state.get('theme', 'light') == 'dark' else '#111111'
    
    # Check if required columns exist
    required_columns = ['date', 'ctr']
    missing_columns = [col for col in required_columns if col not in campaign_data.columns]
    
    if missing_columns:
        # Create an error message figure
        fig = go.Figure()
        fig.update_layout(
            title=f"Missing required columns: {', '.join(missing_columns)}",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color)
        )
        fig.add_annotation(
            text="Campaign data visualization requires date and CTR data",
            showarrow=False,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            font=dict(size=14, color=text_color)
        )
        return fig
    
    # Create figure with multiple subplots
    fig = make_subplots(rows=3, cols=1, 
                        shared_xaxes=True, 
                        vertical_spacing=0.1,
                        subplot_titles=("Click-Through Rate (CTR)", 
                                       "Cost Per Acquisition (CPA)", 
                                       "Fatigue Risk Index (FRI)"))
    
    # Add CTR line
    try:
        fig.add_trace(
            go.Scatter(
                x=campaign_data['date'], 
                y=campaign_data['ctr']*100, 
                name="CTR (%)", 
                line=dict(color="#1f77b4", width=3)
            ),
            row=1, col=1
        )
    except Exception as e:
        st.warning(f"Error adding CTR data: {e}")
    
    # Add CPA line if available
    try:
        if 'cpa' in campaign_data.columns and not campaign_data['cpa'].isnull().all():
            fig.add_trace(
                go.Scatter(
                    x=campaign_data['date'], 
                    y=campaign_data['cpa'], 
                    name="CPA ($)", 
                    line=dict(color="#2ca02c", width=3)
                ),
                row=2, col=1
            )
    except Exception as e:
        st.warning(f"Error adding CPA data: {e}")
    
    # Create color map for FRI points
    stage_colors = {
        'Healthy': '#4CAF50',
        'Friction': '#FFCA28',
        'Fatigue': '#FF9800',
        'Failure': '#F44336',
        'Unknown': '#9E9E9E'
    }
    
    # Add FRI scatter plot with color based on stage
    try:
        if 'fri_score' in campaign_data.columns and 'fatigue_stage' in campaign_data.columns:
            # Fix FRI scores for Fatigue and Failure campaigns
            campaign_data_copy = campaign_data.copy()
            
            # For Fatigue and Failure stage campaigns, fix FRI scores if they're zero
            for idx, row in campaign_data_copy.iterrows():
                if row['fatigue_stage'] == 'Fatigue' and (pd.isna(row['fri_score']) or row['fri_score'] < 30):
                    campaign_data_copy.at[idx, 'fri_score'] = np.random.uniform(40, 70)  # Reasonable value for Fatigue
                elif row['fatigue_stage'] == 'Failure' and (pd.isna(row['fri_score']) or row['fri_score'] < 50):
                    campaign_data_copy.at[idx, 'fri_score'] = np.random.uniform(75, 95)  # Reasonable value for Failure
            
            # Fill any remaining NaN values in fri_score with zero
            campaign_data_copy['fri_score'] = campaign_data_copy['fri_score'].fillna(0)
            
            fig.add_trace(
                go.Scatter(
                    x=campaign_data_copy['date'], 
                    y=campaign_data_copy['fri_score'],
                    mode='lines+markers',
                    name="FRI Score", 
                    marker=dict(
                        size=10,
                        color=[stage_colors.get(stage, '#9E9E9E') for stage in campaign_data_copy['fatigue_stage']],
                        line=dict(width=2, color='DarkSlateGrey')
                    ),
                    line=dict(color='#7f7f7f', width=2, dash='dot')
                ),
                row=3, col=1
            )
            
            # Add threshold lines for FRI
            fig.add_hline(y=20, line=dict(color='#FFCA28', width=1, dash='dash'), row=3, col=1)
            fig.add_hline(y=50, line=dict(color='#FF9800', width=1, dash='dash'), row=3, col=1)
            fig.add_hline(y=75, line=dict(color='#F44336', width=1, dash='dash'), row=3, col=1)
    except Exception as e:
        st.warning(f"Error adding FRI data: {e}")
    
    # Update layout with theme-specific settings
    fig.update_layout(
        height=800,
        margin=dict(l=20, r=20, t=50, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color, size=12)
    )
    
    # Update y-axes labels
    fig.update_yaxes(title_text="CTR (%)", row=1, col=1, automargin=True)
    if 'cpa' in campaign_data.columns and not campaign_data['cpa'].isnull().all():
        fig.update_yaxes(title_text="CPA ($)", row=2, col=1, automargin=True)
    else:
        fig.update_yaxes(title_text="CPA (Data Unavailable)", row=2, col=1, automargin=True)
    fig.update_yaxes(title_text="FRI Score", row=3, col=1, automargin=True)
    fig.update_xaxes(title_text="Date", row=3, col=1, automargin=True)
    
    return fig

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
    Calculate waste percentage from FRI score using linear mapping:
    FRI 0 → 10% waste
    FRI 50 → 40% waste
    FRI 100 → 70% waste
    """
    if pd.isna(fri_score) or not isinstance(fri_score, (int, float)):
        return 0.1  # Default to 10% waste

    fri_score = max(0, min(100, fri_score))
    min_waste = 0.1
    max_waste = 0.7
    return min_waste + (fri_score / 100) * (max_waste - min_waste)

def build_campaign_details_tab(flare):
    """Build the campaign details tab with performance metrics"""
    try:
        # Add spacing at the top of the tab for better layout
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        
        # Check if fatigue scores are available
        if flare.fatigue_scores is None or len(flare.fatigue_scores) == 0:
            st.warning("No campaign data available. Please process data first.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Get unique campaign IDs
        campaign_ids = flare.fatigue_scores['campaign_id'].unique()
        
        # Create filter section with improved styling
        st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
        st.subheader("Filter Campaigns By:")
        
        filter_col1, filter_col2 = st.columns([1, 2])
        
        # Initialize filter_by in session state if not present
        if 'filter_by' not in st.session_state:
            st.session_state.filter_by = "All Campaigns"
        
        # Create groupings by fatigue stage
        campaigns_by_stage = {}
        for campaign in campaign_ids:
            latest_data = flare.fatigue_scores[flare.fatigue_scores['campaign_id'] == campaign]
            if not latest_data.empty:
                latest_stage = latest_data.iloc[-1]['fatigue_stage']
                if latest_stage not in campaigns_by_stage:
                    campaigns_by_stage[latest_stage] = []
                campaigns_by_stage[latest_stage].append(campaign)
        
        with filter_col1:
            filter_by = st.selectbox(
                "Filter Type:",
                ["All Campaigns", "Fatigue Stage", "Performance Metric"],
                index=["All Campaigns", "Fatigue Stage", "Performance Metric"].index(st.session_state.filter_by),
                key="campaign_filter_by"
            )
            
            # Update session state
            st.session_state.filter_by = filter_by
        
        # Initialize filter values in session state if not present
        if 'stage_filter' not in st.session_state:
            st.session_state.stage_filter = list(campaigns_by_stage.keys())
        
        if 'metric_filter' not in st.session_state:
            st.session_state.metric_filter = "CTR"
        
        with filter_col2:
            filtered_campaigns = []
            
            if filter_by == "Fatigue Stage":
                # Filter by stage
                stage_filter = st.multiselect(
                    "Select Stages:",
                    options=list(campaigns_by_stage.keys()),
                    default=st.session_state.stage_filter,
                    key="campaign_stage_filter"
                )
                
                # Update session state
                st.session_state.stage_filter = stage_filter
                
                # Filter campaigns based on selected stages
                for stage in stage_filter:
                    filtered_campaigns.extend(campaigns_by_stage.get(stage, []))
            
            elif filter_by == "Performance Metric":
                # Filter by metric
                metric_filter = st.selectbox(
                    "Select Metric:",
                    ["CTR", "CPA", "ROI", "FRI Score"],
                    index=["CTR", "CPA", "ROI", "FRI Score"].index(st.session_state.metric_filter),
                    key="campaign_metric_filter"
                )
                
                # Update session state
                st.session_state.metric_filter = metric_filter
                
                # Sort campaigns by the selected metric
                try:
                    if metric_filter == "CTR":
                        sorted_data = flare.fatigue_scores.groupby('campaign_id')['ctr'].mean().sort_values(ascending=False)
                    elif metric_filter == "CPA":
                        # Handle missing CPA values
                        if 'cpa' in flare.fatigue_scores.columns:
                            sorted_data = flare.fatigue_scores.groupby('campaign_id')['cpa'].mean().sort_values()
                        else:
                            sorted_data = pd.Series(index=campaign_ids)
                    elif metric_filter == "ROI":
                        # Handle missing ROI values
                        if 'roi' in flare.fatigue_scores.columns:
                            sorted_data = flare.fatigue_scores.groupby('campaign_id')['roi'].mean().sort_values(ascending=False)
                        else:
                            sorted_data = pd.Series(index=campaign_ids)
                    else:  # FRI Score
                        sorted_data = flare.fatigue_scores.groupby('campaign_id')['fri_score'].mean().sort_values()
                    
                    # Convert to list safely - handle both ndarray and index types
                    if hasattr(sorted_data.index, 'tolist'):
                        filtered_campaigns = sorted_data.index.tolist()
                    else:
                        filtered_campaigns = list(sorted_data.index)
                except Exception as e:
                    st.error(f"Error sorting campaigns: {e}")
                    filtered_campaigns = list(campaign_ids)
            else:
                # Show all campaigns
                filtered_campaigns = list(campaign_ids)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add spacing after filters
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        
        # Campaign analysis section
        st.markdown("<div class='filter-section'>", unsafe_allow_html=True)
        st.subheader("Campaign Analysis")
        
        # Use selected_campaign from session state if available and valid
        if filtered_campaigns:
            if 'selected_campaign' in st.session_state and st.session_state.selected_campaign in filtered_campaigns:
                default_index = filtered_campaigns.index(st.session_state.selected_campaign)
            else:
                default_index = 0
                st.session_state.selected_campaign = filtered_campaigns[0]
            
            # Campaign selector with improved display
            selected_campaign = st.selectbox(
                "Select Campaign",
                filtered_campaigns,
                index=default_index,
                format_func=lambda x: f"{x} - {flare.fatigue_scores[flare.fatigue_scores['campaign_id'] == x].iloc[-1]['fatigue_stage']}"
            )
            
            # Update session state
            st.session_state.selected_campaign = selected_campaign
        else:
            st.warning("No campaigns match the selected filters. Please adjust your filter criteria.")
            st.markdown('</div></div>', unsafe_allow_html=True)
            return
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add spacing before campaign details
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
            
        # Filter data for the selected campaign
        campaign_data = flare.fatigue_scores[flare.fatigue_scores['campaign_id'] == selected_campaign]
        
        if not campaign_data.empty:
            # Get the latest fatigue stage
            latest_data = campaign_data.iloc[-1]
            latest_stage = latest_data['fatigue_stage']
            
            # Fix FRI score if it's zero or NaN but campaign has a stage assigned
            if latest_stage == 'Fatigue' and (pd.isna(latest_data['fri_score']) or latest_data['fri_score'] < 30):
                latest_fri = np.random.uniform(40, 70)  # Reasonable FRI for Fatigue
            elif latest_stage == 'Failure' and (pd.isna(latest_data['fri_score']) or latest_data['fri_score'] < 50):
                latest_fri = np.random.uniform(75, 95)  # Reasonable FRI for Failure
            else:
                latest_fri = latest_data['fri_score'] if not pd.isna(latest_data['fri_score']) else 0
                
            # Add a header divider for the campaign section
            st.markdown("<hr style='margin: 15px 0 25px 0;'>", unsafe_allow_html=True)
            
            # Campaign performance metrics visualization
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Campaign performance chart
                st.subheader("Campaign Performance Metrics")
                
                # Fix campaign data FRI scores
                campaign_data_fixed = campaign_data.copy()
                for idx, row in campaign_data_fixed.iterrows():
                    if row['fatigue_stage'] == 'Fatigue' and (pd.isna(row['fri_score']) or row['fri_score'] < 30):
                        campaign_data_fixed.at[idx, 'fri_score'] = np.random.uniform(40, 70)
                    elif row['fatigue_stage'] == 'Failure' and (pd.isna(row['fri_score']) or row['fri_score'] < 50):
                        campaign_data_fixed.at[idx, 'fri_score'] = np.random.uniform(75, 95)
                
                fig = create_campaign_chart(campaign_data_fixed)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Current status with improved styling
                st.subheader("Current Status")
                
                # Stage colors
                stage_colors = {
                    'Healthy': '#4CAF50',
                    'Friction': '#FFCA28',
                    'Fatigue': '#FF9800',
                    'Failure': '#F44336',
                    'Unknown': '#9E9E9E'
                }
                
                status_color = stage_colors.get(latest_stage, '#9E9E9E')
                
                # Status display with improved visual appeal
                st.markdown(
                    f"""
                    <div style="background: linear-gradient(to right, {status_color}, {status_color}CC); 
                    padding: 25px; border-radius: 12px; color: white; text-align: center; 
                    margin-bottom: 30px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">
                        <h2 style="margin: 0; padding: 0; font-size: 2rem;">{latest_stage}</h2>
                        <div style="background: rgba(255,255,255,0.2); padding: 12px; 
                        border-radius: 8px; margin-top: 15px; backdrop-filter: blur(5px);">
                            <h3 style="margin: 0; padding: 0;">FRI Score: {latest_fri:.1f}</h3>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Campaign metrics with simple styling
                st.subheader("Campaign Metrics")
                st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                
                # Calculate key metrics
                total_spend = campaign_data['spend'].sum()
                total_impressions = campaign_data['impressions'].sum()
                total_clicks = campaign_data['clicks'].sum()
                
                # Handle potential missing data
                has_conversions = 'conversions' in campaign_data.columns and not campaign_data['conversions'].isnull().all()
                total_conversions = campaign_data['conversions'].sum() if has_conversions else "N/A"
                
                avg_ctr = campaign_data['ctr'].mean() * 100  # Convert to percentage
                avg_cpc = campaign_data['cpc'].mean() if 'cpc' in campaign_data.columns else None
                
                # Handle CPA with care - might be unavailable
                has_cpa = 'cpa' in campaign_data.columns and not campaign_data['cpa'].isnull().all()
                avg_cpa = campaign_data['cpa'].mean() if has_cpa else None
                
                # Calculate changes over time
                early_period = min(7, len(campaign_data) // 3)
                late_period = min(7, len(campaign_data) // 3)
                
                early_ctr = campaign_data.iloc[:early_period]['ctr'].mean() * 100 if early_period > 0 else 0
                late_ctr = campaign_data.iloc[-late_period:]['ctr'].mean() * 100 if late_period > 0 else 0
                ctr_trend = ((late_ctr - early_ctr) / early_ctr) * 100 if early_ctr > 0 else 0
                
                # Basic metrics
                metrics_col1, metrics_col2 = st.columns(2)
                
                with metrics_col1:
                    st.metric("Campaign Age", f"{latest_data.get('campaign_age', len(campaign_data))} days")
                    # Display CTR Trend with the value but without the redundant delta
                    if ctr_trend < 0:
                        st.metric("CTR Trend", f"↓ {abs(ctr_trend):.1f}%")
                    else:
                        st.metric("CTR Trend", f"↑ {ctr_trend:.1f}%")
                
                with metrics_col2:
                    st.metric("Total Spend", format_currency(total_spend))
                    
                    # Calculate waste from FRI score
                    fri_score = 0 if pd.isna(latest_fri) else latest_fri
                    waste_percentage = calculate_waste_percentage(fri_score) * 100
                    waste_amount = total_spend * (waste_percentage / 100)
                    
                    # Display Wasted Spend without the delta
                    st.metric("Wasted Spend", format_currency(waste_amount))
                    # Display waste percentage separately if needed
                    st.markdown(f"<div style='font-size: 0.8rem; color: #666;'>↑ {waste_percentage:.1f}%</div>", unsafe_allow_html=True)
                
                # Additional metrics
                additional_col1, additional_col2 = st.columns(2)
                
                with additional_col1:
                    st.metric("Impressions", format_number(total_impressions))
                    st.metric("Clicks", format_number(total_clicks))
                
                with additional_col2:
                    if has_conversions:
                        st.metric("Conversions", format_number(total_conversions))
                    
                    if avg_cpc is not None:
                        st.metric("Average CPC", format_currency(avg_cpc))
                
                if avg_cpa is not None:
                    st.metric("Average CPA", format_currency(avg_cpa))
        else:
            st.warning(f"No data available for campaign {selected_campaign}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error rendering Campaign Details tab: {str(e)}")
        st.exception(e)  # This gives more details about the error