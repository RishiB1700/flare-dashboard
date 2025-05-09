# FLARE: Fatigue Learning and Adaptive Response Engine

## Overview

FLARE (Fatigue Learning and Adaptive Response Engine) is a prototype framework designed to help advertisers detect and manage digital ad fatigue. This prototype implements the core concepts presented in the Capstone Project "Decoding Ad Fatigue in Digital Advertising: A Strategic Framework for Smarter and Ethical Campaign Delivery."

The dashboard analyzes campaign data to identify three stages of ad fatigue:
1. **Friction**: Early signs of wear, minor CTR drop
2. **Fatigue**: Engagement stagnation, rising CPA
3. **Failure**: Sharp ROI decline, continued delivery with little return

## Project Structure

```
flare/
├── app.py                   # Main dashboard launcher
│
├── core/
│   └── flare_core.py        # Core FLARE processing engine
│
├── data/
│   └── data_generator.py    # Mock data generation module
│
├── tabs/
│   ├── overview.py          # Overview tab UI components
│   ├── campaign_details.py  # Campaign details tab UI components
│   ├── recommendations.py   # Recommendations tab UI components
│   ├── spend_analysis.py    # Spend analysis tab UI components
│   └── ai_forecasting.py    # AI forecasting tab UI components
│
├── ui/
│   ├── theme.py             # Theme and CSS handling
│   └── viz_utils.py         # Visualization utilities
│
├── assets/
│   └── flare_dashboard.css  # CSS styles for dashboard
│
├── temp_campaign_data.csv   # Temporary data storage
│
├── requirements.txt         # Python dependencies
│
└── README.md                # This file
```

## Features

- **Three-Stage Fatigue Detection**: Identifies campaigns in Friction, Fatigue, or Failure stages
- **Fatigue Risk Index (FRI)**: Scores campaigns from 0-100 based on fatigue severity
- **Wasted Spend Estimation**: Calculates financial impact of ad fatigue
- **Context-Aware Recommendations**: Provides tailored actions based on campaign age, performance trends, and fatigue severity
- **Interactive Visualizations**: Detailed Plotly charts for performance analysis
- **Optimization Impact**: Quantifies potential savings from implementing recommendations
- **Dark/Light Mode**: Fully themeable interface with persistent state

## Setup Instructions

### Prerequisites

- Python 3.7 or newer
- Required Python packages (install using `pip install -r requirements.txt`):
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - streamlit
  - plotly

### Installation

1. Clone this repository or download the files to your local machine
2. Create a virtual environment (recommended):
   ```
   python -m venv flare-env
   source flare-env/bin/activate  # On Windows: flare-env\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Dashboard

To run the dashboard:

```
streamlit run app.py
```

This will start a local web server and open the dashboard in your default browser. From there, you can:
- Use the sample data or upload your own campaign data (CSV format)
- View an overview of campaign health with interactive charts
- Analyze individual campaign performance and fatigue metrics
- See detailed, context-aware recommendations with explanations
- Review wasted spend estimates and optimization opportunities
- Explore potential savings through fatigue management

## Using Your Own Data

To analyze your own campaign data, prepare a CSV file with the following columns:
- `date`: Date of the campaign metrics (YYYY-MM-DD format)
- `campaign_id`: Unique identifier for each campaign
- `impressions`: Number of ad impressions
- `clicks`: Number of clicks
- `spend`: Amount spent on the campaign
- `conversions`: Number of conversions (optional)

Optional additional columns:
- `ctr`: Click-through rate (calculated if not provided)
- `cpc`: Cost per click (calculated if not provided)
- `cpa`: Cost per acquisition (calculated if not provided)
- `revenue`: Revenue generated (if available)
- `roi`: Return on investment (calculated if not provided)

## Key Components

### Core Module

The `flare_core.py` module implements the main fatigue detection algorithm, including:
- FRI (Fatigue Risk Index) calculation based on performance metrics
- Three-stage classification (Friction, Fatigue, Failure)
- Dynamic waste calculation
- Recommendation generation

### Dashboard Tabs

- **Overview**: Shows summary metrics, campaign health distribution and high-risk campaigns
- **Campaign Details**: Detailed performance metrics for individual campaigns
- **Recommendations**: Actionable recommendations with prioritized timeline
- **Spend Analysis**: Wasted spend analysis and optimization potential
- **AI Forecasting**: Predictive modeling of future fatigue patterns (preview)

### Theme Support

The dashboard includes a fully responsive dark/light mode theme with persistent state:
- Dark theme optimized for evening use
- Light theme for better daytime visibility
- Responsive design that adapts to different screen sizes

## Troubleshooting

If you encounter any issues:

1. **ValueError with filter or campaign selection**: This is usually caused by array comparison issues. The updated modular code should fix this problem.

2. **Theme switching not working**: If the theme toggle doesn't properly update all elements, try refreshing the page after switching.

3. **Missing data fields**: If your CSV is missing optional fields, the dashboard will enter "Partial Analysis Mode" and work with available metrics.

4. **Performance issues**: For large datasets, try using the filtering options in the Campaign Details tab to focus on specific campaigns.

## Future Development

Future enhancements could include:

1. **API Integration**: Connect directly to ad platforms like Google Ads, Meta, etc.
2. **Machine Learning Enhancements**: Train predictive models to forecast fatigue before it occurs
3. **Format-Specific Analysis**: Fine-tune detection for different creative formats
4. **Advanced Visualization**: Add more interactive visualizations and trend analysis
5. **Alert System**: Implement notifications when campaigns reach critical fatigue levels
6. **Optimization Recommendations**: Provide more detailed, data-driven action plans

## Credits

Based on the Capstone Project by Rishi Bhanushali.

## License

This prototype is provided for demonstration purposes only. All rights reserved.

---

*FLARE: Decoding Ad Fatigue in Digital Advertising*  
*A Strategic Framework for Smarter and Ethical Campaign Delivery*