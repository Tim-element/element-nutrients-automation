# Element Nutrients Automation

Automated tools for Amazon PPC management and customer review requests.

## Current Tools

### 1. Amazon PPC Analyzer (`ppc/`
- Pulls campaign performance data
- Identifies high ACOS keywords
- Suggests bid adjustments
- Flags underperformers

### 2. Review Request Generator (`reviews/`
- Identifies repeat customers from order data
- Generates personalized review request emails
- Tracks who has been contacted

## Setup

### Amazon Advertising API
1. Go to Seller Central → Advertising → API Access
2. Create authorization
3. Add credentials to `.env` file

### Order Data
Export orders from Seller Central and place in `data/orders/`

## Usage

```bash
# Analyze PPC campaigns
python ppc/analyzer.py

# Generate review requests
python reviews/generator.py
```

---
*Built by Tim (your overnight employee)*
