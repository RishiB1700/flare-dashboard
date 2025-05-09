import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def calculate_waste_percentage(fri_score):
    """
    Convert FRI score to waste percentage using linear mapping:
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

def format_currency(value):
    """Format value as currency"""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return "$0.00"
    return f"${value:,.2f}"

def create_gauge_chart(fri_score, status):
    """Create a simplified plotly gauge chart for FRI score"""
    # Set colors based on status
    color_map = {
        'Healthy': '#4CAF50',
        'Friction': '#FFCA28',
        'Fatigue': '#FF9800',
        'Failure': '#F44336',
        'Unknown': '#9E9E9E'
    }
    
    color = color_map.get(status, '#9E9E9E')
    
    # Create a simple gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fri_score,
        number={'font': {'size': 40}},
        title={'text': f"Fatigue Risk Index<br><span style='font-size:1.2em; color:{color}'>{status}</span>"},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 20], 'color': '#E8F5E9'},
                {'range': [20, 50], 'color': '#FFF8E1'},
                {'range': [50, 75], 'color': '#FFF3E0'},
                {'range': [75, 100], 'color': '#FFEBEE'}
            ]
        }
    ))
    
    # Customize layout
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#111111" if st.session_state.get('theme', 'light') == 'light' else "#FFFFFF"}
    )
    
    return fig

def build_recommendations_tab(flare):
    """Build the recommendations tab with actionable insights"""
    try:
        # Add custom CSS for colored circles and timeline styling
        st.markdown("""
        <style>
        .circle-high {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #F44336;
            margin-right: 8px;
        }
        .circle-medium {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #FF9800;
            margin-right: 8px;
        }
        .circle-low {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: #4CAF50;
            margin-right: 8px;
        }
        .timeline-card {
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            height: 85px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .timeline-immediate {
            background-color: #FFEBEE;
        }
        .timeline-week {
            background-color: #FFF8E1;
        }
        .timeline-next {
            background-color: #E8F5E9;
        }
        .timeline-card h4 {
            margin: 0 0 10px 0;
            font-size: 1.1rem;
            width: 100%;
            text-align: center;
        }
        .timeline-card p {
            margin: 0;
            font-size: 0.9rem;
            width: 100%;
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        
        # Check if recommendations can be generated
        if flare.fatigue_scores is None or len(flare.fatigue_scores) == 0:
            st.warning("No campaign data available. Please process data first.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Get recommendations for all campaigns
        recommendations = flare.get_campaign_recommendations()
        campaign_ids = list(recommendations.keys())
        
        if not campaign_ids:
            st.warning("No recommendations found. Please process campaign data first.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Create a mapping for display names
        recommendation_display = {}
        for campaign in campaign_ids:
            rec = recommendations[campaign]
            recommendation_display[campaign] = f"{campaign} - {rec['status']}"
        
        # Use selected_campaign from session state if available
        if 'selected_campaign' in st.session_state and st.session_state.selected_campaign in campaign_ids:
            default_index = campaign_ids.index(st.session_state.selected_campaign)
        else:
            default_index = 0
            st.session_state.selected_campaign = campaign_ids[0]
        
        # Create campaign selector
        selected_campaign = st.selectbox(
            "Select Campaign", 
            campaign_ids,
            index=default_index,
            format_func=lambda x: recommendation_display[x],
            key="rec_campaign_select"
        )
        
        # Update session state
        st.session_state.selected_campaign = selected_campaign
        
        # Get recommendations for the selected campaign
        campaign_rec = recommendations[selected_campaign]
        
        # Fix potential inconsistencies in the recommendations
        if campaign_rec['status'] == 'Failure' and campaign_rec['risk_level'] == 'Minimal':
            campaign_rec['risk_level'] = 'Critical' 
        if campaign_rec['status'] == 'Failure' and campaign_rec['fri_score'] < 50:
            campaign_rec['fri_score'] = 85.0
        
        # Create two-column layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # FRI Score visualization using Plotly gauge
            fri_score = campaign_rec.get('fri_score', 0)
            status = campaign_rec.get('status', 'Unknown')
            risk_level = campaign_rec.get('risk_level', 'Unknown')
            
            try:
                # Display FRI gauge using Plotly
                gauge_fig = create_gauge_chart(fri_score, status)
                st.plotly_chart(gauge_fig, use_container_width=True)
            except Exception as gauge_error:
                # Fallback to simple display if chart fails
                st.error(f"Unable to display gauge chart. {gauge_error}")
                st.info(f"FRI Score: {fri_score} - Status: {status}")
            
            # Risk level display - use a styled info box
            risk_colors = {
                'Critical': "#F44336",
                'High': "#FF5722",
                'Medium': "#FF9800",
                'Low': "#8BC34A",
                'Minimal': "#4CAF50"
            }
            risk_color = risk_colors.get(risk_level, "#9E9E9E")
            
            st.markdown(
                f"""
                <div style="padding: 10px; background-color: #f5f5f5; border-radius: 5px; margin-bottom: 20px;">
                    <span style="font-weight: bold; color: {risk_color};">Risk Level: {risk_level}</span>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Campaign context metrics
            st.markdown("### Campaign Context")
            
            campaign_data = flare.fatigue_scores[flare.fatigue_scores['campaign_id'] == selected_campaign]
            
            if not campaign_data.empty:
                # Get latest data point
                latest = campaign_data.iloc[-1]
                
                # Get campaign age
                campaign_age = latest.get('campaign_age', len(campaign_data))
                
                # Calculate metrics
                total_spend = campaign_data['spend'].sum()
                
                # Calculate CTR trend
                early_period = min(3, len(campaign_data) // 4)
                late_period = min(3, len(campaign_data) // 4)
                
                if early_period > 0 and late_period > 0:
                    early_ctr = campaign_data.iloc[:early_period]['ctr'].mean() * 100
                    late_ctr = campaign_data.iloc[-late_period:]['ctr'].mean() * 100
                    ctr_trend = ((late_ctr - early_ctr) / early_ctr) * 100 if early_ctr > 0 else 0
                else:
                    ctr_trend = 0
                
                # Calculate waste metrics
                fri_score = 0 if pd.isna(latest['fri_score']) else latest['fri_score']
                waste_percentage = calculate_waste_percentage(fri_score) * 100
                waste_amount = total_spend * (waste_percentage / 100)
                
                # Display simple context metrics
                context_cols = st.columns(2)
                
                with context_cols[0]:
                    st.metric("Campaign Age", f"{campaign_age} days")
                    # Display CTR Trend with the value but without the redundant delta
                    if ctr_trend < 0:
                        st.metric("CTR Trend", f"↓ {abs(ctr_trend):.1f}%")
                    else:
                        st.metric("CTR Trend", f"↑ {ctr_trend:.1f}%")
                
                with context_cols[1]:
                    st.metric("Total Spend", format_currency(total_spend))
                    # Display Wasted Spend without the delta
                    st.metric("Wasted Spend", format_currency(waste_amount))
                    # Display waste percentage separately if needed
                    st.markdown(f"<div style='font-size: 0.8rem; color: #666;'>↑ {waste_percentage:.1f}%</div>", unsafe_allow_html=True)
        
        with col2:
            # Recommendations section
            st.subheader("Recommended Actions")
            
            # Determine priority based on risk level
            priority_map = {
                "Critical": "High",
                "High": "High", 
                "Medium": "Medium", 
                "Low": "Low"
            }
            
            priority = priority_map.get(campaign_rec["risk_level"], "Medium")
            
            # Display priority using styled container
            priority_colors = {
                'High': "#F44336",
                'Medium': "#FF9800",
                'Low': "#4CAF50"
            }
            priority_color = priority_colors.get(priority, "#FF9800")
            
            st.markdown(
                f"""
                <div style="margin-bottom: 15px; background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
                    <span style="font-weight: bold;">Priority: </span>
                    <span style="color: {priority_color}; font-weight: bold;">{priority}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.write("Based on the current fatigue stage and campaign performance, these actions are recommended:")
            
            # Display recommendations using Streamlit components with colored circles
            if "actions_with_reasons" in campaign_rec:
                for i, action_data in enumerate(campaign_rec["actions_with_reasons"]):
                    action = action_data["action"]
                    reason = action_data["reason"]
                    
                    action_priority = "High" if i < 2 else ("Medium" if i < 4 else "Low")
                    priority_color_class = f"circle-{action_priority.lower()}"
                    
                    # Create header with color indicator
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; margin-bottom: 5px;">
                            <div class="{priority_color_class}"></div>
                            <strong>{action_priority}:</strong> {action}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Use standard expander for the reason
                    with st.expander("Details", expanded=True):
                        st.markdown(f"*{reason}*")
            else:
                # Fallback to simpler recommendation format
                for i, action in enumerate(campaign_rec["actions"]):
                    action_priority = "High" if i < 2 else ("Medium" if i < 4 else "Low")
                    priority_color_class = f"circle-{action_priority.lower()}"
                    
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; margin-bottom: 10px; padding: 10px; background-color: #f5f5f5; border-radius: 5px;">
                            <div class="{priority_color_class}"></div>
                            <div><strong>{action_priority}:</strong> {action}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            # Add implementation timeline with better styling
            st.subheader("Implementation Timeline")
            
            # Create timeline using columns with improved styling
            timeline_cols = st.columns(3)
            
            with timeline_cols[0]:
                st.markdown("""
                <div class="timeline-card timeline-immediate">
                    <h4 style="color: #D32F2F;">Immediate</h4>
                    <p>Within 24-48 hours</p>
                </div>
                """, unsafe_allow_html=True)
            
            with timeline_cols[1]:
                st.markdown("""
                <div class="timeline-card timeline-week">
                    <h4 style="color: #F57F17;">This Week</h4>
                    <p>Within 3-7 days</p>
                </div>
                """, unsafe_allow_html=True)
            
            with timeline_cols[2]:
                st.markdown("""
                <div class="timeline-card timeline-next">
                    <h4 style="color: #2E7D32;">Next Cycle</h4>
                    <p>7+ days</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error rendering Recommendations tab: {str(e)}")