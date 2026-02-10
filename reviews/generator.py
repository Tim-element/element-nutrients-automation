"""
Review Request Generator
Identifies repeat customers and generates personalized review request emails.
"""

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional

# Configuration
MIN_PURCHASES = 2  # Minimum orders to be considered repeat customer
MIN_DAYS_SINCE_ORDER = 7  # Wait at least 7 days
MAX_DAYS_SINCE_ORDER = 30  # Don't go beyond 30 days
TRACKING_FILE = Path(__file__).parent / "data" / "contacted_customers.csv"

# Paths
OUTPUT_DIR = Path(__file__).parent / "output"
DATA_DIR = Path(__file__).parent.parent / "data" / "orders"

# Email template
EMAIL_TEMPLATE = """Subject: How's your {product_name} working out?

Hi {first_name},

I hope you're doing well! I noticed you've ordered from us {order_count} times now, and I wanted to personally reach out and say thank you for being such a loyal customer.

Your support means everything to me as a small business owner. I'm always working to improve our products, and honest feedback from customers like you helps me do that.

If you have a moment, would you mind leaving a quick review on Amazon for your recent {product_name} purchase? It takes just a minute and helps other gardeners discover our products.

[Amazon Review Link]

Thanks again for your support!

Best,
Ryan
Element Nutrients
"""


def load_orders(filename: str = "orders.csv") -> List[Dict]:
    """Load order data from CSV export."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        print(f"⚠️  No order data found at {filepath}")
        print("   Export from Amazon: Orders > Order Reports > Request Report")
        return []
    
    orders = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            orders.append(row)
    return orders


def parse_order_date(date_str: str) -> Optional[datetime]:
    """Parse Amazon order date format."""
    try:
        # Common formats: 2024-01-15, 01/15/2024, etc.
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y', '%Y-%m-%d %H:%M:%S']:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
    except:
        pass
    return None


def get_contacted_customers() -> Set[str]:
    """Get list of customers already contacted."""
    if not TRACKING_FILE.exists():
        return set()
    
    contacted = set()
    with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacted.add(row.get('email', '').lower())
    return contacted


def identify_repeat_customers(orders: List[Dict]) -> Dict[str, Dict]:
    """Group orders by customer and identify repeat buyers."""
    customers = {}
    
    for order in orders:
        email = order.get('Buyer Email', '').lower()
        if not email:
            continue
        
        if email not in customers:
            customers[email] = {
                'email': email,
                'name': order.get('Buyer Name', 'Valued Customer'),
                'orders': [],
                'total_spent': 0
            }
        
        # Parse order date
        date_str = order.get('Purchase Date', order.get('Order Date', ''))
        order_date = parse_order_date(date_str)
        
        customers[email]['orders'].append({
            'order_id': order.get('Order ID', ''),
            'date': order_date,
            'product': order.get('Product Name', 'Unknown Product'),
            'amount': float(order.get('Item Price', 0)),
            'status': order.get('Order Status', 'Unknown')
        })
        
        try:
            customers[email]['total_spent'] += float(order.get('Item Price', 0))
        except:
            pass
    
    # Filter for repeat customers
    repeat_customers = {}
    for email, data in customers.items():
        if len(data['orders']) >= MIN_PURCHASES:
            repeat_customers[email] = data
    
    return repeat_customers


def is_eligible_for_review(customer: Dict, contacted: Set[str]) -> Optional[Dict]:
    """Check if customer is eligible for review request."""
    email = customer['email']
    
    # Already contacted?
    if email in contacted:
        return None
    
    # Get most recent order
    orders = sorted(customer['orders'], key=lambda x: x['date'] or datetime.min, reverse=True)
    latest_order = orders[0]
    
    # Must have a valid date
    if not latest_order['date']:
        return None
    
    # Check date range
    days_ago = (datetime.now() - latest_order['date']).days
    if days_ago < MIN_DAYS_SINCE_ORDER or days_ago > MAX_DAYS_SINCE_ORDER:
        return None
    
    # Check order status (should be delivered)
    status = latest_order['status'].upper()
    if 'CANCEL' in status or 'RETURN' in status:
        return None
    
    return {
        'email': email,
        'name': customer['name'],
        'first_name': customer['name'].split()[0] if customer['name'] else 'Friend',
        'order_count': len(orders),
        'total_spent': customer['total_spent'],
        'latest_order': latest_order,
        'days_since_order': days_ago
    }


def generate_email(customer: Dict) -> str:
    """Generate personalized email."""
    product = customer['latest_order']['product']
    # Extract short product name (first 3-4 words)
    short_product = ' '.join(product.split()[:4])
    
    return EMAIL_TEMPLATE.format(
        first_name=customer['first_name'],
        product_name=short_product,
        order_count=customer['order_count']
    )


def generate_reports(eligible: List[Dict]) -> None:
    """Generate output reports."""
    today = datetime.now().strftime('%Y-%m-%d')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if not eligible:
        print("   No eligible customers found today.")
        return
    
    # CSV list for Mailchimp/upload
    csv_file = OUTPUT_DIR / f"{today}_review_requests.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'Email', 'First Name', 'Order Count', 'Total Spent', 
            'Latest Product', 'Days Since Order', 'Email Draft'
        ])
        writer.writeheader()
        for c in eligible:
            writer.writerow({
                'Email': c['email'],
                'First Name': c['first_name'],
                'Order Count': c['order_count'],
                'Total Spent': f"${c['total_spent']:.2f}",
                'Latest Product': c['latest_order']['product'],
                'Days Since Order': c['days_since_order'],
                'Email Draft': generate_email(c).replace('\n', ' | ')
            })
    
    # Text file with ready-to-send emails
    text_file = OUTPUT_DIR / f"{today}_email_drafts.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(f"Review Request Email Drafts - {today}\n")
        f.write("=" * 60 + "\n\n")
        
        for c in eligible:
            f.write(f"To: {c['email']}\n")
            f.write(f"Customer: {c['name']} ({c['order_count']} orders, ${c['total_spent']:.2f})\n")
            f.write("-" * 60 + "\n")
            f.write(generate_email(c))
            f.write("\n" + "=" * 60 + "\n\n")
    
    print(f"\n📧 Generated {len(eligible)} review requests")
    print(f"   Reports saved:")
    print(f"   - {csv_file.name} (for Mailchimp)")
    print(f"   - {text_file.name} (ready to send)")


def main():
    """Main entry point."""
    print("🚀 Review Request Generator")
    print("=" * 50)
    
    orders = load_orders()
    if not orders:
        print("\n📋 To get started:")
        print("   1. Go to Amazon Seller Central")
        print("   2. Orders > Order Reports")
        print("   3. Request Report (last 90 days)")
        print("   4. Save CSV to: data/orders/orders.csv")
        return
    
    print(f"   Loaded {len(orders)} orders")
    
    # Get already contacted customers
    contacted = get_contacted_customers()
    print(f"   Already contacted: {len(contacted)} customers")
    
    # Find repeat customers
    repeat = identify_repeat_customers(orders)
    print(f"   Repeat customers: {len(repeat)}")
    
    # Find eligible ones
    eligible = []
    for email, customer in repeat.items():
        result = is_eligible_for_review(customer, contacted)
        if result:
            eligible.append(result)
    
    print(f"   Eligible for review request: {len(eligible)}")
    
    # Generate reports
    generate_reports(eligible)
    
    if eligible:
        print("\n✅ Next steps:")
        print("   1. Review email drafts in output/ folder")
        print("   2. Send via Gmail or upload to Mailchimp")
        print("   3. Mark as contacted to avoid duplicates")


if __name__ == "__main__":
    main()
