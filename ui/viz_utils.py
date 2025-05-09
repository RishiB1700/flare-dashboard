import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

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
    
    # Add CTR line with improved styling
    try:
        fig.add_trace(
            go.Scatter(
                x=campaign_data['date'], 
                y=campaign_data['ctr']*100, 
                name="CTR (%)", 
                line=dict(color="#0F2E4C", width=2.5),
                mode='lines+markers',
                marker=dict(size=6, color="#0F2E4C")
            ),
            row=1, col=1
        )
    except Exception as e:
        st.warning(f"Error adding CTR data: {e}")
    
    # Add CPA line if available with improved styling
    try:
        if 'cpa' in campaign_data.columns and not campaign_data['cpa'].isnull().all():
            fig.add_trace(
                go.Scatter(
                    x=campaign_data['date'], 
                    y=campaign_data['cpa'], 
                    name="CPA ($)", 
                    line=dict(color="#2C5F8E", width=2.5),
                    mode='lines+markers',
                    marker=dict(size=6, color="#2C5F8E")
                ),
                row=2, col=1
            )
    except Exception as e:
        st.warning(f"Error adding CPA data: {e}")
    
    # Create color map for FRI points - using our new branded colors
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
            # Fill NaN values in fri_score
            campaign_data['fri_score'] = campaign_data['fri_score'].fillna(0)
            
            fig.add_trace(
                go.Scatter(
                    x=campaign_data['date'], 
                    y=campaign_data['fri_score'],
                    mode='lines+markers',
                    name="FRI Score", 
                    marker=dict(
                        size=8,
                        color=[stage_colors.get(stage, '#9E9E9E') for stage in campaign_data['fatigue_stage']],
                        line=dict(width=1, color='DarkSlateGrey')
                    ),
                    line=dict(color='#7f7f7f', width=1.5, dash='dot')
                ),
                row=3, col=1
            )
            
            # Add threshold lines for FRI with improved styling
            fig.add_hline(y=20, line=dict(color='#FFCA28', width=1, dash='dash'), row=3, col=1)
            fig.add_hline(y=50, line=dict(color='#FF9800', width=1, dash='dash'), row=3, col=1)
            fig.add_hline(y=75, line=dict(color='#F44336', width=1, dash='dash'), row=3, col=1)
            
            # Add annotations for threshold lines
            fig.add_annotation(
                x=campaign_data['date'].iloc[0],
                y=20,
                text="Friction",
                showarrow=False,
                xshift=-40,
                font=dict(size=10, color="#FFCA28"),
                row=3, col=1
            )
            
            fig.add_annotation(
                x=campaign_data['date'].iloc[0],
                y=50,
                text="Fatigue",
                showarrow=False,
                xshift=-40,
                font=dict(size=10, color="#FF9800"),
                row=3, col=1
            )
            
            fig.add_annotation(
                x=campaign_data['date'].iloc[0],
                y=75,
                text="Failure",
                showarrow=False,
                xshift=-40,
                font=dict(size=10, color="#F44336"),
                row=3, col=1
            )
    except Exception as e:
        st.warning(f"Error adding FRI data: {e}")
    
    # Update layout with theme-specific settings and improved styling
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
    
    # Update axes for better readability
    fig.update_xaxes(
        showgrid=True,
        gridwidth=0.5,
        gridcolor='rgba(150,150,150,0.1)',
        zeroline=False,
        showline=True,
        linewidth=0.5,
        linecolor='rgba(150,150,150,0.5)'
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=0.5,
        gridcolor='rgba(150,150,150,0.1)',
        zeroline=False,
        showline=True,
        linewidth=0.5,
        linecolor='rgba(150,150,150,0.5)'
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
    
    if not campaigns:
        # Handle empty data
        fig = go.Figure()
        text_color = '#ffffff' if st.session_state.get('theme', 'light') == 'dark' else '#111111'
        fig.update_layout(
            title="No waste data available",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=text_color)
        )
        fig.add_annotation(
            text="Waste data could not be calculated or is empty",
            showarrow=False,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            font=dict(size=14, color=text_color)
        )
        return fig
    
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
        marker=dict(color='#F44336')
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
    
    # Update axes for better readability
    fig.update_xaxes(
        showgrid=True,
        gridwidth=0.5,
        gridcolor='rgba(150,150,150,0.1)',
        zeroline=False
    )
    
    fig.update_yaxes(
        showgrid=False,
        zeroline=False
    )
    
    # Format hover template
    fig.update_traces(
        hovertemplate="%{y}<br>%{x:$,.0f}<br>%{data.name}"
    )
    
    return fig

def enhance_fri_display(campaign_rec):
    """
    Create an improved FRI score visualization with gauge display
    This version works with both light and dark themes
    """
    status = campaign_rec['status'] if 'status' in campaign_rec else 'Unknown'
    fri_score = campaign_rec['fri_score'] if 'fri_score' in campaign_rec else 0
    risk_level = campaign_rec['risk_level'] if 'risk_level' in campaign_rec else 'Unknown'
    
    # Determine color based on status
    status_color = {
        'Healthy': '#4CAF50',
        'Friction': '#FFCA28',
        'Fatigue': '#FF9800',
        'Failure': '#F44336',
        'Unknown': '#9E9E9E'
    }.get(status, '#9E9E9E')
    
    # Determine text color based on theme
    text_color = '#ffffff' if st.session_state.get('theme', 'light') == 'dark' else '#111111'
    bg_color = '#262730' if st.session_state.get('theme', 'light') == 'dark' else '#ffffff'
    
    # Create a visual gauge for the FRI score
    gauge_html = f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <div style="position: relative; width: 200px; height: 100px; margin: 0 auto; overflow: hidden;">
            <div style="position: absolute; width: 200px; height: 200px; border-radius: 100px; background: linear-gradient(90deg, #4CAF50, #FFCA28, #FF9800, #F44336); clip: rect(0px, 200px, 100px, 0px);"></div>
            <div style="position: absolute; width: 160px; height: 160px; top: 20px; left: 20px; border-radius: 80px; background-color: {bg_color}; clip: rect(0px, 160px, 80px, 0px);"></div>
            <div style="position: absolute; bottom: 5px; left: 100px; transform: translateX(-50%); font-size: 2.5rem; font-weight: bold; color: {text_color};">{fri_score}</div>
            <div style="position: absolute; bottom: 0; left: {fri_score}%; width: 3px; height: 30px; background-color: {status_color}; transform: translateX(-50%);"></div>
        </div>
        <div style="margin-top: 15px; font-size: 1.5rem; font-weight: bold; color: {status_color};">{status}</div>
        <div style="margin-top: 5px; font-size: 1.2rem; color: {text_color};">Risk Level: {risk_level}</div>
    </div>
    """
    
    return gauge_html

def create_fri_heatmap(fri_data):
    """
    Create a heatmap visualization of FRI scores across campaigns and time
    """
    if fri_data.empty:
        return None
    
    # Get unique campaigns and dates
    campaigns = fri_data['campaign_id'].unique()
    dates = pd.to_datetime(fri_data['date']).dt.strftime('%Y-%m-%d').unique()
    
    # Create a pivot table of FRI scores
    pivot_data = fri_data.pivot_table(
        index='campaign_id', 
        columns=pd.to_datetime(fri_data['date']).dt.strftime('%Y-%m-%d'),
        values='fri_score',
        aggfunc='mean'
    ).fillna(0)
    
    # Create heatmap
    fig = px.imshow(
        pivot_data,
        labels=dict(x="Date", y="Campaign", color="FRI Score"),
        x=pivot_data.columns,
        y=pivot_data.index,
        color_continuous_scale=[
            "#4CAF50",  # Green (Healthy)
            "#FFCA28",  # Yellow (Friction)
            "#FF9800",  # Orange (Fatigue) 
            "#F44336"   # Red (Failure)
        ],
        zmin=0, zmax=100
    )
    
    # Update layout
    text_color = '#ffffff' if st.session_state.get('theme', 'light') == 'dark' else '#111111'
    fig.update_layout(
        title="FRI Score Heatmap",
        xaxis_title="Date",
        yaxis_title="Campaign",
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=text_color)
    )
    
    return fig

def diagnose_tab_functionality(tab_name):
    """
    Helper function to diagnose tab functionality issues
    Returns a tuple of (is_ok, message)
    """
    import sys
    import importlib
    
    try:
        # Check if required modules are available
        required_modules = ['streamlit', 'pandas', 'plotly', 'numpy']
        missing_modules = []
        
        for module in required_modules:
            try:
                importlib.import_module(module)
            except ImportError:
                missing_modules.append(module)
        
        if missing_modules:
            return False, f"Missing required modules: {', '.join(missing_modules)}"
        
        # Check Python version
        py_version = sys.version_info
        if py_version.major < 3 or (py_version.major == 3 and py_version.minor < 7):
            return False, f"Python version {py_version.major}.{py_version.minor} may not be compatible. Python 3.7+ is recommended."
        
        # Check if theme is in session state
        if not hasattr(st, 'session_state') or 'theme' not in st.session_state:
            st.session_state.theme = 'light'
            return True, "Warning: Theme was not set in session state, defaulted to 'light'"
        
        return True, "Tab diagnostics passed successfully"
    
    except Exception as e:
        return False, f"Error during {tab_name} tab diagnostics: {str(e)}"

def troubleshoot_tabs():
    """Show troubleshooting information for tab issues"""
    with st.expander("Troubleshooting Information"):
        st.write("### Tab Troubleshooting")
        st.write("If you're experiencing issues with this tab, try the following:")
        st.write("1. Check that your data has all required columns")
        st.write("2. Ensure session state is properly initialized")
        st.write("3. Check console logs for any JavaScript errors")
        st.write("4. Try refreshing the page or clearing cache")
        
        st.write("### Session State Information")
        st.write(st.session_state)
