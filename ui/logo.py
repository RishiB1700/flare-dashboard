"""
FLARE Logo Component - Streamlit-compatible image loading

This module provides functions to render the FLARE logo from a local image file.
"""
import streamlit as st
import base64
import os

def get_base64_encoded_image(image_path):
    """Get base64 encoded image data for embedding in HTML"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

def render_logo(size="medium", type="horizontal"):
    """
    Renders the FLARE logo using base64 encoded image
    
    Parameters:
    - size: "small", "medium", or "large"
    - type: "horizontal" or "vertical"
    
    Returns:
    - HTML for the logo display
    """
    # Size mapping
    size_map = {
        "small": {"logo": 30, "text": 18},
        "medium": {"logo": 40, "text": 24},
        "large": {"logo": 80, "text": 42}
    }
    
    logo_size = size_map[size]["logo"]
    text_size = size_map[size]["text"]
    
    # Get text color based on theme
    text_color = "#ffffff" if st.session_state.get('theme', 'light') == 'dark' else "#212121"
    
    # Try multiple logo paths (for flexibility)
    logo_paths = [
        "/Users/hrishibhanushali/Documents/Flare/assets/Flare logo.png",
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "Flare logo.png"),
        "assets/Flare logo.png"
    ]
    
    # Try to get the base64 encoded image
    logo_base64 = None
    for path in logo_paths:
        logo_base64 = get_base64_encoded_image(path)
        if logo_base64:
            break
    
    # System font stack for consistent appearance
    font_stack = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
    
    # If logo was loaded successfully, use it
    if logo_base64:
        # Horizontal layout (logo next to text)
        if type == "horizontal":
            return f"""
            <div style="display: flex; align-items: center; gap: 8px;">
                <img src="data:image/png;base64,{logo_base64}" width="{logo_size}" height="{logo_size}" alt="FLARE Logo" style="object-fit: contain;" />
                <span style="font-family: {font_stack}; font-weight: 700; font-size: {text_size}px; color: {text_color}; letter-spacing: 0.5px;">FLARE</span>
            </div>
            """
        
        # Vertical layout (logo above text)
        else:
            return f"""
            <div style="display: flex; flex-direction: column; align-items: center; gap: 10px; margin-bottom: 20px;">
                <img src="data:image/png;base64,{logo_base64}" width="{logo_size}" height="{logo_size}" alt="FLARE Logo" style="object-fit: contain;" />
                <span style="font-family: {font_stack}; font-weight: 700; font-size: {text_size}px; color: {text_color}; letter-spacing: 1px;">FLARE</span>
            </div>
            """
    
    # Fallback if no logo could be loaded (using SVG fire instead of emoji)
    fire_svg = f"""<svg width="{logo_size}" height="{logo_size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 22C16.4183 22 20 18.4183 20 14C20 9 16.5 4.5 12 2C12 6.5 8 9 8 14C8 18.4183 11.5817 22 12 22Z" fill="{text_color}" stroke="{text_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>"""
    
    # Horizontal layout (SVG next to text)
    if type == "horizontal":
        return f"""
        <div style="display: flex; align-items: center; gap: 8px;">
            {fire_svg}
            <span style="font-family: {font_stack}; font-weight: 700; font-size: {text_size}px; color: {text_color}; letter-spacing: 0.5px;">FLARE</span>
        </div>
        """
    
    # Vertical layout (SVG above text)
    else:
        return f"""
        <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 20px;">
            {fire_svg}
            <span style="font-family: {font_stack}; font-weight: 700; font-size: {text_size}px; color: {text_color}; letter-spacing: 1px;">FLARE</span>
        </div>
        """