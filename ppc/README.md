# Amazon PPC Campaign Analyzer

Analyzes your Amazon advertising campaigns and provides actionable recommendations.

## What It Does

1. **Pulls campaign data** from Amazon Advertising API
2. **Calculates ACOS** (Advertising Cost of Sale) for each keyword/ad group
3. **Identifies problems:**
   - High ACOS keywords (above your target)
   - Low CTR ads (wasting impressions)
   - Overspending campaigns
4. **Generates recommendations:**
   - Bid adjustments (up/down)
   - Keywords to pause
   - Budget reallocation suggestions

## Output

Creates daily reports in `reports/ppc/`:
- `YYYY-MM-DD_summary.csv` - Top-level campaign stats
- `YYYY-MM-DD_actions.csv` - Specific actions to take

## Configuration

Edit `config.py` to set:
- Target ACOS (default: 30%)
- Minimum clicks before judgment (default: 20)
- Bid adjustment increments (default: 10%)

## Future: Auto-Execution

Currently generates recommendations only. Once you approve the approach, can connect to API to execute bid changes automatically.
