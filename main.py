# -*- coding: utf-8 -*-
import os
from email_reader import fetch_emails
from ai_analyzer import analyze_email_for_phishing, format_analysis_report


def get_credentials():
    """Get email credentials from environment variables or user input."""
    email_address = os.environ.get("EMAIL_ADDRESS")
    password = os.environ.get("EMAIL_PASSWORD")
    imap_server = os.environ.get("IMAP_SERVER", "imap.gmail.com")

    if not email_address:
        email_address = input("Enter your email address: ").strip()
    if not password:
        password = input("Enter your app password: ").strip()

    return email_address, password, imap_server


def run_demo_mode():
    """Run with sample emails for testing without real credentials."""
    print("\n[*] Running in DEMO MODE with sample emails...\n")

    sample_emails = [
        {
            "sender": "security@paypa1-alert.com",
            "subject": "URGENT: Your account has been suspended!",
            "body": """Dear Valued Customer,

We have detected unusual activity on your PayPal account.
Your account has been temporarily suspended.

Click here IMMEDIATELY to restore access:
http://paypal-secure-login.suspicious-site.xyz/restore

You must verify within 24 hours or your account will be permanently deleted.

Provide your:
- Full name
- Credit card number
- Social security number
- Password

PayPal Security Team"""
        },
        {
            "sender": "newsletter@medium.com",
            "subject": "Your weekly reading list is ready",
            "body": """Hi there,

Here's your personalized reading list for this week based on your interests:

1. "The Future of AI in Software Development" by Jane Doe
2. "10 Python Tips Every Developer Should Know" by John Smith
3. "Understanding Cloud Architecture" by Tech Weekly

Happy reading!

The Medium Team
Unsubscribe | Privacy Policy | Help"""
        },
        {
            "sender": "hr-noreply@totally-real-company.net",
            "subject": "You've been selected for a $500 gift card!",
            "body": """Congratulations Employee!

You have been randomly selected to receive a $500 Amazon Gift Card
as part of our employee appreciation program!

To claim your reward, click the link below and enter your
employee credentials and banking information for direct deposit:

http://employee-rewards.sketchy-domain.ru/claim

Hurry! This offer expires in 2 hours.

HR Department"""
        }
    ]
    return sample_emails


def main():
    print("=" * 60)
    print("   [PHISHGUARD-AI] AI-POWERED PHISHING EMAIL DETECTOR")
    print("=" * 60)
    print("\nThis tool analyzes your emails using Claude AI")
    print("to detect phishing attempts and calculate risk scores.\n")

    mode = input("Choose mode:\n  [1] Analyze real emails (requires credentials)\n  [2] Demo mode (sample emails)\nEnter choice (1 or 2): ").strip()

    if mode == "2":
        emails = run_demo_mode()
    else:
        try:
            num = int(input("How many recent emails to analyze? (default 5): ").strip() or "5")
        except ValueError:
            num = 5

        email_address, password, imap_server = get_credentials()

        print(f"\n[*] Connecting to {imap_server}...")
        emails = fetch_emails(email_address, password, imap_server, num_emails=num)

        if not emails:
            print("[ERROR] No emails fetched. Check credentials or enable IMAP in your email settings.")
            return

    print(f"\n[+] Fetched {len(emails)} email(s). Analyzing with Claude AI...\n")

    phishing_count = 0
    total_score = 0

    for i, email_data in enumerate(emails, 1):
        print(f"[*] Analyzing email {i}/{len(emails)}: \"{email_data['subject'][:50]}...\"")

        analysis = analyze_email_for_phishing(
            subject=email_data["subject"],
            sender=email_data["sender"],
            body=email_data["body"]
        )

        report = format_analysis_report(email_data, analysis)
        print(report)

        if analysis.get("is_phishing"):
            phishing_count += 1
        total_score += analysis.get("score", 0)

    # Summary
    avg_score = total_score / len(emails) if emails else 0
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total Emails Analyzed : {len(emails)}")
    print(f"  Phishing Detected     : {phishing_count}")
    print(f"  Safe Emails           : {len(emails) - phishing_count}")
    print(f"  Average Risk Score    : {avg_score:.1f}/100")

    if phishing_count > 0:
        print(f"\n  [WARNING] {phishing_count} phishing email(s) detected!")
        print("  Do NOT click any links or provide personal information.")
    else:
        print("\n  [OK] No phishing emails detected. Stay vigilant!")
    print("=" * 60)


if __name__ == "__main__":
    main()
