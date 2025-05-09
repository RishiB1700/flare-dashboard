import streamlit as st
import os
import pandas as pd

def apply_css():
    """Apply base CSS for the FLARE dashboard with consistent fonts"""
    css = """
    /* Global Reset and Basic Layout */
    body {
        margin: 0;
        padding: 0;
        font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Consistent fonts across the entire dashboard - limited to 3 variations */
    body, p, div, span, button, input, select, textarea, label, th, td {
        font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        font-weight: 600 !important;
    }
    
    /* Logo font - can be different */
    .logo-text {
        font-family: system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        font-weight: 700 !important;
    }
    
    /* Fix for streamlit container spacing */
    .block-container {
        max-width: 95% !important;  /* Prevent content being cut off */
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    
    /* Let Streamlit handle tabs directly - DO NOT OVERRIDE TAB VISIBILITY */
    
    /* Ensure buttons are visible with consistent styling */
    .stButton>button {
        background-color: #FF5A5F !important;
        color: white !important;
        margin: 0.5rem 0;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        border: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background-color: #E65056 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
    }
    
    /* Enhanced progress animation */
    @keyframes progress-animation {
        0% { width: 0%; }
        100% { width: var(--target-width); }
    }
    
    .progress-container {
        width: 100%;
        background-color: rgba(0,0,0,0.05);
        border-radius: 10px;
        margin: 10px 0;
        overflow: hidden;
        height: 15px;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(to right, #FF5A5F, #FF8A8F);
        width: 0;
        transition: width 0.8s cubic-bezier(0.22, 1, 0.36, 1);
    }
    
    /* Loading indicator with animation */
    .processing-indicator {
        background: linear-gradient(to right, #FF5A5F, #FF8A8F);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(255, 90, 95, 0.3);
        margin: 30px 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 4px 12px rgba(255, 90, 95, 0.3); }
        50% { box-shadow: 0 4px 20px rgba(255, 90, 95, 0.5); }
        100% { box-shadow: 0 4px 12px rgba(255, 90, 95, 0.3); }
    }
    
    /* Main styles */
    .main-header {
        font-size: 2.6rem;
        font-weight: bold;
        color: #FF5A5F;
        margin-bottom: 0px;
        padding-bottom: 0px;
        letter-spacing: 0.5px;
    }

    .sub-header {
        font-size: 0.9rem;
        color: #666666;
        margin-top: 0px;
        padding-top: 0px;
        margin-bottom: 30px;
        letter-spacing: 0.5px;
    }

    /* Improved dashboard card with subtle shadow and smooth corners */
    .dashboard-card {
        background-color: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 25px;
        border: none !important;
        transition: all 0.3s ease;
    }
    
    .dashboard-card:hover {
        box-shadow: 0 4px 14px rgba(0,0,0,0.08);
    }
    
    /* Improved metric cards with better hover effect and shadow */
    .metric-card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 15px;
        border: none !important;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 12px 0;
        color: #0F2E4C;
    }

    .metric-label {
        font-size: 0.95rem;
        font-weight: 500;
        color: #666666;
        letter-spacing: 0.3px;
    }

    /* High risk campaign card with subtle gradient background */
    .risk-card {
        background: linear-gradient(to right, #FFF8F8, #FFF0F0);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(244,67,54,0.1);
        border-left: 4px solid #F44336;
        transition: all 0.3s ease;
    }
    
    .risk-card:hover {
        box-shadow: 0 6px 16px rgba(244,67,54,0.15);
    }

    /* Improved stage badges with better contrast and subtle glow */
    .stage-healthy {
        background-color: #4CAF50;
        color: white !important;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 0.3px;
        box-shadow: 0 2px 5px rgba(76,175,80,0.3);
    }

    .stage-friction {
        background-color: #FFCA28;
        color: #333 !important;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 0.3px;
        box-shadow: 0 2px 5px rgba(255,202,40,0.3);
    }

    .stage-fatigue {
        background-color: #FF9800;
        color: white !important;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 0.3px;
        box-shadow: 0 2px 5px rgba(255,152,0,0.3);
    }

    .stage-failure {
        background-color: #F44336;
        color: white !important;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 0.3px;
        box-shadow: 0 2px 5px rgba(244,67,54,0.3);
    }

    .stage-unknown {
        background-color: #9E9E9E;
        color: white !important;
        padding: 6px 12px;
        border-radius: 6px;
        font-weight: 600;
        letter-spacing: 0.3px;
        box-shadow: 0 2px 5px rgba(158,158,158,0.3);
    }

    /* Improved recommendation cards with better visuals */
    .recommendation-card {
        background-color: #F8F9FA;
        border-left: 5px solid #FF5A5F;
        padding: 18px;
        margin: 15px 0;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 8px rgba(255,90,95,0.1);
    }

    .recommendation-high {
        border-left: 5px solid #F44336;
        box-shadow: 0 2px 8px rgba(244,67,54,0.1);
    }

    .recommendation-medium {
        border-left: 5px solid #FF9800;
        box-shadow: 0 2px 8px rgba(255,152,0,0.1);
    }

    .recommendation-low {
        border-left: 5px solid #4CAF50;
        box-shadow: 0 2px 8px rgba(76,175,80,0.1);
    }

    .action-item {
        padding: 10px 0 10px 20px;
        border-bottom: 1px solid #EEEEEE;
        transition: all 0.2s ease;
    }

    .action-item:hover {
        background-color: rgba(0,0,0,0.02);
    }

    .action-item:last-child {
        border-bottom: none;
    }

    /* Improved metric change indicators with animations */
    .stat-change-up {
        color: #F44336;
        font-size: 0.85rem;
        font-weight: bold;
        animation: pulse 2s infinite;
    }

    .stat-change-down {
        color: #4CAF50;
        font-size: 0.85rem;
        font-weight: bold;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }

    .sidebar-logo {
        text-align: center;
        padding: 20px 0;
    }

    /* Improved tooltip with animation */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
    }

    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #333;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 8px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s, transform 0.3s;
        transform: translateY(10px);
        box-shadow: 0 3px 10px rgba(0,0,0,0.2);
    }

    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
        transform: translateY(0);
    }

    /* Improved animated progress bar with smoother animation */
    .progress-container {
        width: 100%;
        background-color: #f1f1f1;
        border-radius: 10px;
        margin: 10px 0;
        overflow: hidden;
    }

    .progress-bar {
        height: 10px;
        border-radius: 10px;
        background: linear-gradient(to right, #4CAF50, #8BC34A);
        width: 0;
        transition: width 0.8s cubic-bezier(0.22, 1, 0.36, 1);
    }
    
    /* Failure progress bar with different gradient */
    .progress-bar-failure {
        background: linear-gradient(to right, #F44336, #FF9800);
    }
    
    /* Fatigue progress bar with different gradient */
    .progress-bar-fatigue {
        background: linear-gradient(to right, #FF9800, #FFCA28);
    }

    /* Better landing page styling */
    .landing-container {
        text-align: center;
        max-width: 800px;
        margin: 0 auto;
        padding: 50px 0;
    }
    
    .landing-title {
        font-size: 3rem;
        color: #FF5A5F;
        margin-bottom: 20px;
        font-weight: 800;
    }
    
    .landing-subtitle {
        font-size: 1.4rem;
        color: #666;
        margin-bottom: 40px;
        font-weight: 300;
        line-height: 1.4;
    }
    
    .landing-icon {
        margin-bottom: 20px;
    }
    
    /* Step cards on landing page */
    .step-card {
        text-align: center;
        padding: 25px;
        background-color: #f8f9fa;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        height: 100%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    
    .step-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    /* Campaign detail stats with better styling */
    .stat-item {
        background-color: rgba(0,0,0,0.02);
        border-radius: 8px;
        padding: 12px 15px;
        margin: 8px 0;
        display: flex;
        justify-content: space-between;
        transition: all 0.2s ease;
    }
    
    .stat-item:hover {
        background-color: rgba(0,0,0,0.04);
    }
    
    /* Campaign listing style improvements */
    .campaign-listing {
        margin-bottom: 5px;
        padding: 8px;
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    
    .campaign-listing:hover {
        background-color: rgba(0,0,0,0.03);
    }

    /* Uniform metric card size fix */
    div[data-testid="metric-container"] {
        height: 160px !important;
        min-height: 160px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 20px !important;
        margin: 10px 5px !important;
        background-color: #FFFFFF;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    div[data-testid="metric-container"] > div:first-child {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
    }

    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }

    div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
        font-size: 0.9rem !important;
    }

    /* Fix step cards in Get Started section */
    .step-card {
        height: 160px !important;
        min-height: 160px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 20px !important;
        margin: 10px !important;
        background-color: #f8f9fa;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }

    /* Implementation Timeline Cards for Light Mode */
    .implementation-timeline {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        gap: 15px;
    }

    .timeline-card {
        flex: 1;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        transition: transform 0.2s;
    }

    .timeline-card:hover {
        transform: translateY(-5px);
    }

    .timeline-immediate {
        background-color: #FFEBEE;
        border: 1px solid #FFCDD2;
    }

    .timeline-week {
        background-color: #FFF8E1;
        border: 1px solid #FFE0B2;
    }

    .timeline-next {
        background-color: #E8F5E9;
        border: 1px solid #C8E6C9;
    }

    .timeline-immediate h3 {
        color: #D32F2F !important;
    }

    .timeline-week h3 {
        color: #F57F17 !important;
    }

    .timeline-next h3 {
        color: #2E7D32 !important;
    }

    .timeline-card p {
        margin-top: 10px;
        font-size: 0.9rem;
    }
    """
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def apply_theme_css(theme="light"):
    """Apply theme-specific CSS (light or dark) with enhanced tab support"""
    if theme == "dark":
        css = """
        <style>
        /* Global dark theme with visibility fixes */
        html, body, .main {
            background-color: #121212 !important;
            color: #FFFFFF !important;
        }
        
        /* Dark theme uses blue color scheme */
        button, 
        .stButton>button, 
        [data-testid="stWidgetLabel"] {
            color: #FFFFFF !important;
            background-color: #0F2E4C !important;
            border: none !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.3) !important;
        }
        
        .stButton>button:hover {
            background-color: #2C5F8E !important;
            transform: translateY(-2px) !important;
        }
        
        .processing-indicator {
            background: linear-gradient(to right, #0F2E4C, #2C5F8E) !important;
        }
        
        /* Dashboard container */
        .stApp, .main, header, footer {
            background-color: #121212 !important;
        }
        
        /* All text elements */
        p, h1, h2, h3, h4, h5, h6, span, div, label {
            color: #FFFFFF !important;
        }
        
        .stMarkdown, .stMarkdown p {
            color: #FFFFFF !important;
        }
        
        /* Fix chart visibility in dark mode */
        .js-plotly-plot .plotly .main-svg, 
        .js-plotly-plot .plotly .bg {
            background-color: transparent !important;
            fill: rgba(30, 30, 30, 0.8) !important;
        }
        
        .js-plotly-plot .plotly .gridlayer path {
            stroke: rgba(255, 255, 255, 0.2) !important;
        }
        
        .js-plotly-plot .plotly .xy path {
            stroke: rgba(255, 255, 255, 0.4) !important;
        }
        
        .js-plotly-plot .plotly .xtick text, 
        .js-plotly-plot .plotly .ytick text {
            fill: #FFFFFF !important;
        }

        /* Fix chart legibility in dark mode */
        .js-plotly-plot .plotly text {
            fill: #FFFFFF !important;
        }

        .js-plotly-plot .plotly .xtick text, 
        .js-plotly-plot .plotly .ytick text, 
        .js-plotly-plot .plotly .gtitle, 
        .js-plotly-plot .plotly .annotation-text {
            fill: #FFFFFF !important;
            color: #FFFFFF !important;
        }

        .js-plotly-plot .plotly .modebar-btn path {
            fill: #FFFFFF !important;
        }

        /* Fix grid lines for better visibility */
        .js-plotly-plot .plotly .gridlayer path {
            stroke: rgba(255, 255, 255, 0.2) !important;
        }

        .js-plotly-plot .plotly .xgrid, .js-plotly-plot .plotly .ygrid {
            stroke: rgba(255, 255, 255, 0.2) !important;
        }

        /* Fix axis lines */
        .js-plotly-plot .plotly .xaxis path,
        .js-plotly-plot .plotly .yaxis path {
            stroke: rgba(255, 255, 255, 0.4) !important;
        }

        /* Ensure plot background stays dark */
        .js-plotly-plot .plotly .bg {
            fill: rgba(18, 18, 18, 0.8) !important;
        }

        /* Improve legend visibility */
        .js-plotly-plot .plotly .legend text {
            fill: #FFFFFF !important;
        }

        .js-plotly-plot .plotly .legend rect {
            stroke: rgba(255, 255, 255, 0.5) !important;
        }
        
        /* Dashboard cards */
        .dashboard-card {
            background-color: #1E1E1E !important; 
            color: #FFFFFF !important; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
            border: 1px solid #333 !important;
        }
        
        /* Metric cards */
        .metric-card {
            background-color: #1E1E1E !important; 
            color: #FFFFFF !important; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
            border: 1px solid #333 !important;
        }
        
        /* Fix recommendation cards */
        .recommendation-card {
            background-color: #2D2D2D !important; 
            color: #FFFFFF !important;
        }
        
        /* Fix risk cards */
        .risk-card {
            background-color: #3a2525 !important;
            color: #FFFFFF !important;
            border: 1px solid #5a3333 !important;
        }
        
        /* Sidebar elements */
        section[data-testid="stSidebar"] {
            background-color: #121212 !important;
        }
        
        section[data-testid="stSidebar"] > div,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] span {
            background-color: #121212 !important;
            color: #FFFFFF !important;
        }
        
        /* Fix metric cards */
        .metric-value, .metric-label {
            color: #FFFFFF !important;
        }
        
        /* Fix all input elements */
        .stTextInput>div>div,
        .stNumberInput>div>div,
        .stDateInput>div>div,
        div[data-baseweb="base-input"],
        div[data-baseweb="input"],
        input,
        .stTextInput input,
        .stNumberInput input,
        .stDateInput input {
            color: #FFFFFF !important;
            background-color: #333333 !important;
            border-color: #555555 !important;
        }
        
        /* Input elements - select boxes, file uploaders, checkboxes */
        div[data-baseweb="select"],
        div[data-baseweb="select"] div,
        .stSelectbox>div,
        .stSelectbox>div>div,
        .stFileUploader>div,
        .stFileUploader>div>div,
        .stMultiSelect>div,
        .stMultiSelect>div>div,
        .stCheckbox label,
        .stCheckbox span,
        div[data-baseweb="checkbox"] {
            color: #FFFFFF !important;
            background-color: #333333 !important;
            border-color: #555555 !important;
        }
        
        /* Fix for dropdown background */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] div,
        div[data-baseweb="menu"],
        div[data-baseweb="menu"] div,
        div[data-baseweb="list"],
        div[data-baseweb="list"] div,
        div[role="listbox"],
        div[role="listbox"] ul,
        div[role="listbox"] li,
        [data-baseweb="menu"] div,
        [data-baseweb="select-dropdown"],
        [data-baseweb="select-dropdown"] div,
        [data-baseweb="select"] ul,
        [data-baseweb="select"] li {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }
        
        /* Fix for dropdown hover state */
        div[role="option"]:hover,
        div[data-baseweb="menu"] div:hover,
        div[role="listbox"] li:hover,
        [data-baseweb="select-dropdown"] div:hover,
        [data-baseweb="select"] li:hover {
            background-color: #444444 !important;
        }
        
        /* Select dropdown elements */
        div[data-baseweb="select"] input {
            color: #FFFFFF !important;
        }
        
        /* Fix dropdown search bar */
        div[data-baseweb="select"] input,
        div[data-baseweb="select"] input::placeholder {
            color: #FFFFFF !important;
        }
        
        /* Dark mode file upload box fix */
        div[data-testid="stFileUploadDropzone"] {
            background-color: #1E1E1E !important;
            border: 1px solid #333333 !important;
            border-radius: 8px !important;
        }

        div[data-testid="stFileUploader"] {
            background-color: transparent !important;
        }

        div[data-testid="stFileUploader"] p,
        div[data-testid="stFileUploader"] span,
        div[data-testid="stFileUploader"] svg {
            color: #FFFFFF !important;
            fill: #FFFFFF !important;
        }

        div[data-testid="stFileUploader"] button {
            background-color: #0F2E4C !important;
            color: #FFFFFF !important;
        }

        /* Custom style for "Drag and drop file here" text in dark mode */
        div[data-testid="stFileUploadDropzone"] > div:first-child {
            background-color: #2D2D2D !important;
            border: none !important;
            color: #FFFFFF !important;
        }

        /* Fix file uploader - ensure it works in dark mode */
        .stFileUploader>div,
        .stFileUploader label,
        .stFileUploader span,
        .stFileUploader p,
        .stFileUploader [data-testid="stFileUploader"] {
            background-color: #333333 !important;
            color: #FFFFFF !important;
            border-color: #555555 !important;
        }
        
        .uploadedFile {
            background-color: #282828 !important;
            color: #FFFFFF !important;
        }
        
        /* Fix browse files button */
        .stFileUploader [data-testid="baseButton-secondary"] {
            background-color: #444444 !important;
            color: #FFFFFF !important;
        }
        
        /* Progress bars */
        .stProgress>div>div {
            background-color: #0F2E4C !important;
        }
        
        /* Progress container */
        .progress-container {
            background-color: #333333 !important;
        }
        
        /* Fix checkbox */
        .stCheckbox label p {
            color: #FFFFFF !important;
        }
        
        /* Fix tables */
        .dataframe {
            color: #FFFFFF !important;
        }
        
        .dataframe tbody tr {
            background-color: #1E1E1E !important;
        }
        
        .dataframe tbody tr:nth-child(even) {
            background-color: #2D2D2D !important;
        }
        
        .dataframe th {
            background-color: #333333 !important;
            color: #FFFFFF !important;
        }
        
        /* Fix success, info, error messages */
        div.stAlert {
            background-color: #1E1E1E !important;
            color: #FFFFFF !important;
        }
        
        /* Style for filter sections */
        .filter-section {
            background-color: #2A2A2A !important;
            border: 1px solid #444444 !important;
        }
        
        /* Fix for stat items */
        .stat-item {
            background-color: #2A2A2A !important;
        }
        
        .stat-item:hover {
            background-color: #333333 !important;
        }
        
        /* Landing page styles */
        .landing-container {
            background-color: #121212 !important;
        }
        
        .landing-subtitle {
            color: #BBBBBB !important;
        }
        
        /* Fix expander */
        div[data-testid="stExpander"] {
            background-color: #1E1E1E !important; 
            border: 1px solid #333 !important;
        }
        
        div[data-testid="stExpander"] > div {
            background-color: #1E1E1E !important;
        }
        
        /* Step cards on landing page */
        .step-card {
            background-color: #2A2A2A !important;
            border: 1px solid #444444 !important;
            color: #FFFFFF !important;
        }
        
        /* Campaign listing styling */
        .campaign-listing {
            background-color: #2A2A2A !important;
        }
        
        .campaign-listing:hover {
            background-color: #333333 !important;
        }
        
        /* Fix view details button for dark mode */
        .view-details-btn {
            background-color: #0F2E4C !important;
        }
        
        .view-details-btn:hover {
            background-color: #2C5F8E !important;
        }

        /* Dark theme fixes for metric containers */
        div[data-testid="metric-container"] {
            background-color: #1E1E1E !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
            border: 1px solid #333 !important;
        }

        /* Recommendations page white elements in dark mode fix */
        .dashboard-card div.row-widget.stButton > button {
            background-color: #0F2E4C !important;
            color: #FFFFFF !important;
        }

        div[data-testid="stMarkdownContainer"] div,
        .stMarkdown div {
            color: inherit !important;
            background-color: inherit !important;
        }

        /* Override any unwanted white backgrounds in dark mode */
        .dark-mode div[data-testid="stExpander"] {
            background-color: #1E1E1E !important;
            border-color: #333333 !important;
        }

        .dark-mode div[data-testid="stMarkdownContainer"] > div {
            background-color: #2D2D2D !important;
            color: #FFFFFF !important;
        }

        /* Fix recommendation timeline cards in dark mode */
        div.recommendation-card,
        div.dashboard-card div[class*="stMarkdownContainer"] > div,
        div[class*="stSelectbox"] > div,
        div.stSelectbox div[role="listbox"],
        div[data-baseweb="select"] ul,
        div[data-baseweb="select-dropdown"] {
            background-color: #2D2D2D !important;
            color: #FFFFFF !important;
        }

        /* Fix implementation timeline cards in recommendations tab */
        div.dashboard-card div.row-widget div[class*="stMarkdownContainer"] > div {
            background-color: #2D2D2D !important;
            border: 1px solid #444444 !important;
        }

        /* Adjust the timeline card colors for dark mode */
        div.dashboard-card div.row-widget div[class*="stMarkdownContainer"] > div:nth-child(1) {
            background-color: #3A2525 !important; /* Dark red */
        }

        div.dashboard-card div.row-widget div[class*="stMarkdownContainer"] > div:nth-child(2) {
            background-color: #33332A !important; /* Dark yellow */
        }

        div.dashboard-card div.row-widget div[class*="stMarkdownContainer"] > div:nth-child(3) {
            background-color: #1E3329 !important; /* Dark green */
        }

        /* Improve timeline headers in dark mode */
        div.dashboard-card div.row-widget div[class*="stMarkdownContainer"] h4 {
            color: #EEEEEE !important;
        }
        
        /* Fix step cards in dark mode */
        .dark-mode .step-card {
            background-color: #2D2D2D !important;
            border-color: #444444 !important;
        }

        /* Dark Mode Timeline Cards */
        .dark-mode .timeline-immediate {
            background-color: #3A2525 !important;
            border: 1px solid #4D2F2F !important;
        }

        .dark-mode .timeline-week {
            background-color: #33332A !important;
            border: 1px solid #45452F !important;
        }

        .dark-mode .timeline-next {
            background-color: #1E3329 !important;
            border: 1px solid #2A4635 !important;
        }

        .dark-mode .timeline-immediate h3 {
            color: #FF8A80 !important;
        }

        .dark-mode .timeline-week h3 {
            color: #FFD180 !important;
        }

        .dark-mode .timeline-next h3 {
            color: #B9F6CA !important;
        }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    else:
        # Light theme CSS - improved for better contrast
        css = """
        <style>
        /* Global light theme */
        body, .main {
            background-color: #FFFFFF !important;
            color: #111111 !important;
        }
        
        /* Fix all text colors */
        p, h1, h2, h3, h4, h5, h6, span, div, label {
            color: #111111 !important;
        }
        
        /* Dashboard cards */
        .dashboard-card {
            background-color: #FFFFFF !important; 
            color: #111111 !important; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
            border: none !important;
        }
        
        /* Metric cards */
        .metric-card {
            background-color: #FFFFFF !important; 
            color: #111111 !important; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
            border: none !important;
        }
        
        /* Fix metric cards */
        .metric-value, .metric-label {
            color: #111111 !important;
        }
        
        /* Style for filter sections */
        .filter-section {
            background-color: #F8F9FA !important;
            border: 1px solid #E9ECEF !important;
        }
        
        /* Fix dropdown hover state */
        div[data-baseweb="select"] div[role="option"]:hover,
        div[data-baseweb="menu"] div:hover,
        div[role="listbox"] li:hover {
            background-color: #f2f2f2 !important;
        }
        
        /* Button hover effects */
        .stButton>button:hover {
            background-color: #E65056 !important;
            transform: translateY(-2px) !important;
        }
        
        /* Step cards on landing page */
        .step-card {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
        }
        
        /* Enhanced processing indicator */
        .processing-indicator {
            background: linear-gradient(to right, #FF5A5F, #FF8A8F) !important;
            color: white !important;
        }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)

def create_config_toml(theme="light"):
    """Create or update .streamlit/config.toml for theme settings"""
    config_dir = ".streamlit"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    config_path = os.path.join(config_dir, "config.toml")
    
    if theme == "dark":
        config_content = """[theme]
base="dark"
primaryColor="#0F2E4C"
backgroundColor="#121212"
secondaryBackgroundColor="#1E1E1E"
textColor="#FFFFFF"
font="sans serif"
"""
    else:
        config_content = """[theme]
base="light"
primaryColor="#FF5A5F"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F8F9FA"
textColor="#111111"
font="sans serif"
"""
    
    with open(config_path, "w") as f:
        f.write(config_content)

def create_metric_card(title, value, delta=None, delta_good_direction="up", help_text=None):
    """Create a styled metric card with optional tooltip and delta indicator"""
    # Ensure value is properly formatted and not NaN
    if pd.isna(value) or value == "nan":
        display_value = "$0.00" if "spend" in title.lower() or "$" in str(value) else "0"
    else:
        display_value = value
    
    delta_html = ""
    if delta is not None:
        if pd.isna(delta):
            delta = 0
        
        if delta_good_direction == "up":
            delta_class = "stat-change-up" if delta < 0 else "stat-change-down"
            delta_icon = "↓" if delta < 0 else "↑"
        else:
            delta_class = "stat-change-down" if delta < 0 else "stat-change-up"
            delta_icon = "↓" if delta < 0 else "↑"
        
        delta_html = f'<div class="{delta_class}">{delta_icon} {abs(delta):.2f}%</div>'
    
    tooltip_html = ""
    if help_text:
        tooltip_html = f"""
        <div class="tooltip">ⓘ
            <span class="tooltiptext">{help_text}</span>
        </div>
        """
    
    # Get theme from session state
    theme = st.session_state.get('theme', 'light')
    
    # Determine text color and background color based on theme
    text_color = '#ffffff' if theme == 'dark' else '#111111'
    bg_color = '#1E1E1E' if theme == 'dark' else '#FFFFFF'
    
    html = f"""
    <div class="metric-card" style="background-color: {bg_color}; color: {text_color};">
        <div class="metric-label" style="color: {text_color}">{title} {tooltip_html}</div>
        <div class="metric-value" style="color: {text_color}">{display_value}</div>
        {delta_html}
    </div>
    """
    
    return html