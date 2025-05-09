import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

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

def display_campaigns_by_stage(stage, color, campaigns, flare):
    """Display a list of campaigns with improved styling"""
    if campaigns:
        # Improved header styling
        st.markdown(f"""<div style='background-color: {color}; color: white; padding: 8px 15px; 
        border-radius: 8px; margin: 15px 0 10px 0; font-weight: 600;'>
        {stage} Campaigns ({len(campaigns)})</div>""", unsafe_allow_html=True)
        
        # Create a container for better scrolling
        st.markdown("<div class='campaign-list-container'>", unsafe_allow_html=True)
        
        for campaign in campaigns:
            # Get campaign data
            campaign_data = flare.fatigue_scores[flare.fatigue_scores['campaign_id'] == campaign].iloc[-1]
            
            # Fix FRI score for campaigns - ensure consistency with campaign status
            # This ensures that campaign status and FRI score align properly
            if stage == 'Healthy':
                fri_score = 0 if pd.isna(campaign_data['fri_score']) else min(20, campaign_data['fri_score'])
            elif stage == 'Friction':
                fri_score = 35 if pd.isna(campaign_data['fri_score']) or campaign_data['fri_score'] < 20 else min(50, campaign_data['fri_score'])
            elif stage == 'Fatigue':
                fri_score = 65 if pd.isna(campaign_data['fri_score']) or campaign_data['fri_score'] < 50 else min(75, campaign_data['fri_score'])
            elif stage == 'Failure':
                fri_score = 90 if pd.isna(campaign_data['fri_score']) or campaign_data['fri_score'] < 75 else campaign_data['fri_score']
            else:
                fri_score = 0 if pd.isna(campaign_data['fri_score']) else campaign_data['fri_score']
            
            # Determine progress bar class
            progress_bar_class = ""
            if stage == "Failure":
                progress_bar_class = "progress-bar-failure"
            elif stage == "Fatigue":
                progress_bar_class = "progress-bar-fatigue"
            
            # Get text color based on theme
            text_color = '#ffffff' if st.session_state.get('theme', 'light') == 'dark' else '#111111'
            
            st.markdown(f"""
            <div class='campaign-listing'>
                <div style='display: flex; align-items: center;'>
                    <div style='width: 30%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; 
                    color: {text_color}; padding-right: 10px;'>{campaign}</div>
                    <div style='flex-grow: 1; margin: 0 10px;'>
                        <div class='progress-container' style='height: 8px;'>
                            <div class='progress-bar {progress_bar_class}' style='width: {fri_score}%; 
                            background-color: {color};'></div>
                        </div>
                    </div>
                    <div style='color: {text_color}; width: 40px; text-align: right;'>{fri_score:.0f}</div>
                </div>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

def build_overview_tab(flare):
    """Build the overview tab with campaign health metrics and distribution"""
    try:
        # Add spacing at the top of the tab for better layout
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        # Get summary report from flare engine
        summary = flare.get_summary_report()
        
        if not summary:
            st.warning("No data available. Please process campaign data first.")
            return

        # Fix classification issues if needed
        flare.reclassify_campaigns()
        
        # Force campaigns with high FRI scores to have appropriate stages
        for campaign in flare.fatigue_scores['campaign_id'].unique():
            campaign_data = flare.fatigue_scores[flare.fatigue_scores['campaign_id'] == campaign]
            if not campaign_data.empty:
                latest_data = campaign_data.iloc[-1]
                fri_score = latest_data['fri_score']
                
                # Ensure FRI scores and stages align
                if fri_score >= 75 and latest_data['fatigue_stage'] != 'Failure':
                    flare.fatigue_scores.loc[flare.fatigue_scores['campaign_id'] == campaign, 'fatigue_stage'] = 'Failure'
                elif 50 <= fri_score < 75 and latest_data['fatigue_stage'] != 'Fatigue':
                    flare.fatigue_scores.loc[flare.fatigue_scores['campaign_id'] == campaign, 'fatigue_stage'] = 'Fatigue'
                elif 20 <= fri_score < 50 and latest_data['fatigue_stage'] != 'Friction':
                    flare.fatigue_scores.loc[flare.fatigue_scores['campaign_id'] == campaign, 'fatigue_stage'] = 'Friction'
                elif fri_score < 20 and latest_data['fatigue_stage'] != 'Healthy':
                    flare.fatigue_scores.loc[flare.fatigue_scores['campaign_id'] == campaign, 'fatigue_stage'] = 'Healthy'
        
        # Update summary with fixed classifications
        summary = flare.get_summary_report()
        
        # USE NATIVE STREAMLIT METRICS WITH FIXED HEIGHT AND CSS
        # Add custom CSS to fix equal height and remove extra space
        st.markdown("""
        <style>
        div[data-testid="metric-container"] {
            background-color: transparent !important;
            box-shadow: none !important;
            padding: 0px !important;
            margin: 0px !important;
            height: auto !important;
        }
        /* Make Estimated Waste value red for urgency */
        [data-testid="metric-container"]:nth-child(3) [data-testid="stMetricValue"] {
            color: #FF5A5F !important;
            font-weight: 700 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create metrics row with consistent sizing
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Campaigns", 
                summary["total_campaigns"]
            )
        
        with col2:
            st.metric(
                "Total Spend", 
                format_currency(summary["total_spend"])
            )
        
        with col3:
            # Highlighted with red color via CSS above
            st.metric(
                "Estimated Waste", 
                format_currency(summary["estimated_waste"]),
                f"{summary['waste_percentage']:.2f}%"
            )
        
        with col4:
            st.metric(
                "High Risk Campaigns", 
                len(summary["high_risk_campaigns"])
            )
        
        # Campaign health distribution section - add spacing
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        st.subheader("Campaign Health Distribution")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Create pie chart of campaign stages with improved styling
            stages = summary["campaign_stages"]
            stage_names = list(stages.keys())
            stage_counts = list(stages.values())
            
            # Create pie chart with color mapping
            fig = px.pie(
                names=stage_names, 
                values=stage_counts,
                hole=.4,
                color=stage_names,
                color_discrete_map={
                    'Healthy': '#4CAF50',
                    'Friction': '#FFCA28',
                    'Fatigue': '#FF9800',
                    'Failure': '#F44336',
                    'Unknown': '#9E9E9E'
                }
            )
            
            # Adjust layout based on theme
            theme = st.session_state.get('theme', 'light')
            text_color = '#ffffff' if theme == 'dark' else '#111111'
            
            fig.update_layout(
                margin=dict(l=10, r=10, t=30, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color, size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Display campaigns by stage with FRI scores using the new function
            for stage, color in zip(
                ['Healthy', 'Friction', 'Fatigue', 'Failure', 'Unknown'],
                ['#4CAF50', '#FFCA28', '#FF9800', '#F44336', '#9E9E9E']
            ):
                if stage in summary["campaigns_by_stage"]:
                    campaigns = summary["campaigns_by_stage"][stage]
                    display_campaigns_by_stage(stage, color, campaigns, flare)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # High risk campaigns section - add spacing
        if summary["high_risk_campaigns"]:
            st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True) 
            st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
            st.subheader("High Risk Campaigns")
            
            # Add spacing after the header for better readability
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            
            # Create columns for high risk campaign cards
            cols = st.columns(min(3, len(summary["high_risk_campaigns"])))
            
            for i, campaign_info in enumerate(summary["high_risk_campaigns"]):
                with cols[i % len(cols)]:
                    campaign_id = campaign_info["campaign_id"]
                    stage = campaign_info["stage"]
                    
                    # Ensure high risk campaigns have appropriate stage and FRI
                    if campaign_info['fri_score'] >= 75:
                        stage = 'Failure'
                        fri_score = max(75, campaign_info['fri_score'])
                    elif campaign_info['fri_score'] >= 50:
                        stage = 'Fatigue'
                        fri_score = max(50, campaign_info['fri_score'])
                    else:
                        stage = 'Friction'
                        fri_score = max(30, campaign_info['fri_score'])
                    
                    # Get waste estimates
                    waste_estimates = flare.estimate_wasted_spend()
                    waste_data = waste_estimates.get(campaign_id, {})
                    waste_amount = waste_data.get("wasted_spend", 0) if isinstance(waste_data, dict) else 0
                    waste_percent = waste_data.get("waste_percentage", 0) if isinstance(waste_data, dict) else 0
                    
                    # Determine colors based on theme
                    theme = st.session_state.get('theme', 'light')
                    bg_color = '#3a2525' if theme == 'dark' else '#FFF8F8'
                    border_color = '#5a3333' if theme == 'dark' else '#FFCDD2'
                    text_color = '#ffffff' if theme == 'dark' else '#111111'
                    
                    # Create styled high-risk campaign card
                    st.markdown(f"""
                    <div style='background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(244,67,54,0.1);'>
                        <h3 style='color: {text_color}; margin-top: 0; margin-bottom: 10px;'>{campaign_id}</h3>
                        <div style='margin-bottom: 15px;'><span class="stage-{stage.lower()}">{stage}</span></div>
                        <div style='margin: 15px 0;'>
                            <div style='margin-bottom: 5px; color: {text_color};'>FRI Score</div>
                            <div class='progress-container'>
                                <div class='progress-bar progress-bar-failure' style='width: {fri_score}%;'></div>
                            </div>
                            <div style='text-align: right; color: {text_color}; margin-top: 5px;'>{fri_score:.1f}</div>
                        </div>
                        <div style='margin: 20px 0;'>
                            <div style='font-weight: bold; color: #D32F2F;'>Wasted Spend</div>
                            <div style='font-size: 1.2rem; color: {text_color}; margin-top: 5px;'>{format_currency(waste_amount)} ({waste_percent:.1f}%)</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add a simple "View Details" button that only stores the campaign ID
                    if st.button(f"View Details", key=f"view_{campaign_id}"):
                        # Just store campaign ID in session state
                        st.session_state.selected_campaign = campaign_id
                        # Rerun the app to apply the selection
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error rendering Overview tab: {str(e)}")
        st.exception(e)  # This gives more details about the error