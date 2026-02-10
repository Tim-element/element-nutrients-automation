"""
Amazon PPC Campaign Analyzer
Analyzes Amazon Advertising campaign performance and generates optimization recommendations.
"""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
TARGET_ACOS = 0.30  # 30% target ACOS (Advertising Cost of Sale)
MIN_CLICKS = 20  # Minimum clicks before making judgment
MIN_IMPRESSIONS = 500  # Minimum impressions to evaluate
BID_ADJUSTMENT_UP = 0.10  # 10% increase
BID_ADJUSTMENT_DOWN = 0.15  # 15% decrease
PAUSE_THRESHOLD_ACOS = 0.50  # Flag if ACOS > 50%

# Paths
REPORTS_DIR = Path(__file__).parent / "reports"
DATA_DIR = Path(__file__).parent.parent / "data" / "ppc"


def load_campaign_data(filename: str = "campaigns.csv") -> List[Dict]:
    """Load campaign data from Amazon CSV export."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        # Try to auto-find any CSV in the folder
        csv_files = list(DATA_DIR.glob("*.csv"))
        if csv_files:
            filepath = csv_files[0]
            print(f"   Found: {filepath.name}")
        else:
            print(f"⚠️  No campaign data found in {DATA_DIR}")
            print("   Export from Amazon: Advertising > Campaign Manager > Bulk Operations")
            return []
    
    campaigns = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
        reader = csv.DictReader(f)
        for row in reader:
            campaigns.append(row)
    return campaigns


def parse_currency(value) -> float:
    """Parse currency string to float."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    # Remove currency symbols and commas
    cleaned = str(value).replace('$', '').replace(',', '').replace('"', '').strip()
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def parse_number(value) -> float:
    """Parse number string to float."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).replace(',', '').replace('"', '').strip()
    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def extract_field(row: Dict, possible_names: List[str]) -> str:
    """Extract field value trying multiple possible column names."""
    for name in possible_names:
        if name in row:
            return row[name]
    return ""


def analyze_campaign(campaign: Dict) -> Optional[Dict]:
    """Analyze a single campaign and return recommendations."""
    try:
        # Map Amazon's column names to our fields
        name = extract_field(campaign, ['Campaign name', 'Campaign Name', 'Campaign'])
        if not name:
            return None
            
        spend = parse_currency(extract_field(campaign, ['Total cost', 'Spend', 'Cost', 'Total Cost']))
        sales = parse_currency(extract_field(campaign, ['Sales', 'Sales (promoted)', 'Total Sales']))
        clicks = int(parse_number(extract_field(campaign, ['Clicks', 'Gross clicks', 'Total Clicks'])))
        impressions = int(parse_number(extract_field(campaign, ['Impressions', 'Total Impressions'])))
        
        # Try to get ROAS directly if available
        roas_str = extract_field(campaign, ['ROAS', 'ROAS (promoted)'])
        roas = parse_number(roas_str) if roas_str else 0
        
        # Calculate ACOS
        if sales > 0:
            acos = spend / sales
        elif roas > 0:
            acos = 1 / roas
        else:
            acos = 0 if spend == 0 else 1.0
        
        # Calculate CTR
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        
        # Calculate CPC
        cpc = spend / clicks if clicks > 0 else 0
        
        recommendation = {
            'campaign': name,
            'spend': spend,
            'sales': sales,
            'acos': acos,
            'roas': roas if roas > 0 else (sales / spend if spend > 0 else 0),
            'clicks': clicks,
            'impressions': impressions,
            'ctr': ctr,
            'cpc': cpc,
            'action': 'HOLD',
            'priority': 'LOW',
            'reason': ''
        }
        
        # Skip if not enough data
        if impressions < MIN_IMPRESSIONS:
            recommendation['reason'] = f'Not enough impressions ({impressions} < {MIN_IMPRESSIONS})'
            return recommendation
        
        if clicks < MIN_CLICKS:
            recommendation['reason'] = f'Not enough clicks ({clicks} < {MIN_CLICKS})'
            return recommendation
        
        # Decision logic
        if acos > PAUSE_THRESHOLD_ACOS:
            recommendation['action'] = 'URGENT_REVIEW'
            recommendation['priority'] = 'HIGH'
            recommendation['reason'] = f'ACOS {acos:.1%} is very high (target: {TARGET_ACOS:.1%}). Consider pausing or aggressive bid reduction.'
        elif acos > TARGET_ACOS:
            recommendation['action'] = 'REDUCE_BID'
            recommendation['priority'] = 'MEDIUM'
            recommendation['reason'] = f'ACOS {acos:.1%} above target {TARGET_ACOS:.1%}. Reduce bids by ~{BID_ADJUSTMENT_DOWN:.0%}.'
        elif acos < TARGET_ACOS * 0.6:  # Exceptional performance (40% below target)
            recommendation['action'] = 'INCREASE_BID'
            recommendation['priority'] = 'HIGH'
            recommendation['reason'] = f'Excellent ACOS {acos:.1%}! Increase bids by {BID_ADJUSTMENT_UP:.0%} to scale.'
        elif acos < TARGET_ACOS * 0.85:  # Good performance (15% below target)
            recommendation['action'] = 'INCREASE_BID'
            recommendation['priority'] = 'MEDIUM'
            recommendation['reason'] = f'Good ACOS {acos:.1%}. Increase bids slightly to capture more sales.'
        elif ctr < 0.2:
            recommendation['action'] = 'REVIEW_CREATIVES'
            recommendation['priority'] = 'MEDIUM'
            recommendation['reason'] = f'Low CTR {ctr:.2f}%. Review images, titles, and targeting.'
        else:
            recommendation['reason'] = f'Performing well (ACOS: {acos:.1%}, CTR: {ctr:.2f}%)'
        
        return recommendation
        
    except Exception as e:
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
    
    # Sort by priority and spend
    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    results.sort(key=lambda x: (priority_order.get(x['priority'], 3), -x['spend']))
    
    # Summary report - all campaigns
    summary_file = REPORTS_DIR / f"{today}_summary.csv"
    with open(summary_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'campaign', 'spend', 'sales', 'acos', 'roas', 'clicks', 'impressions', 
            'ctr', 'cpc', 'action', 'priority', 'reason'
        ])
        writer.writeheader()
        for r in results:
            writer.writerow({
                'campaign': r['campaign'],
                'spend': f"${r['spend']:.2f}",
                'sales': f"${r['sales']:.2f}",
                'acos': f"{r['acos']:.1%}",
                'roas': f"{r['roas']:.2f}",
                'clicks': r['clicks'],
                'impressions': r['impressions'],
                'ctr': f"{r['ctr']:.2f}%",
                'cpc': f"${r['cpc']:.2f}",
                'action': r['action'],
                'priority': r['priority'],
                'reason': r['reason']
            })
    
    # Actions report - only actionable items
    actions = [r for r in results if r['action'] != 'HOLD']
    actions_file = REPORTS_DIR / f"{today}_actions.csv"
    with open(actions_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'priority', 'campaign', 'action', 'acos', 'spend', 'sales', 'reason'
        ])
        writer.writeheader()
        for r in actions:
            writer.writerow({
                'priority': r['priority'],
                'campaign': r['campaign'],
                'action': r['action'],
                'acos': f"{r['acos']:.1%}",
                'spend': f"${r['spend']:.2f}",
                'sales': f"${r['sales']:.2f}",
                'reason': r['reason']
            })
    
    # Print summary to console
    print(f"\n📊 PPC Analysis Complete - {today}")
    print(f"=" * 60)
    print(f"   Campaigns analyzed: {len(results)}")
    print(f"   Actions needed: {len(actions)}")
    
    total_spend = sum(r['spend'] for r in results)
    total_sales = sum(r['sales'] for r in results)
    overall_acos = total_spend / total_sales if total_sales > 0 else 0
    
    print(f"\n   Total Spend: ${total_spend:,.2f}")
    print(f"   Total Sales: ${total_sales:,.2f}")
    print(f"   Overall ACOS: {overall_acos:.1%}")
    print(f"   Overall ROAS: {(total_sales/total_spend if total_spend > 0 else 0):.2f}")
    
    print(f"\n   Reports saved:")
    print(f"   - {summary_file.name}")
    print(f"   - {actions_file.name}")
    
    # Print action summary
    if actions:
        print(f"\n🎯 Recommended Actions (by priority):")
        print("-" * 60)
        for a in actions[:15]:  # Show top 15
            print(f"\n   [{a['priority']}] {a['action']}")
            print(f"   Campaign: {a['campaign']}")
            print(f"   ACOS: {a['acos']:.1%} | Spend: ${a['spend']:.2f}")
            print(f"   └─ {a['reason']}")
        
        if len(actions) > 15:
            print(f"\n   ... and {len(actions) - 15} more actions")
    else:
        print("\n✅ All campaigns performing within target ACOS!")


def main():
    """Main entry point."""
    print("🚀 Amazon PPC Analyzer")
    print("=" * 60)
    
    # Look for any CSV file in the ppc folder
    csv_files = list(DATA_DIR.glob("*.csv"))
    
    if not csv_files:
        print("\n📋 To get started:")
        print("   1. Go to Amazon Seller Central")
        print("   2. Advertising > Campaign Manager")
        print("   3. Click 'Bulk Operations' > 'Create Report'")
        print("   4. Select date range and download CSV")
        print("   5. Save to: data/ppc/")
        return
    
    # Process all CSV files found
    for csv_file in csv_files:
        print(f"\n📁 Processing: {csv_file.name}")
        campaigns = load_campaign_data(csv_file.name)
        if campaigns:
            generate_report(campaigns)
        else:
            print(f"   No data in {csv_file.name}")


if __name__ == "__main__":
    main()
