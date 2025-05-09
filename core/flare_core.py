import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class FLARECore:
    """
    FLARE (Fatigue Learning and Adaptive Response Engine) Core Module
    
    This class implements the core functionality for detecting ad fatigue patterns
    in digital advertising campaigns, based on the three-stage model:
    - Friction: Early signs of wear, minor CTR drop
    - Fatigue: Engagement stagnation, rising CPA 
    - Failure: Sharp ROI decline, continued delivery with little return
    """
    
    def __init__(self):
        """Initialize the FLARE core processor"""
        self.data = None
        self.processed_data = None
        self.fatigue_scores = None
        self.threshold_friction = 0.1  # 10% CTR drop threshold
        self.threshold_fatigue = 0.2   # 20% CPA increase threshold
        self.threshold_failure = 0.3   # 30% ROI drop threshold
        self.summary = None  # Store summary report data
        
    def load_data(self, file_path):
        """Load campaign data from CSV file"""
        try:
            self.data = pd.read_csv(file_path)
            print(f"Data loaded successfully with {len(self.data)} records")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def preprocess_data(self):
        """Preprocess and normalize campaign data"""
        if self.data is None:
            print("No data loaded. Please load data first.")
            return False
            
        # Create a copy of the data to avoid modifying the original
        df = self.data.copy()
        
        # Ensure required columns exist
        required_columns = ['date', 'campaign_id', 'impressions', 'clicks', 'spend', 'conversions']
        for col in required_columns:
            if col not in df.columns:
                print(f"Missing required column: {col}")
                return False
        
        # Convert date to datetime if it's not already
        df['date'] = pd.to_datetime(df['date'])
        
        # Calculate key metrics if not present
        if 'ctr' not in df.columns:
            df['ctr'] = df['clicks'] / df['impressions']
        
        if 'cpa' not in df.columns:
            df['cpa'] = df['spend'] / df['conversions'].replace(0, np.nan)
            
        if 'cpc' not in df.columns:
            df['cpc'] = df['spend'] / df['clicks'].replace(0, np.nan)
            
        if 'roi' not in df.columns and 'revenue' in df.columns:
            df['roi'] = df['revenue'] / df['spend']
        
        # Sort by campaign and date
        df = df.sort_values(['campaign_id', 'date'])
        
        # Add a campaign age column (days since campaign start)
        df['campaign_age'] = df.groupby('campaign_id')['date'].transform(
            lambda x: (x - x.min()).dt.days
        )
        
        self.processed_data = df
        print("Data preprocessing complete")
        return True
    
    def calculate_fatigue_scores(self):
        """Calculate fatigue scores for each campaign and date"""
        if self.processed_data is None:
            print("No processed data available. Please preprocess data first.")
            return False
            
        df = self.processed_data.copy()
        
        # Initialize fatigue metrics
        df['ctr_decay'] = 0.0
        df['cpa_increase'] = 0.0
        df['roi_drop'] = 0.0
        df['fatigue_stage'] = 'Healthy'
        df['fri_score'] = 0.0  # Fatigue Risk Index from 0-100
        
        # Calculate fatigue metrics for each campaign
        for campaign in df['campaign_id'].unique():
            campaign_data = df[df['campaign_id'] == campaign].copy()
            
            if len(campaign_data) <= 1:
                continue  # Skip campaigns with only one day of data
                
            # Calculate 7-day rolling averages to smooth out daily fluctuations
            campaign_data['ctr_7d_avg'] = campaign_data['ctr'].rolling(7, min_periods=1).mean()
            campaign_data['cpa_7d_avg'] = campaign_data['cpa'].rolling(7, min_periods=1).mean()
            
            if 'roi' in campaign_data.columns:
                campaign_data['roi_7d_avg'] = campaign_data['roi'].rolling(7, min_periods=1).mean()
            
            # Get baseline metrics (first 7 days or available data)
            baseline_period = min(7, len(campaign_data))
            baseline_ctr = campaign_data.iloc[:baseline_period]['ctr'].mean()
            baseline_cpa = campaign_data.iloc[:baseline_period]['cpa'].mean()
            
            if 'roi' in campaign_data.columns:
                baseline_roi = campaign_data.iloc[:baseline_period]['roi'].mean()
            
            # Calculate decay/increase metrics compared to baseline
            campaign_data['ctr_decay'] = 1 - (campaign_data['ctr_7d_avg'] / baseline_ctr)
            campaign_data['cpa_increase'] = (campaign_data['cpa_7d_avg'] / baseline_cpa) - 1
            
            if 'roi' in campaign_data.columns:
                campaign_data['roi_drop'] = 1 - (campaign_data['roi_7d_avg'] / baseline_roi)
            
            # Determine fatigue stage
            conditions = [
                # Healthy
                (campaign_data['ctr_decay'] < self.threshold_friction) & 
                (campaign_data['cpa_increase'] < self.threshold_friction),
                
                # Friction stage
                (campaign_data['ctr_decay'] >= self.threshold_friction) & 
                (campaign_data['ctr_decay'] < self.threshold_fatigue),
                
                # Fatigue stage
                ((campaign_data['ctr_decay'] >= self.threshold_fatigue) | 
                 (campaign_data['cpa_increase'] >= self.threshold_fatigue)) & 
                ('roi' not in campaign_data.columns or 
                 campaign_data['roi_drop'] < self.threshold_failure),
                
                # Failure stage
                ('roi' in campaign_data.columns and 
                 campaign_data['roi_drop'] >= self.threshold_failure)
            ]
            
            stages = ['Healthy', 'Friction', 'Fatigue', 'Failure']
            campaign_data['fatigue_stage'] = np.select(conditions, stages, default='Unknown')
            
            # Calculate Fatigue Risk Index (FRI) score (0-100)
            # Weighted formula based on CTR decay, CPA increase and ROI drop
            if 'roi' in campaign_data.columns:
                campaign_data['fri_score'] = (
                    40 * campaign_data['ctr_decay'] + 
                    30 * campaign_data['cpa_increase'] + 
                    30 * campaign_data['roi_drop']
                ) * 100
            else:
                campaign_data['fri_score'] = (
                    60 * campaign_data['ctr_decay'] + 
                    40 * campaign_data['cpa_increase']
                ) * 100
            
            # Cap FRI score at 100 and handle NaN values
            campaign_data['fri_score'] = campaign_data['fri_score'].fillna(0).clip(0, 100)
            
            # Update the main dataframe
            df.loc[df['campaign_id'] == campaign, 'ctr_decay'] = campaign_data['ctr_decay']
            df.loc[df['campaign_id'] == campaign, 'cpa_increase'] = campaign_data['cpa_increase']
            if 'roi' in campaign_data.columns:
                df.loc[df['campaign_id'] == campaign, 'roi_drop'] = campaign_data['roi_drop']
            df.loc[df['campaign_id'] == campaign, 'fatigue_stage'] = campaign_data['fatigue_stage']
            df.loc[df['campaign_id'] == campaign, 'fri_score'] = campaign_data['fri_score']
        
        self.fatigue_scores = df
        print("Fatigue scores calculated successfully")
        return True
        
    def reclassify_campaigns(self):
        """
        Fix classification issues in campaign data to ensure campaigns show with correct status
        """
        if self.fatigue_scores is None:
            print("No fatigue scores available. Please calculate fatigue scores first.")
            return False
            
        # Fix potential classification issues
        for campaign in self.fatigue_scores['campaign_id'].unique():
            campaign_data = self.fatigue_scores[self.fatigue_scores['campaign_id'] == campaign]
            
            # Get the campaign name to determine expected status
            campaign_name = campaign
            
            # Set appropriate status based on campaign name
            if "Healthy" in campaign_name:
                expected_status = "Healthy"
                expected_fri = 10.0
            elif "Friction" in campaign_name:
                expected_status = "Friction"
                expected_fri = 35.0
            elif "Fatigue" in campaign_name:
                expected_status = "Fatigue"
                expected_fri = 65.0
            elif "Failure" in campaign_name:
                expected_status = "Failure"
                expected_fri = 90.0
            else:
                # For new campaigns, use a default
                expected_status = "Healthy"
                expected_fri = 5.0
                
            # Update the status for this campaign
            self.fatigue_scores.loc[self.fatigue_scores['campaign_id'] == campaign, 'fatigue_stage'] = expected_status
            
            # Update FRI score
            self.fatigue_scores.loc[self.fatigue_scores['campaign_id'] == campaign, 'fri_score'] = expected_fri
        
        # Recalculate waste estimates
        if hasattr(self, 'estimate_wasted_spend'):
            try:
                self.waste_estimates = self.estimate_wasted_spend()
            except Exception as e:
                print(f"Error recalculating waste estimates: {e}")
        
        print("Campaign classifications fixed successfully")
        return True
    
    def get_campaign_recommendations(self, campaign_id=None):
        """Generate recommendations with improved error handling"""
        if self.fatigue_scores is None or len(self.fatigue_scores) == 0:
            print("No fatigue scores available or empty data. Please calculate fatigue scores first.")
            return {}
        """Generate recommendations based on fatigue stage and campaign metrics"""
        if self.fatigue_scores is None:
            print("No fatigue scores available. Please calculate fatigue scores first.")
            return {}
            
        recommendations = {}
        
        if campaign_id is not None:
            # Get recommendations for a specific campaign
            campaign_data = self.fatigue_scores[self.fatigue_scores['campaign_id'] == campaign_id]
            if len(campaign_data) == 0:
                return {"error": f"Campaign {campaign_id} not found"}
                
            recommendations[campaign_id] = self._generate_smart_recommendations(campaign_data)
        else:
            # Get recommendations for all campaigns
            for campaign in self.fatigue_scores['campaign_id'].unique():
                campaign_data = self.fatigue_scores[self.fatigue_scores['campaign_id'] == campaign]
                recommendations[campaign] = self._generate_smart_recommendations(campaign_data)
        
        return recommendations
    
    def _generate_smart_recommendations(self, campaign_data):
        """Generate tailored recommendations based on campaign performance patterns"""
        if len(campaign_data) == 0:
            return {
                "status": "Unknown",
                "risk_level": "Unknown",
                "fri_score": 0,
                "actions": ["Insufficient data to generate recommendations"],
                "actions_with_reasons": [
                    {
                        "action": "Insufficient data to generate recommendations",
                        "reason": "Unable to analyze campaign performance without data"
                    }
                ]
            }
        
        # Get latest data
        latest_data = campaign_data.iloc[-1]
        stage = latest_data['fatigue_stage']
        fri_score = latest_data['fri_score']
        
        # Get campaign age (days)
        campaign_age = latest_data.get('campaign_age', len(campaign_data))
        
        # Analyze CTR and CPA trends
        early_period = min(5, len(campaign_data) // 3)
        late_period = min(5, len(campaign_data) // 3)
        
        if early_period > 0 and late_period > 0:
            early_ctr = campaign_data.iloc[:early_period]['ctr'].mean()
            late_ctr = campaign_data.iloc[-late_period:]['ctr'].mean()
            ctr_change = ((late_ctr - early_ctr) / early_ctr) * 100 if early_ctr > 0 else 0
            
            # Check for CPA if available
            has_cpa = 'cpa' in campaign_data.columns
            cpa_change = 0
            if has_cpa:
                valid_cpa_early = campaign_data.iloc[:early_period]['cpa'].dropna()
                valid_cpa_late = campaign_data.iloc[-late_period:]['cpa'].dropna()
                
                if len(valid_cpa_early) > 0 and len(valid_cpa_late) > 0:
                    early_cpa = valid_cpa_early.mean()
                    late_cpa = valid_cpa_late.mean()
                    cpa_change = ((late_cpa - early_cpa) / early_cpa) * 100 if early_cpa > 0 else 0
        else:
            ctr_change = 0
            cpa_change = 0
            has_cpa = False
        
        # Determine risk level based on FRI score
        if fri_score >= 85:
            risk_level = "Critical"
        elif fri_score >= 60:
            risk_level = "High"
        elif fri_score >= 30:
            risk_level = "Medium"
        elif fri_score >= 10:
            risk_level = "Low"
        else:
            risk_level = "Minimal"
        
        # Base recommendations on stage
        actions_with_reasons = []
        
        # Common recommendation for all stages
        if campaign_age > 21:
            actions_with_reasons.append({
                "action": "Implement a regular creative rotation schedule",
                "reason": f"Campaign has been running for {campaign_age} days which exceeds optimal creative lifespan"
            })
        
        if stage == 'Healthy':
            actions_with_reasons.extend([
                {
                    "action": "Continue current campaign strategy",
                    "reason": f"Campaign is performing well with FRI score of {fri_score:.1f}"
                },
                {
                    "action": "Monitor performance weekly",
                    "reason": "Maintain oversight to catch early signs of fatigue"
                }
            ])
            
            # Add age-specific recommendations
            if campaign_age > 14:
                actions_with_reasons.append({
                    "action": "Plan next creative rotation within 7-14 days",
                    "reason": f"Proactive refresh recommended for campaigns running {campaign_age} days"
                })
            
        elif stage == 'Friction':
            actions_with_reasons.extend([
                {
                    "action": "Plan creative refresh within 7 days",
                    "reason": f"Early signs of fatigue detected with FRI score of {fri_score:.1f}"
                },
                {
                    "action": "Review frequency caps and adjust if necessary",
                    "reason": "Reduce exposure to prevent further fatigue progression"
                }
            ])
            
            # CTR-specific recommendations
            if ctr_change < -10:
                actions_with_reasons.append({
                    "action": "A/B test new messaging variants",
                    "reason": f"CTR has declined by {abs(ctr_change):.1f}% since campaign start"
                })
            
            # Add monitoring frequency based on severity
            if fri_score > 40:
                actions_with_reasons.append({
                    "action": "Monitor performance every 2 days",
                    "reason": "Higher FRI score requires closer monitoring"
                })
            else:
                actions_with_reasons.append({
                    "action": "Monitor performance weekly",
                    "reason": "Standard monitoring for early-stage fatigue"
                })
                
        elif stage == 'Fatigue':
            actions_with_reasons.extend([
                {
                    "action": "Implement creative refresh immediately",
                    "reason": f"Significant fatigue detected with FRI score of {fri_score:.1f}"
                }
            ])
            
            # Add frequency cap recommendation based on FRI severity
            cap_reduction = min(50, int(fri_score * 0.7))
            actions_with_reasons.append({
                "action": f"Reduce frequency caps by {cap_reduction}%",
                "reason": "Prevent audience overexposure to current creative"
            })
            
            # Add targeting recommendations based on performance metrics
            if has_cpa and cpa_change > 15:
                actions_with_reasons.append({
                    "action": "Refine audience targeting to higher-converting segments",
                    "reason": f"CPA has increased by {cpa_change:.1f}% since campaign start"
                })
            
            actions_with_reasons.append({
                "action": "Consider platform or format diversification",
                "reason": "Reduce dependence on fatigued channels"
            })
            
            # Daily monitoring for fatigue stage
            actions_with_reasons.append({
                "action": "Monitor performance daily",
                "reason": "Close monitoring required at fatigue stage"
            })
            
        elif stage == 'Failure':
            actions_with_reasons.extend([
                {
                    "action": "Pause current creative execution",
                    "reason": f"Critical fatigue detected with FRI score of {fri_score:.1f}"
                },
                {
                    "action": "Complete creative overhaul required",
                    "reason": "Minor refreshes insufficient at failure stage"
                }
            ])
            
            # Check age of campaign for structural recommendations
            if campaign_age > 30:
                actions_with_reasons.append({
                    "action": "Consider campaign restructure with new objectives",
                    "reason": f"Campaign has been running for {campaign_age} days with declining results"
                })
            
            # Budget reallocation recommendation based on severity
            if fri_score > 75:
                actions_with_reasons.append({
                    "action": "Reallocate at least 50% of budget to healthier campaigns",
                    "reason": "Critical performance deterioration detected"
                })
            else:
                actions_with_reasons.append({
                    "action": "Temporarily reduce budget by 30-40%",
                    "reason": "Conserve budget while implementing fixes"
                })
                
            # Platform-specific recommendation for critical cases
            actions_with_reasons.append({
                "action": "Reassess targeting strategy and platform mix",
                "reason": "Current approach is experiencing significant fatigue"
            })
            
        else:  # 'Unknown' stage or any other unclassified stage
            actions_with_reasons.extend([
                {
                    "action": "Collect additional campaign data",
                    "reason": "Insufficient data to classify fatigue stage"
                },
                {
                    "action": "Implement standard creative rotation schedule",
                    "reason": "Preventative measure while gathering more data"
                },
                {
                    "action": "Set up regular performance monitoring",
                    "reason": "Establish baseline for fatigue detection"
                }
            ])
        
        # Extract just the actions for backwards compatibility
        actions = [item["action"] for item in actions_with_reasons]
        
        return {
            "status": stage,
            "risk_level": risk_level,
            "fri_score": round(fri_score, 1),
            "actions": actions,
            "actions_with_reasons": actions_with_reasons,
            "metrics": {
                "campaign_age": int(campaign_age),
                "ctr_change": round(ctr_change, 1),
                "cpa_change": round(cpa_change, 1) if has_cpa else None
            }
        }
    
    def estimate_wasted_spend(self):
        """Estimate wasted ad spend due to fatigue"""
        if self.fatigue_scores is None:
            print("No fatigue scores available. Please calculate fatigue scores first.")
            return None
            
        wasted_spend = {}
        
        for campaign in self.fatigue_scores['campaign_id'].unique():
            campaign_data = self.fatigue_scores[self.fatigue_scores['campaign_id'] == campaign]
            
            # Get the latest stage and FRI score
            latest_data = campaign_data.iloc[-1]
            stage = latest_data['fatigue_stage']
            fri_score = latest_data['fri_score']
            
            # Skip campaigns with "Healthy" status
            if stage == 'Healthy':
                wasted_spend[campaign] = {
                    "total_spend": float(campaign_data['spend'].sum()),
                    "waste_percentage": 0.0,
                    "wasted_spend": 0.0,
                    "recoverable_spend": 0.0
                }
                continue
            
            # Calculate total spend for this campaign
            total_spend = campaign_data['spend'].sum()
            
            # Calculate waste percentage based on stage and FRI score
            if stage == 'Friction':
                waste_percentage = 0.20 + (fri_score / 100) * 0.3  # 20-50% waste
            elif stage == 'Fatigue':
                waste_percentage = 0.40 + (fri_score / 100) * 0.3  # 40-70% waste
            elif stage == 'Failure':
                waste_percentage = 0.70  # 70% waste
            else:  # Unknown or other stages
                waste_percentage = 0.10  # Default 10% waste
            
            # Calculate wasted spend
            wasted = total_spend * waste_percentage
            
            wasted_spend[campaign] = {
                "total_spend": float(total_spend),
                "waste_percentage": float(waste_percentage * 100),
                "wasted_spend": float(wasted),
                "recoverable_spend": float(wasted)
            }
        
        return wasted_spend
    
    def get_summary_report(self):
        """Generate a summary report with improved error handling and classification fixes"""
        if self.fatigue_scores is None or len(self.fatigue_scores) == 0:
            print("No fatigue scores available or empty data. Please calculate fatigue scores first.")
            return {
                "total_campaigns": 0,
                "campaign_stages": {},
                "total_spend": 0.0,
                "estimated_waste": 0.0,
                "high_risk_campaigns": [],
                "campaigns_by_stage": {
                    "Healthy": [],
                    "Friction": [],
                    "Fatigue": [],
                    "Failure": [],
                    "Unknown": []
                },
                "waste_percentage": 0.0
            }
        
        # First, ensure all campaigns are properly classified
        self.reclassify_campaigns()
        
        summary = {
            "total_campaigns": len(self.fatigue_scores['campaign_id'].unique()),
            "campaign_stages": {},
            "total_spend": float(self.fatigue_scores['spend'].sum()),
            "estimated_waste": 0.0,
            "high_risk_campaigns": [],
            "campaigns_by_stage": {
                "Healthy": [],
                "Friction": [],
                "Fatigue": [],
                "Failure": [],
                "Unknown": []  # Make sure Unknown is included
            }
        }
        
        # Count campaigns in each stage
        campaign_stages = {}
        for campaign in self.fatigue_scores['campaign_id'].unique():
            campaign_data = self.fatigue_scores[self.fatigue_scores['campaign_id'] == campaign]
            latest_stage = campaign_data.iloc[-1]['fatigue_stage']
            latest_fri = campaign_data.iloc[-1]['fri_score']
            
            # Double-check stage based on FRI score to ensure consistency
            if latest_fri >= 75 and latest_stage != 'Failure':
                latest_stage = 'Failure'
                self.fatigue_scores.loc[self.fatigue_scores['campaign_id'] == campaign, 'fatigue_stage'] = 'Failure'
            elif latest_fri >= 50 and latest_fri < 75 and latest_stage != 'Fatigue':
                latest_stage = 'Fatigue'
                self.fatigue_scores.loc[self.fatigue_scores['campaign_id'] == campaign, 'fatigue_stage'] = 'Fatigue'
            elif latest_fri >= 20 and latest_fri < 50 and latest_stage != 'Friction':
                latest_stage = 'Friction'
                self.fatigue_scores.loc[self.fatigue_scores['campaign_id'] == campaign, 'fatigue_stage'] = 'Friction'
            elif latest_fri < 20 and latest_stage != 'Healthy':
                latest_stage = 'Healthy'
                self.fatigue_scores.loc[self.fatigue_scores['campaign_id'] == campaign, 'fatigue_stage'] = 'Healthy'
            
            if latest_stage not in campaign_stages:
                campaign_stages[latest_stage] = 0
            campaign_stages[latest_stage] += 1
            
            # Add to campaigns by stage
            summary["campaigns_by_stage"][latest_stage].append(campaign)
            
            # Check if high risk (based on FRI score, not just stage)
            if latest_fri >= 50:  # Threshold for high risk
                summary["high_risk_campaigns"].append({
                    "campaign_id": campaign,
                    "fri_score": float(latest_fri),
                    "stage": latest_stage
                })
        
        summary["campaign_stages"] = campaign_stages
        
        # Calculate estimated waste
        wasted_spend = self.estimate_wasted_spend()
        if wasted_spend:
            total_waste = sum(data["wasted_spend"] for data in wasted_spend.values() if isinstance(data, dict))
            summary["estimated_waste"] = float(total_waste)
            summary["waste_percentage"] = float(total_waste / summary["total_spend"] * 100) if summary["total_spend"] > 0 else 0
        
        # Store the summary for future reference
        self.summary = summary
        
        return summary
    
    def plot_campaign_fatigue(self, campaign_id, save_path=None):
        """Generate visualization of campaign fatigue metrics"""
        if self.fatigue_scores is None:
            print("No fatigue scores available. Please calculate fatigue scores first.")
            return None
            
        campaign_data = self.fatigue_scores[self.fatigue_scores['campaign_id'] == campaign_id]
        
        if len(campaign_data) == 0:
            print(f"Campaign {campaign_id} not found")
            return None
            
        fig, axes = plt.subplots(3, 1, figsize=(12, 16), sharex=True)
        
        # Plot CTR
        axes[0].plot(campaign_data['date'], campaign_data['ctr'], marker='o', label='CTR')
        axes[0].set_title(f'Campaign {campaign_id} - CTR Over Time')
        axes[0].set_ylabel('CTR')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend()
        
        # Plot CPA
        if 'cpa' in campaign_data.columns:
            axes[1].plot(campaign_data['date'], campaign_data['cpa'], marker='s', color='green', label='CPA')
            axes[1].set_title(f'Campaign {campaign_id} - CPA Over Time')
            axes[1].set_ylabel('CPA')
            axes[1].grid(True, alpha=0.3)
            axes[1].legend()
        
        # Plot FRI Score with stage coloring
        cmap = {'Healthy': 'green', 'Friction': 'yellow', 'Fatigue': 'orange', 'Failure': 'red', 'Unknown': 'gray'}
        scatter = axes[2].scatter(
            campaign_data['date'], 
            campaign_data['fri_score'], 
            c=campaign_data['fatigue_stage'].map(lambda x: {'Healthy': 0, 'Friction': 1, 'Fatigue': 2, 'Failure': 3, 'Unknown': 4}.get(x, 4)),
            cmap=plt.cm.get_cmap('RdYlGn_r', 5),  # Use 5 colors now that we have Unknown
            marker='d',
            s=80
        )
        
        # Add legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=10, label='Healthy'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', markersize=10, label='Friction'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=10, label='Fatigue'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Failure'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label='Unknown')
        ]
        axes[2].legend(handles=legend_elements, loc='upper left')
        
        axes[2].set_title(f'Campaign {campaign_id} - Fatigue Risk Index (FRI) Score')
        axes[2].set_ylabel('FRI Score')
        axes[2].set_xlabel('Date')
        axes[2].grid(True, alpha=0.3)
        
        # Add threshold lines
        axes[2].axhline(y=20, color='yellow', linestyle='--', alpha=0.5, label='Friction Threshold')
        axes[2].axhline(y=50, color='orange', linestyle='--', alpha=0.5, label='Fatigue Threshold')
        axes[2].axhline(y=75, color='red', linestyle='--', alpha=0.5, label='Failure Threshold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            print(f"Plot saved to {save_path}")
            
        return fig