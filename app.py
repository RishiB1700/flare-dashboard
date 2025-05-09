"""
FLARE Dashboard - Main Application File

This app presents an interactive dashboard for the Fatigue Learning 
and Adaptive Response Engine (FLARE) that detects and helps manage
digital ad fatigue.
"""
import streamlit as st
import os
import sys
import pandas as pd
import time
import numpy as np

# Fix path to load modules correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Core engine and helpers
from ui.theme import apply_css, apply_theme_css
from ui.logo import render_logo, get_base64_encoded_image
from data.data_generator import load_sample_data, validate_data
from core.flare_utils import get_flare_engine, process_data

# Import tabs
from tabs.overview import build_overview_tab
from tabs.campaign_details import build_campaign_details_tab
from tabs.recommendations import build_recommendations_tab
from tabs.spend_analysis import build_spend_analysis_tab
from tabs.ai_forecasting import build_ai_forecasting_tab

# Get logo for page icon
logo_paths = [
    "/Users/hrishibhanushali/Documents/Flare/assets/Flare logo.png",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "Flare logo.png"),
    "assets/Flare logo.png"
]

# Try to find the logo
logo_base64 = None
for path in logo_paths:
    logo_base64 = get_base64_encoded_image(path)
    if logo_base64:
        break

# Streamlit page config
st.set_page_config(
    page_title="FLARE Dashboard",
    page_icon=f"data:image/png;base64,{logo_base64}" if logo_base64 else "🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply basic CSS for styling but without overriding tab functionality
st.markdown("""
<style>
/* Base styling without overriding tab visibility */
section[data-testid="stSidebar"] {
    z-index: 999 !important;
}

[data-testid="stHeader"] {
    z-index: 998 !important;
}

/* Fix font consistency */
body, p, h1, h2, h3, h4, h5, h6, div, span, button, input, select, textarea {
    font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
}

/* Enhanced loading indicators */
.processing-container {
    border-radius: 10px;
    padding: 20px;
    background-color: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin: 20px 0;
    text-align: center;
}

.dark-mode .processing-container {
    background-color: #1E1E1E;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}

.progress-indicator {
    height: 15px;
    background-color: rgba(0,0,0,0.05);
    border-radius: 8px;
    overflow: hidden;
    margin: 15px 0;
    position: relative;
}

.progress-indicator-bar {
    height: 100%;
    background: linear-gradient(90deg, #FF5A5F, #FF8A8F);
    border-radius: 8px;
    transition: width 0.5s ease-out;
}

.dark-mode .progress-indicator-bar {
    background: linear-gradient(90deg, #0F2E4C, #2C5F8E);
}
</style>
""", unsafe_allow_html=True)

# Add this basic CSS fix to ensure clean Streamlit metrics display
st.markdown("""
<style>
/* Simple clean Streamlit metrics */
div[data-testid="metric-container"] {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    padding: 15px !important;
    margin: 10px 0 !important;
}

.dark-mode div[data-testid="metric-container"] {
    background-color: #1E1E1E;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

div[data-testid="metric-container"] > div:first-child {
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    margin-bottom: 0.3rem !important;
}

div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-size: 2.0rem !important;
    font-weight: 700 !important;
}

div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}
</style>
""", unsafe_allow_html=True)

# Apply global CSS and initialize theme
apply_css()
if "theme" not in st.session_state:
    st.session_state.theme = "light"  # Set light mode as default
apply_theme_css(st.session_state.theme)

# Apply theme-specific class for dark mode
if st.session_state.theme == "dark":
    st.markdown("<style>body {}</style><script>document.body.classList.add('dark-mode');</script>", unsafe_allow_html=True)
else:
    st.markdown("<style>body {}</style><script>document.body.classList.remove('dark-mode');</script>", unsafe_allow_html=True)

# Initialize data processed flag if not present
if "data_processed" not in st.session_state:
    st.session_state.data_processed = False

# Initialize active tab if not present
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Overview"

# Initialize FLARE engine
@st.cache_resource
def get_cached_flare_engine():
    return get_flare_engine()

flare = get_cached_flare_engine()

# --- SIDEBAR ---
with st.sidebar:
    # Use the improved logo with error handling
    try:
        st.markdown(render_logo(type="horizontal"), unsafe_allow_html=True)
    except Exception as e:
        # Fallback to text-only display if all else fails
        st.markdown("<h3>FLARE</h3>", unsafe_allow_html=True)
    
    st.markdown("---")

    # Theme Toggle
    st.markdown("### Display Settings")
    col1, col2 = st.columns(2)
    if col1.button("Light", key="light_mode_button", use_container_width=True):
        st.session_state.theme = "light"
        apply_theme_css("light")
        st.rerun()
    if col2.button("Dark", key="dark_mode_button", use_container_width=True):
        st.session_state.theme = "dark"
        apply_theme_css("dark")
        st.rerun()

    st.markdown("---")
    st.markdown("### Data Source")
    
    # Add spacing for better appearance
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    
    # Add some spacing between uploader and checkbox
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    
    use_sample = st.checkbox("Use sample data", value=True if not uploaded_file else False)
    
    # Add spacing before process button
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    process_data_clicked = st.button("Process Data", type="primary", use_container_width=True)

    # Process data only when button is clicked (not on every rerun)
    if process_data_clicked:
        try:
            # Show processing animation (in the main area, not sidebar)
            st.session_state.processing = True
            st.session_state.process_stage = "Starting"
            st.session_state.process_progress = 0.0
            
            # Load data
            if uploaded_file is not None:
                st.session_state.process_stage = "Loading uploaded data"
                st.session_state.process_progress = 0.2
                df = load_sample_data(uploaded_file)
            elif use_sample:
                st.session_state.process_stage = "Generating sample data"
                st.session_state.process_progress = 0.2
                df = load_sample_data()
            else:
                df = None
                st.sidebar.error("Please upload a CSV or enable sample data.")
                
            # Process data if available
            if df is not None:
                # Validate data
                st.session_state.process_stage = "Validating data"
                st.session_state.process_progress = 0.4
                is_valid, validation_message = validate_data(df)
                
                if not is_valid:
                    st.sidebar.error(validation_message)
                    st.session_state.processing = False
                else:
                    # Process with FLARE
                    st.session_state.process_stage = "Processing with FLARE"
                    st.session_state.process_progress = 0.6
                    
                    # Save to temp file for processing
                    temp_file = "temp_campaign_data.csv"
                    df.to_csv(temp_file, index=False)
                    
                    # Process data
                    flare.load_data(temp_file)
                    st.session_state.process_stage = "Preprocessing data"
                    st.session_state.process_progress = 0.7
                    flare.preprocess_data()
                    
                    st.session_state.process_stage = "Calculating fatigue scores"
                    st.session_state.process_progress = 0.9
                    flare.calculate_fatigue_scores()
                    
                    # Set the data processed flag
                    st.session_state.data_processed = True
                    st.session_state.process_progress = 1.0
                    st.session_state.process_stage = "Complete"
                    
                    # Store validation message if any
                    if validation_message:
                        st.session_state.validation_message = validation_message
                    
                    # Clear processing flag after a short delay
                    time.sleep(1)
                    st.session_state.processing = False
                    
                    # Rerun to update all tabs
                    st.rerun()
            else:
                st.session_state.processing = False
        except Exception as e:
            st.sidebar.error(f"Error processing data: {e}")
            st.session_state.processing = False

    st.markdown("---")
    st.markdown("### Connect Platforms")
    st.text_input("Google Ads ID", disabled=True)
    st.text_input("Meta Business ID", disabled=True)
    st.button("Connect", disabled=True, use_container_width=True)

    st.markdown("---")
    
    st.markdown("### Help & Debug")
    with st.expander("📘 About FLARE"):
        st.markdown("""
        FLARE is a predictive tool for detecting and mitigating advertising fatigue 
        using a proprietary Fatigue Risk Index (FRI). It analyzes campaign data to identify three stages of fatigue:
        
        1. **Friction**: Early signs of wear, minor CTR drop
        2. **Fatigue**: Engagement stagnation, rising CPA
        3. **Failure**: Sharp ROI decline, continued delivery with little return
        """)

    with st.expander("📚 Glossary"):
        st.markdown("""
        - **CTR**: Click Through Rate
        - **CPA**: Cost Per Acquisition
        - **ROI**: Return on Investment
        - **FRI**: Fatigue Risk Index
        """)

    with st.expander("🐞 Debug Tools"):
        if st.button("Show Session State", use_container_width=True):
            st.write(st.session_state)
        if st.button("Clear Session State", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key != "theme":  # Keep theme setting
                    del st.session_state[key]
            st.success("Session state cleared. Refresh the app.")

# --- MAIN CONTENT ---

# Show enhanced processing indicator if processing
if st.session_state.get("processing", False):
    # Create a centered progress bar in the main area
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    
    text_color = 'white'
    bg_gradient = '#0F2E4C, #2C5F8E' if st.session_state.get('theme', 'light') == 'dark' else '#FF5A5F, #FF8A8F'
    
    st.markdown(f"""
    <div class='processing-container'>
        <h2 style="margin-top: 0; font-weight: 600; color: {'white' if st.session_state.get('theme', 'light') == 'dark' else '#FF5A5F'};">
            Processing Data
        </h2>
        <h3 style="margin: 10px 0; font-weight: 400; color: {'white' if st.session_state.get('theme', 'light') == 'dark' else '#FF5A5F'};">
            {st.session_state.process_stage}
        </h3>
        
        <div class="progress-indicator">
            <div class="progress-indicator-bar" style="width: {st.session_state.process_progress * 100}%;"></div>
        </div>
        
        <p style="margin-bottom: 0;">Progress: {int(st.session_state.process_progress * 100)}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add a spinner as extra visual feedback
    with st.spinner(""):
        pass  # This just keeps the spinner active

# Add a small gap at the top for better appearance
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# Check if data is processed
if st.session_state.data_processed:
    # Header if not showing processing indicator
    st.markdown('<h1 style="margin-bottom: 0.5rem; color: #FF5A5F; font-family: system-ui, -apple-system, sans-serif; font-weight: 600;">FLARE Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="margin-top: 0; margin-bottom: 1rem; color: #666; font-size: 1.1rem; font-family: system-ui, -apple-system, sans-serif;">Fatigue Learning and Adaptive Response Engine</p>', unsafe_allow_html=True)
    
    # Show validation message if any
    if hasattr(st.session_state, 'validation_message') and st.session_state.validation_message:
        st.warning(st.session_state.validation_message)
    
    # Create the tab container and tabs
    tabs = st.tabs([
        "Overview",
        "Campaign Details",
        "Recommendations",
        "Spend Analysis",
        "AI Forecasting"
    ])
    
    # Build tab content based on which tab is selected
    # Overview Tab
    with tabs[0]:
        if hasattr(flare, 'fatigue_scores') and flare.fatigue_scores is not None:
            build_overview_tab(flare)
        else:
            st.info("Please process data first to view campaign overview.")

    # Campaign Details Tab
    with tabs[1]:
        if hasattr(flare, 'fatigue_scores') and flare.fatigue_scores is not None:
            build_campaign_details_tab(flare)
        else:
            st.info("Please process data first to view campaign details.")

    # Recommendations Tab
    with tabs[2]:
        if hasattr(flare, 'fatigue_scores') and flare.fatigue_scores is not None:
            build_recommendations_tab(flare)
        else:
            st.info("Please process data first to view recommendations.")

    # Spend Analysis Tab
    with tabs[3]:
        if hasattr(flare, 'fatigue_scores') and flare.fatigue_scores is not None:
            build_spend_analysis_tab(flare)
        else:
            st.info("Please process data first to view spend analysis.")

    # AI Forecasting Tab
    with tabs[4]:
        if hasattr(flare, 'fatigue_scores') and flare.fatigue_scores is not None:
            build_ai_forecasting_tab(flare)
        else:
            st.info("Please process data first to view AI forecasting.")

else:
    # Show landing page when no data is processed - ORIGINAL WELCOME MESSAGE, NO REPETITION
    st.markdown("<div style='max-width: 800px; margin: 30px auto; text-align: center;'>", unsafe_allow_html=True)
    
    # Add the logo with error handling
    try:
        st.markdown(render_logo(size="large", type="vertical"), unsafe_allow_html=True)
    except Exception as e:
        # Fallback to text-only display if logo fails
        st.markdown("<h1 style='font-size: 3rem; color: #FF5A5F; margin-bottom: 30px;'>FLARE</h1>", unsafe_allow_html=True)
    
    # Original welcome message
    st.markdown("<h2 style='margin-bottom: 15px; font-weight: 700; color: #333333;'>Welcome to FLARE</h2>", unsafe_allow_html=True)
    st.markdown("""
    <p style='font-size: 1.25rem; margin-bottom: 30px; color: #666;'>
        FLARE helps you detect and manage <strong>digital ad fatigue</strong> with our proprietary Fatigue Risk Index. 
        Identify early warning signs, get actionable recommendations, and reduce wasted ad spend.
    </p>
    """, unsafe_allow_html=True)
    
    # Dashboard preview placeholder
    st.markdown("""
    <div style="background-color: #f8f9fa; border-radius: 12px; padding: 30px; text-align: center; margin: 20px 0;">
        <p style="font-style: italic; color: #666;">Dashboard preview</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get started section
    st.markdown("<h2 style='margin: 40px 0 20px; font-weight: 600;'>Get Started</h2>", unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align: center; margin-bottom: 30px;'>
        To begin analyzing your campaigns, please use the <strong>Data Source</strong> section in the sidebar to:
    </p>
    """, unsafe_allow_html=True)
    
    # Create 3 columns for the steps
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown("""
        <div style="background-color: #f8f9fa; border-radius: 12px; border: 1px solid #e9ecef; padding: 20px; text-align: center; height: 100%;">
            <h3 style='margin-top: 0; color: #FF5A5F; font-weight: 600;'>Step 1</h3>
            <p style='color: #495057;'>Upload your campaign data CSV file or use our sample data</p>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[1]:
        st.markdown("""
        <div style="background-color: #f8f9fa; border-radius: 12px; border: 1px solid #e9ecef; padding: 20px; text-align: center; height: 100%;">
            <h3 style='margin-top: 0; color: #FF5A5F; font-weight: 600;'>Step 2</h3>
            <p style='color: #495057;'>Click the "Process Data" button in the sidebar</p>
        </div>
        """, unsafe_allow_html=True)
        
    with cols[2]:
        st.markdown("""
        <div style="background-color: #f8f9fa; border-radius: 12px; border: 1px solid #e9ecef; padding: 20px; text-align: center; height: 100%;">
            <h3 style='margin-top: 0; color: #FF5A5F; font-weight: 600;'>Step 3</h3>
            <p style='color: #495057;'>Explore the dashboard tabs to analyze your campaigns</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Closing div
    st.markdown("</div>", unsafe_allow_html=True)