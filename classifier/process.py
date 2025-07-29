import random

def generate_synthetic_not_scam(num_samples):
    not_scam_templates = [
        "Your order #{} has been confirmed and will be delivered by {} to your address at {}.",
        "Thank you for your payment of ${} for your {} subscription. Contact {} for support.",
        "Your appointment with {} is scheduled for {} at {}. Please confirm by replying to {}.",
        "We’ve processed your refund of ${} for your purchase on {}. Expect it within {} days.",
        "Your account balance for {} is ${}. Log in at {} to view details.",
        "Thank you for registering for our {} event. A confirmation email was sent to {}.",
        "Your donation of ${} to {} has been received. You’ll get a receipt at {}.",
        "We’re offering a {}% discount on your next purchase at {}. Use code {} at checkout.",
        "Your loan application for ${} has been approved. Visit {} to finalize the terms.",
        "Thank you for your feedback on {}. We’ll use it to improve our services at {}.",
    ]

    companies = ["Amazon", "Netflix", "Shopify", "Local Clinic", "Charity Org", "Bank of America"]
    dates = ["Monday, Oct 10", "Tuesday, Nov 15", "Friday, Dec 5"]
    times = ["9:00 AM", "1:00 PM", "3:30 PM"]
    emails = ["support@company.com", "help@service.org", "info@store.com"]
    addresses = ["123 Main St", "456 Oak Ave", "789 Pine Rd"]
    services = ["Premium Plan", "Annual Membership", "Online Course"]
    codes = ["SAVE10", "DISCOUNT20", "FREESHIP"]

    not_scam_data = []
    for _ in range(num_samples):
        template = random.choice(not_scam_templates)
        filled_template = template.format(
            random.randint(1000, 9999),  # Order number
            random.choice(dates),  # Delivery date
            random.choice(addresses),  # Address
            random.randint(10, 500),  # Amount
            random.choice(services),  # Service
            random.choice(emails),  # Support email
            random.choice(["Dr. Smith", "Dr. Lee", "Dr. Patel"]),  # Doctor
            random.choice(dates),  # Appointment date
            random.choice(times),  # Appointment time
            random.choice(emails),  # Confirmation email
            random.choice(["3-5", "5-7", "7-10"]),  # Refund days
            random.choice(dates),  # Purchase date
            random.choice(companies),  # Company
            random.uniform(10, 1000),  # Balance
            random.choice(["app.company.com", "portal.service.org"]),  # Login URL
            random.choice(["webinar", "workshop", "conference"]),  # Event
            random.choice(emails),  # Receipt email
            random.randint(5, 50),  # Discount percentage
            random.choice(companies),  # Store
            random.choice(codes),  # Discount code
        )
        not_scam_data.append(filled_template)

    return not_scam_data