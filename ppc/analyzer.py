"""
Amazon PPC Campaign Analyzer
Analyzes campaign performance and generates optimization recommendations.
"""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
TARGET_ACOS = 0.30  # 30% target ACOS
MIN_CLICKS = 20  # Minimum clicks before making judgment
BID_ADJUSTMENT_UP = 0.10  # 10% increase
BID_ADJUSTMENT_DOWN = 0.15  # 15% decrease
PAUSE_THRESHOLD_ACOS = 0.50  # Pause if ACOS > 50%

# Paths
REPORTS_DIR = Path(__file__).parent / "reports"
DATA_DIR = Path(__file__).parent.parent / "data" / "ppc"


def load_campaign_data(filename: str = "campaigns.csv") -> List[Dict]:
    """Load campaign data from CSV export."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        print(f"⚠️  No campaign data found at {filepath}")
        print("   Export from Amazon: Advertising > Campaign Manager > Export")
        return []
    
    campaigns = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            campaigns.append(row)
    return campaigns


def calculate_acos(spend: float, sales: float) -> float:
    """Calculate ACOS (Advertising Cost of Sale)."""
    if sales == 0:
        return 1.0  # 100% if no sales
    return spend / sales


def analyze_campaign(campaign: Dict) -> Optional[Dict]:
    """Analyze a single campaign and return recommendations."""
    try:
        name = campaign.get('Campaign Name', 'Unknown')
        spend = float(campaign.get('Spend', 0))
        sales = float(campaign.get('Sales', 0))
        clicks = int(float(campaign.get('Clicks', 0)))
        impressions = int(float(campaign.get('Impressions', 0)))
        current_bid = float(campaign.get('Bid', 0.50))
        
        acos = calculate_acos(spend, sales)
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        
        recommendation = {
            'campaign': name,
            'spend': spend,
            'sales': sales,
            'acos': acos,
            'clicks': clicks,
            'ctr': ctr,
            'current_bid': current_bid,
            'action': 'HOLD',
            'new_bid': current_bid,
            'reason': ''
        }
        
        # Skip if not enough data
        if clicks < MIN_CLICKS:
            recommendation['reason'] = f'Not enough clicks ({clicks} < {MIN_CLICKS})'
            return recommendation
        
        # High ACOS - pause or reduce bid
        if acos > PAUSE_THRESHOLD_ACOS:
            recommendation['action'] = 'PAUSE'
            recommendation['reason'] = f'High ACOS ({acos:.1%})'
        elif acos > TARGET_ACOS:
            recommendation['action'] = 'REDUCE_BID'
            recommendation['new_bid'] = round(current_bid * (1 - BID_ADJUSTMENT_DOWN), 2)
            recommendation['reason'] = f'ACOS ({acos:.1%}) above target ({TARGET_ACOS:.1%})'
        
        # Low ACOS, good performance - increase bid
        elif acos < TARGET_ACOS * 0.7:  # 30% below target = great performance
            recommendation['action'] = 'INCREASE_BID'
            recommendation['new_bid'] = round(current_bid * (1 + BID_ADJUSTMENT_UP), 2)
            recommendation['reason'] = f'Great ACOS ({acos:.1%}), scale up'
        
        # Low CTR - investigate
        elif ctr < 0.3:
            recommendation['action'] = 'REVIEW'
            recommendation['reason'] = f'Low CTR ({ctr:.2f}%), check relevance'
        
        else:
            recommendation['reason'] = f'Performing well (ACOS: {acos:.1%})'
        
        return recommendation
        
    except (ValueError, KeyError) as e:
        print(f"⚠️  Error analyzing campaign: {e}")
        return None


def generate_report(campaigns: List[Dict]) -> None:
    """Generate analysis report."""
    today = datetime.now().strftime('%Y-%m-%d')
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Analyze all campaigns
    results = []
    for campaign in campaigns:
        result = analyze_campaign(campaign)
        if result:
            results.append(result)
    
    if not results:
        print("⚠️  No campaigns to analyze")
        return
    
    # Summary report
    summary_file = REPORTS_DIR / f"{today}_summary.csv"
    with open(summary_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'campaign', 'spend', 'sales', 'acos', 'clicks', 'ctr', 'action', 'reason'
        ])
        writer.writeheader()
        for r in results:
            writer.writerow({
                'campaign': r['campaign'],
                'spend': f"${r['spend']:.2f}",
                'sales': f"${r['sales']:.2f}",
                'acos': f"{r['acos']:.1%}",
                'clicks': r['clicks'],
                'ctr': f"{r['ctr']:.2f}%",
                'action': r['action'],
                'reason': r['reason']
            })
    
    # Actions report (only actionable items)
    actions = [r for r in results if r['action'] != 'HOLD']
    actions_file = REPORTS_DIR / f"{today}_actions.csv"
    with open(actions_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'campaign', 'action', 'current_bid', 'new_bid', 'reason'
        ])
        writer.writeheader()
        for r in actions:
            writer.writerow({
                'campaign': r['campaign'],
                'action': r['action'],
                'current_bid': f"${r['current_bid']:.2f}",
                'new_bid': f"${r['new_bid']:.2f}" if r['action'] in ['INCREASE_BID', 'REDUCE_BID'] else 'N/A',
                'reason': r['reason']
            })
    
    # Print summary
    print(f"\n📊 PPC Analysis Complete - {today}")
    print(f"   Campaigns analyzed: {len(results)}")
    print(f"   Actions needed: {len(actions)}")
    print(f"\n   Reports saved:")
    print(f"   - {summary_file.name}")
    print(f"   - {actions_file.name}")
    
    # Print action summary
    if actions:
        print(f"\n🎯 Recommended Actions:")
        for a in actions[:10]:  # Show top 10
            print(f"   {a['action']}: {a['campaign']}")
            print(f"      └─ {a['reason']}")


def main():
    """Main entry point."""
    print("🚀 Amazon PPC Analyzer")
    print("=" * 50)
    
    campaigns = load_campaign_data()
    if campaigns:
        generate_report(campaigns)
    else:
        print("\n📋 To get started:")
        print("   1. Go to Amazon Seller Central")
        print("   2. Advertising > Campaign Manager")
        print("   3. Click 'Export' to download campaign data")
        print("   4. Save CSV to: data/ppc/campaigns.csv")


if __name__ == "__main__":
    main()
