"""
Data Generator Module for FLARE

This module provides functions to generate sample campaign data
and load data from uploaded files.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import io

def generate_sample_campaign_data(campaign_id, days=30, start_date=None, fatigue_start=None):
    """Generate sample campaign data with realistic fatigue patterns"""
    if start_date is None:
        start_date = datetime.now() - timedelta(days=days)
    
    # Basic campaign parameters with more variation based on campaign type
    if "Healthy" in campaign_id:
        base_impressions = np.random.randint(15000, 25000)
        base_ctr = np.random.uniform(0.04, 0.06)
        base_conversion_rate = np.random.uniform(0.08, 0.12)
        base_cpc = np.random.uniform(0.7, 1.5)
        base_conversion_value = np.random.uniform(50, 100)
    elif "Friction" in campaign_id:
        base_impressions = np.random.randint(10000, 20000)
        base_ctr = np.random.uniform(0.03, 0.05)
        base_conversion_rate = np.random.uniform(0.05, 0.09)
        base_cpc = np.random.uniform(0.8, 1.7)
        base_conversion_value = np.random.uniform(40, 80)
    elif "Fatigue" in campaign_id:
        base_impressions = np.random.randint(8000, 15000)
        base_ctr = np.random.uniform(0.02, 0.04)
        base_conversion_rate = np.random.uniform(0.03, 0.07)
        base_cpc = np.random.uniform(1.0, 2.0)
        base_conversion_value = np.random.uniform(35, 70)
    elif "Failure" in campaign_id:
        base_impressions = np.random.randint(5000, 12000)
        base_ctr = np.random.uniform(0.01, 0.03)
        base_conversion_rate = np.random.uniform(0.01, 0.05)
        base_cpc = np.random.uniform(1.2, 2.5)
        base_conversion_value = np.random.uniform(25, 60)
    else:  # New campaign
        base_impressions = np.random.randint(3000, 8000)
        base_ctr = np.random.uniform(0.04, 0.08)
        base_conversion_rate = np.random.uniform(0.08, 0.15)
        base_cpc = np.random.uniform(0.5, 1.2)
        base_conversion_value = np.random.uniform(40, 90)
    
    data = []
    
    # Create daily performance data
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        
        # Modifiers based on day of week (weekends might have different patterns)
        day_of_week = current_date.weekday()
        weekday_modifier = 1.0 if day_of_week < 5 else 0.8
        
        # Calculate fatigue effect based on campaign type
        if fatigue_start is not None and day >= fatigue_start:
            days_in_fatigue = day - fatigue_start
            
            if "Healthy" in campaign_id:
                # Minimal fatigue for healthy campaigns
                impression_modifier = 1.0 + 0.02 * days_in_fatigue
                ctr_modifier = 1.0 - 0.01 * days_in_fatigue
                cpc_modifier = 1.0 + 0.01 * days_in_fatigue
                conversion_modifier = 1.0 - 0.005 * days_in_fatigue
            elif "Friction" in campaign_id:
                # Early signs of fatigue
                impression_modifier = 1.0 + 0.04 * days_in_fatigue
                ctr_modifier = 1.0 - 0.02 * days_in_fatigue
                cpc_modifier = 1.0 + 0.02 * days_in_fatigue
                conversion_modifier = 1.0 - 0.015 * days_in_fatigue
            elif "Fatigue" in campaign_id:
                # Clear fatigue signs
                impression_modifier = 1.0 + 0.06 * days_in_fatigue
                ctr_modifier = 1.0 - 0.04 * days_in_fatigue
                cpc_modifier = 1.0 + 0.04 * days_in_fatigue
                conversion_modifier = 1.0 - 0.03 * days_in_fatigue
            elif "Failure" in campaign_id:
                # Severe fatigue signs
                impression_modifier = 1.0 + 0.08 * days_in_fatigue
                ctr_modifier = 1.0 - 0.06 * days_in_fatigue
                cpc_modifier = 1.0 + 0.06 * days_in_fatigue
                conversion_modifier = 1.0 - 0.05 * days_in_fatigue
            else:
                # Default moderate fatigue
                impression_modifier = 1.0 + 0.05 * days_in_fatigue
                ctr_modifier = 1.0 - 0.03 * days_in_fatigue
                cpc_modifier = 1.0 + 0.03 * days_in_fatigue
                conversion_modifier = 1.0 - 0.025 * days_in_fatigue
        else:
            # Learning/optimization phase
            impression_modifier = 1.0 + 0.01 * day
            ctr_modifier = 1.0 + 0.01 * day  # CTR improves slightly in early days
            cpc_modifier = 1.0
            conversion_modifier = 1.0 + 0.01 * day  # Conversion rate improves slightly
        
        # Apply randomness
        random_factor = np.random.normal(1.0, 0.1)
        
        # Calculate metrics
        impressions = int(base_impressions * impression_modifier * weekday_modifier * random_factor)
        ctr = base_ctr * ctr_modifier * random_factor
        clicks = int(impressions * ctr)
        cpc = base_cpc * cpc_modifier * random_factor
        spend = clicks * cpc
        conversion_rate = base_conversion_rate * conversion_modifier * random_factor
        conversions = int(clicks * conversion_rate)
        revenue = conversions * base_conversion_value * random_factor
        
        # Ensure reasonable values
        impressions = max(100, impressions)
        clicks = max(1, clicks)
        conversions = max(0, conversions)
        spend = max(1.0, spend)
        revenue = max(0.0, revenue)
        
        data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'campaign_id': campaign_id,
            'impressions': impressions,
            'clicks': clicks,
            'ctr': clicks / impressions,
            'spend': spend,
            'cpc': spend / clicks,
            'conversions': conversions,
            'cpa': spend / conversions if conversions > 0 else None,
            'revenue': revenue,
            'roi': revenue / spend if spend > 0 else None
        })
    
    return pd.DataFrame(data)

def generate_sample_dataset(num_campaigns=10):
    """Generate a sample dataset with multiple campaigns in various fatigue stages"""
    all_data = []
    
    # Campaign patterns representing different fatigue stages
    patterns = [
        {'fatigue_start': 25, 'days': 30, 'name': 'Healthy_Campaign'},     # Healthy campaign
        {'fatigue_start': 15, 'days': 30, 'name': 'Friction_Campaign'},    # Early friction signs
        {'fatigue_start': 10, 'days': 30, 'name': 'Fatigue_Campaign'},     # Clear fatigue
        {'fatigue_start': 5, 'days': 30, 'name': 'Failure_Campaign'},      # Complete failure
        {'fatigue_start': None, 'days': 30, 'name': 'New_Campaign'}        # No fatigue (new campaign)
    ]
    
    for i in range(num_campaigns):
        pattern = patterns[i % len(patterns)]
        campaign_id = f"{pattern['name']}_{i+1}"
        campaign_data = generate_sample_campaign_data(
            campaign_id,
            days=pattern['days'],
            fatigue_start=pattern['fatigue_start']
        )
        all_data.append(campaign_data)
    
    # Combine all campaign data
    combined_data = pd.concat(all_data, ignore_index=True)
    return combined_data

def load_sample_data(uploaded_file=None):
    """
    Load campaign data either from an uploaded file or generate sample data
    Args:
        uploaded_file: Optional file uploaded by the user
    """
    if uploaded_file is not None:
        try:
            # Read the uploaded CSV file
            df = pd.read_csv(uploaded_file)
            
            # Validate required columns
            required_columns = ['date', 'campaign_id', 'impressions', 'clicks', 'spend']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Uploaded file is missing required columns: {', '.join(missing_columns)}")
                return None
                
            # Convert date column to datetime
            df['date'] = pd.to_datetime(df['date'])
            
            # Calculate derived metrics if not present
            if 'ctr' not in df.columns:
                df['ctr'] = df['clicks'] / df['impressions']
                
            if 'cpc' not in df.columns:
                df['cpc'] = df['spend'] / df['clicks'].replace(0, np.nan)
                
            if 'conversions' in df.columns and 'cpa' not in df.columns:
                df['cpa'] = df['spend'] / df['conversions'].replace(0, np.nan)
                
            if 'revenue' in df.columns and 'roi' not in df.columns:
                df['roi'] = df['revenue'] / df['spend']
                
            return df
            
        except Exception as e:
            st.error(f"Error loading uploaded file: {e}")
            return None
    else:
        # Generate sample data
        return generate_sample_dataset(num_campaigns=10)

def validate_data(df):
    """Check if the data has all required columns and handle incomplete datasets"""
    if df is None:
        return False, "No data provided."
        
    # Check required columns
    required_columns = ['date', 'campaign_id', 'impressions', 'clicks', 'spend']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    # Check for conversion data
    is_partial = 'conversions' not in df.columns or df['conversions'].isnull().all()
    
    partial_message = None
    if is_partial:
        partial_message = "Partial Analysis Mode: CTR-based fatigue detection enabled (conversion data unavailable)"
    
    # Check for revenue data
    if 'revenue' not in df.columns or df['revenue'].isnull().all():
        if partial_message:
            partial_message += ". ROI analysis disabled (revenue data unavailable)."
        else:
            is_partial = True
            partial_message = "Partial Analysis Mode: ROI analysis disabled (revenue data unavailable)"
    
    return True, partial_message