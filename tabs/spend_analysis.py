import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def calculate_waste_percentage(fri_score):
    """
    Calculate waste percentage from FRI score using linear mapping:
    FRI 0 → 10% waste
    FRI 50 → 40% waste
    FRI 100 → 70% waste
    
    Handles NaN values and ensures proper calculation
    """
    # Check for NaN or invalid values
    if pd.isna(fri_score) or not isinstance(fri_score, (int, float)):
        return 0.1  # Default to minimal waste (10%)
    
    # Ensure fri_score is within valid range
    fri_score = max(0, min(100, fri_score))
    
    # Linear formula: waste = min_waste + (fri_score / max_fri) * (max_waste - min_waste)
    min_waste = 0.1  # 10%
    max_waste = 0.7  # 70%
    max_fri = 100.0
    
    waste_percentage = min_waste + (fri_score / max_fri) * (max_waste - min_waste)
    # Cap at 70%
    waste_percentage = min(waste_percentage, max_waste)
    
    return waste_percentage

def format_currency(value):
    """Format value as currency"""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return "$0.00"
    return f"${value:,.2f}"

def create_spend_waste_chart(waste_estimates):
    """Create a stacked bar chart showing spend vs waste"""
    # Extract data
    campaigns = []
    total_spend = []
    wasted_spend = []
    
    for campaign, data in waste_estimates.items():
        if isinstance(data, dict) and 'total_spend' in data and 'wasted_spend' in data:
            campaigns.append(campaign)
            total_spend.append(data["total_spend"])
            wasted_spend.append(data["wasted_spend"])
    
    # Calculate effective spend (total - wasted)
    effective_spend = [t - w for t, w in zip(total_spend, wasted_spend)]
    
    # Create figure
    fig = go.Figure()
    
    # Add effective spend bars
    fig.add_trace(go.Bar(
        y=campaigns,
        x=effective_spend,
        name='Effective Spend',
        orientation='h',
        marker=dict(color='#4CAF50')
    ))
    
    # Add wasted spend bars
    fig.add_trace(go.Bar(
        y=campaigns,
        x=wasted_spend,
        name='Wasted Spend',
        orientation='h',
        marker=dict(color='#FF5A5F')  # Updated to FLARE brand color
    ))
    
    # Update layout with theme-appropriate colors
    text_color = '#ffffff' if st.session_state.get('theme', 'light') == 'dark' else '#111111'
    
    fig.update_layout(
        barmode='stack',
        title='Campaign Spend Efficiency',
        xaxis=dict(
            title='Spend ($)',
            tickformat='$,.0f'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=400,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color)
    )
    
    return fig

def build_spend_analysis_tab(flare):
    """Build the spend analysis tab with waste metrics"""
    try:
        st.markdown('<div class="dashboard-card">', unsafe_allow_html=True)
        
        # Check if fatigue scores are available
        if flare.fatigue_scores is None or len(flare.fatigue_scores) == 0:
            st.warning("No campaign data available. Please process data first.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Update waste estimates with dynamic calculation
        waste_estimates = flare.estimate_wasted_spend()
        
        if not waste_estimates:
            st.warning("No waste data to display. Please process campaign data first.")
            st.markdown('</div>', unsafe_allow_html=True)
            return
        
        # Fix waste calculations to handle any NaN values
        for campaign, data in waste_estimates.items():
            if isinstance(data, dict):
                # Get the latest FRI score
                campaign_data = flare.fatigue_scores[flare.fatigue_scores['campaign_id'] == campaign]
                if not campaign_data.empty:
                    latest_fri = campaign_data.iloc[-1]['fri_score']
                    if pd.isna(latest_fri):
                        latest_fri = 0  # Default to 0 if NaN
                    
                    # Calculate dynamic waste percentage based on FRI
                    waste_percentage = calculate_waste_percentage(latest_fri)
                    total_spend = data["total_spend"]
                    wasted_spend = total_spend * waste_percentage
                    
                    # Update values in waste_estimates with proper handling of NaN
                    waste_estimates[campaign]["waste_percentage"] = float(waste_percentage * 100)
                    waste_estimates[campaign]["wasted_spend"] = float(wasted_spend)
                    waste_estimates[campaign]["recoverable_spend"] = float(wasted_spend)
        
        # Recalculate total waste for summary
        total_waste = sum(
            data["wasted_spend"] for campaign, data in waste_estimates.items() 
            if isinstance(data, dict) and "wasted_spend" in data
        )
        
        # Get summary data
        summary = flare.get_summary_report()
        
        # Update summary waste data
        summary["estimated_waste"] = float(total_waste)
        if summary["total_spend"] > 0:
            summary["waste_percentage"] = float(total_waste / summary["total_spend"] * 100)
        
        # Summary metrics in cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Campaign Spend", 
                format_currency(summary["total_spend"]),
                help="Total expenditure across all campaigns"
            )
        
        with col2:
            waste_percentage = summary["waste_percentage"]
            st.metric(
                "Estimated Wasted Spend", 
                format_currency(summary["estimated_waste"]),
                f"{waste_percentage:.1f}%",
                help="Estimated spend lost due to ad fatigue"
            )
        
        with col3:
            # Calculate potential savings
            potential_savings = total_waste * 0.7  # Assumption: 70% of waste could be recovered
            
            st.metric(
                "Potential Monthly Savings", 
                format_currency(potential_savings),
                help="Estimated savings with improved fatigue management"
            )
        
        st.divider()  # Add divider between sections
        
        # Create visualization tabs
        waste_tabs = st.tabs(["Waste by Campaign", "Spend Efficiency", "Optimization Impact"])
        
        with waste_tabs[0]:
            # Create waste by campaign table
            waste_data = []
            
            for campaign, data in waste_estimates.items():
                if isinstance(data, dict) and "total_spend" in data and "wasted_spend" in data:
                    waste_data.append({
                        "Campaign": campaign,
                        "Total Spend": data["total_spend"],
                        "Waste %": data["waste_percentage"],
                        "Wasted Spend": data["wasted_spend"],
                        "Recoverable": data["recoverable_spend"] if "recoverable_spend" in data else data["wasted_spend"]
                    })
            
            if not waste_data:
                st.warning("No waste data available to display.")
            else:
                waste_df = pd.DataFrame(waste_data)
                
                # Get color based on theme
                text_color = '#ffffff' if st.session_state.get('theme', 'light') == 'dark' else '#111111'
                
                # Create bar chart for waste by campaign with FLARE colors
                fig = px.bar(
                    waste_df,
                    x="Wasted Spend",
                    y="Campaign",
                    orientation='h',
                    color="Waste %",
                    color_continuous_scale=["#FFCDD2", "#FF5A5F", "#D32F2F"],  # FLARE palette
                    labels={"Wasted Spend": "Wasted Spend ($)", "Campaign": "Campaign", "Waste %": "Waste Percentage (%)"},
                    hover_data=["Total Spend", "Waste %", "Recoverable"]
                )
                
                fig.update_layout(
                    height=400,
                    margin=dict(l=10, r=10, t=30, b=10),
                    yaxis={'categoryorder':'total ascending'},
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=text_color)
                )
                
                # Format hover template
                fig.update_traces(
                    hovertemplate="<b>%{y}</b><br>" +
                                "Wasted Spend: $%{x:.2f}<br>" +
                                "Total Spend: $%{customdata[0]:.2f}<br>" +
                                "Waste Percentage: %{customdata[1]:.1f}%<br>" +
                                "Recoverable: $%{customdata[2]:.2f}<br>"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display data table
                st.dataframe(waste_df.style.format({
                    "Total Spend": "$ {:,.0f}",
                    "Wasted Spend": "$ {:,.0f}",
                    "Waste %": "{:.1f}%",
                    "Recoverable": "$ {:,.0f}"
                }))
        
        with waste_tabs[1]:
            # Create stacked bar chart showing effective vs wasted spend
            if len(waste_estimates) > 0:
                fig = create_spend_waste_chart(waste_estimates)
                st.plotly_chart(fig, use_container_width=True)
                
                # Add explanation with updated styling
                st.markdown(
                    f"""
                    <div style="padding: 20px; background-color: rgba(255,90,95,0.05); border-radius: 10px; margin: 20px 0; border: 1px solid rgba(255,90,95,0.1);">
                        <h3 style="margin-top: 0; color: #FF5A5F; font-weight: 600;">Understanding Spend Efficiency</h3>
                        <p>This chart shows how much of your ad spend is being effectively utilized (green) versus wasted due to ad fatigue (red).</p>
                        <p style="margin-bottom: 0;">Campaigns with larger red portions are experiencing more severe fatigue and should be prioritized for optimization.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.warning("No spend efficiency data available to display.")
        
        with waste_tabs[2]:
            # Create projection chart showing potential impact of optimization
            
            # Prepare projection data
            current_waste = total_waste
            current_effective = summary["total_spend"] - current_waste
            
            # Assume 70% waste reduction with FLARE
            optimized_waste = current_waste * 0.3
            optimized_effective = summary["total_spend"] - optimized_waste
            
            # Add data points
            projection_data = []
            projection_data.append({
                "Scenario": "Current",
                "Category": "Effective Spend",
                "Value": current_effective
            })
            projection_data.append({
                "Scenario": "Current",
                "Category": "Wasted Spend",
                "Value": current_waste
            })
            projection_data.append({
                "Scenario": "With FLARE",
                "Category": "Effective Spend",
                "Value": optimized_effective
            })
            projection_data.append({
                "Scenario": "With FLARE",
                "Category": "Wasted Spend",
                "Value": optimized_waste
            })
            
            # Create dataframe
            projection_df = pd.DataFrame(projection_data)
            
            # Get color based on theme
            text_color = '#ffffff' if st.session_state.get('theme', 'light') == 'dark' else '#111111'
            
            # Create grouped bar chart with FLARE colors
            fig = px.bar(
                projection_df,
                x="Scenario",
                y="Value",
                color="Category",
                barmode="stack",
                color_discrete_map={
                    "Effective Spend": "#4CAF50",
                    "Wasted Spend": "#FF5A5F"  # Updated to FLARE brand color
                },
                labels={"Value": "Spend ($)", "Scenario": "", "Category": ""}
            )
            
            # Add optimization impact annotation
            savings = current_waste - optimized_waste
            fig.add_annotation(
                x=1,
                y=optimized_effective + (optimized_waste / 2),
                text=f"${savings:,.2f} savings",
                showarrow=True,
                arrowhead=1,
                arrowcolor="#FF5A5F",  # Updated to FLARE brand color
                arrowsize=1,
                arrowwidth=2,
                ax=-40,
                ay=-40,
                font=dict(color=text_color)
            )
            
            # Update layout
            fig.update_layout(
                height=400,
                margin=dict(l=10, r=10, t=30, b=10),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=text_color)
            )
            
            # Format y-axis as currency
            fig.update_yaxes(tickprefix="$", tickformat=",")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add explanation and call to action with updated styling
            st.markdown(
                f"""
                <div style="padding: 24px; background-color: rgba(255,90,95,0.05); border-radius: 12px; margin-top: 20px; border: 1px solid rgba(255,90,95,0.1);">
                    <h3 style="margin-top: 0; color: #FF5A5F; font-weight: 600;">Optimization Impact</h3>
                    <p>By implementing FLARE recommendations, you could potentially save <strong>{format_currency(savings)}</strong> in wasted ad spend.</p>
                    <p>This represents a <strong>{(savings/current_waste*100):.1f}%</strong> reduction in waste and a <strong>{(savings/summary["total_spend"]*100):.1f}%</strong> overall improvement in campaign efficiency.</p>
                    <div style="text-align: center; margin-top: 20px;">
                        <button style="background-color: #FF5A5F; color: white; border: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; cursor: pointer; box-shadow: 0 2px 5px rgba(255,90,95,0.3);">
                            Download Full Analysis Report
                        </button>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error rendering Spend Analysis tab: {str(e)}")