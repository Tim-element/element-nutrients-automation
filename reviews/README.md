# Review Request Automation

Identifies repeat customers and generates personalized review request emails.

## What It Does

1. **Imports order data** from your Amazon exports
2. **Identifies repeat buyers** (2+ purchases)
3. **Filters eligible customers:**
   - 7-30 days since last order (sweet spot for reviews)
   - Haven't been contacted yet
   - Order delivered successfully
4. **Generates personalized emails** with:
   - Customer name
   - Product they bought
   - Friendly, non-pushy tone

## Output

Creates daily files in `reviews/output/`:
- `YYYY-MM-DD_review_requests.csv` - List of customers to contact
- `YYYY-MM-DD_email_drafts.txt` - Ready-to-send email drafts

## Integration Options

### Option A: Manual (Current)
You copy email drafts and send via Gmail

### Option B: Mailchimp (Recommended)
Upload CSV to Mailchimp and send campaign

### Option C: Full Auto (Future)
Connect to Amazon's "Request a Review" API or email system

## Configuration

Edit `config.py` to customize:
- Days since order (default: 7-30)
- Minimum purchase count (default: 2)
- Email template
