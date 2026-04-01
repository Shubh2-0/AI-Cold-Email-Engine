"""
HR Cold Email Sender Tool — Shubham Bhati
==========================================
Sends personalized job application emails to HR contacts with resume attached.

Usage:
    python email_sender.py              # Send today's batch (default 30)
    python email_sender.py --count 10   # Send only 10 emails
    python email_sender.py --tier TIER1 # Send only to TIER1 contacts
    python email_sender.py --preview    # Preview emails without sending
    python email_sender.py --status     # Show sending progress
    python email_sender.py --test       # Send test email to yourself
"""

import smtplib
import csv
import json
import os
import sys
import time
import argparse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config():
    config_path = os.path.join(SCRIPT_DIR, "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    # Override with environment variables (for GitHub Actions)
    if os.environ.get("GMAIL_APP_PASSWORD"):
        config["app_password"] = os.environ["GMAIL_APP_PASSWORD"]
    if os.environ.get("GMAIL_ADDRESS"):
        config["sender_email"] = os.environ["GMAIL_ADDRESS"]
    return config


def get_sent_today(log_path):
    """Count how many emails were sent today."""
    today = date.today().isoformat()
    count = 0
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("date", "").startswith(today):
                    count += 1
    return count


def get_all_sent_emails(log_path):
    """Get set of all emails already sent."""
    sent = set()
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sent.add(row["email"].lower())
    return sent


def log_sent(log_path, contact, status):
    """Log a sent email."""
    file_exists = os.path.exists(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "time", "name", "email", "company", "tier", "status"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "date": date.today().isoformat(),
            "time": datetime.now().strftime("%H:%M:%S"),
            "name": contact["name"],
            "email": contact["email"],
            "company": contact["company"],
            "tier": contact["tier"],
            "status": status,
        })


def update_contacts_csv(csv_path, sent_email):
    """Mark contact as sent in the contacts CSV."""
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            if row["email"].lower() == sent_email.lower():
                row["sent"] = "YES"
            rows.append(row)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_pending_contacts(csv_path, tier_filter=None):
    """Get contacts that haven't been emailed yet."""
    pending = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["sent"].strip().upper() == "YES":
                continue
            if tier_filter and row["tier"] != tier_filter:
                continue
            pending.append(row)
    return pending


def get_email_body(contact, config):
    """Generate personalized email body based on company/tier."""
    raw_name = contact["name"].strip()
    name = raw_name.split()[0] if raw_name and raw_name.lower() not in ["hr", "team", "hr team"] else "Team"
    company = contact["company"]
    tier = contact["tier"]

    if tier == "TIER1":
        body = f"""Hi {name},

Java Backend Engineer | 2+ yrs | Immediate Joiner | Gurgaon

Currently at AlignBits, working on Justransform — an enterprise B2B
integration platform serving 10+ clients across REST, SFTP, AS2, SOAP.

My contributions:
  - Delivered client-facing features and bug fixes
  - Added new protocol modules (AS2)
  - Java migration (11→17), dev and prod deployments
  - Server monitoring — alarms, cron jobs, scheduled tasks
  - Previously: Healthcare backend at IHX
  - Side project: Built and launched a live e-commerce platform end-to-end
    (backend, admin panel, payments, deployment) → maakaalicreations.in

Tech: Java, Spring Boot, Microservices, REST APIs, MySQL, Docker, JWT
Notice Period: Immediate Joiner
Location: Gurgaon (on-site / hybrid / remote)

Resume attached.

Shubham Bhati
{config['phone']} | {config['linkedin']}"""

    elif tier == "TIER2":
        body = f"""Hi {name},

Java Backend Engineer | 2+ yrs | Immediate Joiner | Gurgaon

Currently at AlignBits, working on Justransform — enterprise B2B
integration platform serving 10+ clients.

My contributions:
  - Client-facing features and bug fixes
  - New protocol modules added
  - Dev and prod deployments, server monitoring
  - Previously: Healthcare backend at IHX

Tech: Java, Spring Boot, Microservices, REST APIs, MySQL, Docker, JWT
Notice Period: Immediate Joiner
Location: Gurgaon (on-site / hybrid / remote)

Resume attached — happy to connect if there's a relevant opening.

Shubham Bhati
{config['phone']} | {config['linkedin']}"""

    elif tier == "TIER4":
        body = f"""Hi {name},

I'm Shubham Bhati — Java Backend Engineer with 2+ years experience,
looking for Java Backend / Software Engineer roles.

Tech: Java, Spring Boot, Microservices, REST APIs, MySQL, Docker, JWT
Current: Enterprise B2B integration platform (Justransform/AlignBits)
Previous: Healthcare backend (IHX)

Notice Period: Immediate Joiner
Location: Gurgaon (on-site / hybrid / remote)

Resume attached.

Shubham Bhati
{config['phone']} | {config['linkedin']}"""

    else:
        body = f"""Hi {name},

Java Backend Engineer | 2+ yrs | Immediate Joiner | Gurgaon

Currently at AlignBits — enterprise B2B integration platform.
Previously: Healthcare backend at IHX.

Tech: Java, Spring Boot, Microservices, REST APIs, MySQL, Docker, JWT
Notice Period: Immediate Joiner
Location: Gurgaon (flexible)

Resume attached — please consider if {company} has relevant openings.

Shubham Bhati
{config['phone']} | {config['linkedin']}"""

    return body


def get_html_body(contact, config):
    """Generate HTML version of the email for better formatting."""
    raw_name = contact["name"].strip()
    name = raw_name.split()[0] if raw_name and raw_name.lower() not in ["hr", "team", "hr team"] else "Team"
    company = contact["company"]
    tier = contact["tier"]

    if tier == "TIER1":
        html = f"""<html>
<body style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6;">
<p>Hi {name},</p>

<p><strong>Java Backend Engineer | 2+ yrs | Immediate Joiner | Gurgaon</strong></p>

<p>Currently at AlignBits, working on <strong>Justransform</strong> — an enterprise B2B integration platform serving <strong>10+ clients</strong> across REST, SFTP, AS2, SOAP.</p>

<p><strong>My contributions:</strong></p>
<ul>
<li>Delivered client-facing features and bug fixes</li>
<li>Added new protocol modules (AS2)</li>
<li>Java migration (11→17), dev and prod deployments</li>
<li>Server monitoring — alarms, cron jobs, scheduled tasks</li>
<li>Previously: Healthcare backend at IHX</li>
<li>Side project: Built and launched a live e-commerce platform end-to-end (backend, admin panel, payments, deployment) &rarr; <a href="https://maakaalicreations.in" style="color: #1a73e8;">maakaalicreations.in</a></li>
</ul>

<table style="border-collapse: collapse; margin: 8px 0;">
<tr><td style="padding: 3px 12px 3px 0; color: #666;"><strong>Tech</strong></td><td style="padding: 3px 0;">Java, Spring Boot, Microservices, REST APIs, MySQL, Docker, JWT</td></tr>
<tr><td style="padding: 3px 12px 3px 0; color: #666;"><strong>Notice Period</strong></td><td style="padding: 3px 0;">Immediate Joiner</td></tr>
<tr><td style="padding: 3px 12px 3px 0; color: #666;"><strong>Location</strong></td><td style="padding: 3px 0;">Gurgaon (on-site / hybrid / remote)</td></tr>
</table>

<p>Resume attached.</p>

<p>
<strong>Shubham Bhati</strong><br>
{config['phone']} | <a href="https://{config['linkedin']}" style="color: #1a73e8;">LinkedIn</a>
</p>
</body>
</html>"""

    elif tier == "TIER2":
        html = f"""<html>
<body style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6;">
<p>Hi {name},</p>

<p><strong>Java Backend Engineer | 2+ yrs | Immediate Joiner | Gurgaon</strong></p>

<p>Currently at AlignBits, working on <strong>Justransform</strong> — enterprise B2B integration platform serving <strong>10+ clients</strong>.</p>

<ul>
<li>Client-facing features and bug fixes</li>
<li>New protocol modules added</li>
<li>Dev and prod deployments, server monitoring</li>
<li>Previously: Healthcare backend at IHX</li>
</ul>

<table style="border-collapse: collapse; margin: 8px 0;">
<tr><td style="padding: 3px 12px 3px 0; color: #666;"><strong>Tech</strong></td><td style="padding: 3px 0;">Java, Spring Boot, Microservices, REST APIs, MySQL, Docker, JWT</td></tr>
<tr><td style="padding: 3px 12px 3px 0; color: #666;"><strong>Notice Period</strong></td><td style="padding: 3px 0;">Immediate Joiner</td></tr>
<tr><td style="padding: 3px 12px 3px 0; color: #666;"><strong>Location</strong></td><td style="padding: 3px 0;">Gurgaon (on-site / hybrid / remote)</td></tr>
</table>

<p>Resume attached &mdash; happy to connect if there's a relevant opening.</p>

<p>
<strong>Shubham Bhati</strong><br>
{config['phone']} | <a href="https://{config['linkedin']}" style="color: #1a73e8;">LinkedIn</a>
</p>
</body>
</html>"""

    elif tier == "TIER4":
        html = f"""<html>
<body style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6;">
<p>Hi {name},</p>

<p>I'm <strong>Shubham Bhati</strong> — Java Backend Engineer with 2+ years experience, looking for Java Backend / Software Engineer roles.</p>

<table style="border-collapse: collapse; margin: 8px 0;">
<tr><td style="padding: 3px 12px 3px 0; color: #666;"><strong>Tech</strong></td><td style="padding: 3px 0;">Java, Spring Boot, Microservices, REST APIs, MySQL, Docker, JWT</td></tr>
<tr><td style="padding: 3px 12px 3px 0; color: #666;"><strong>Current</strong></td><td style="padding: 3px 0;">Enterprise B2B integration platform (Justransform/AlignBits)</td></tr>
<tr><td style="padding: 3px 12px 3px 0; color: #666;"><strong>Previous</strong></td><td style="padding: 3px 0;">Healthcare backend (IHX)</td></tr>
<tr><td style="padding: 3px 12px 3px 0; color: #666;"><strong>Notice Period</strong></td><td style="padding: 3px 0;">Immediate Joiner</td></tr>
<tr><td style="padding: 3px 12px 3px 0; color: #666;"><strong>Location</strong></td><td style="padding: 3px 0;">Gurgaon (on-site / hybrid / remote)</td></tr>
</table>

<p>Resume attached.</p>

<p>
<strong>Shubham Bhati</strong><br>
{config['phone']} | <a href="https://{config['linkedin']}" style="color: #1a73e8;">LinkedIn</a>
</p>
</body>
</html>"""

    else:
        html = f"""<html>
<body style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.6;">
<p>Hi {name},</p>

<p><strong>Java Backend Engineer | 2+ yrs | Immediate Joiner | Gurgaon</strong></p>

<p>Currently at AlignBits — enterprise B2B integration platform. Previously: Healthcare backend at IHX.</p>

<table style="border-collapse: collapse; margin: 8px 0;">
<tr><td style="padding: 3px 12px 3px 0; color: #666;"><strong>Tech</strong></td><td style="padding: 3px 0;">Java, Spring Boot, Microservices, REST APIs, MySQL, Docker, JWT</td></tr>
<tr><td style="padding: 3px 12px 3px 0; color: #666;"><strong>Notice Period</strong></td><td style="padding: 3px 0;">Immediate Joiner</td></tr>
<tr><td style="padding: 3px 12px 3px 0; color: #666;"><strong>Location</strong></td><td style="padding: 3px 0;">Gurgaon (flexible)</td></tr>
</table>

<p>Resume attached &mdash; please consider if <strong>{company}</strong> has relevant openings.</p>

<p>
<strong>Shubham Bhati</strong><br>
{config['phone']} | <a href="https://{config['linkedin']}" style="color: #1a73e8;">LinkedIn</a>
</p>
</body>
</html>"""

    return html


def send_email(contact, config, preview=False):
    """Send a single personalized email with resume attached."""
    subject = config["subject_template"].replace("{company}", contact["company"])
    plain_body = get_email_body(contact, config)
    html_body = get_html_body(contact, config)

    if preview:
        print(f"\n{'='*70}")
        print(f"TO: {contact['name']} <{contact['email']}>")
        print(f"SUBJECT: {subject}")
        print(f"TIER: {contact['tier']} | COMPANY: {contact['company']}")
        print(f"{'='*70}")
        print(plain_body)
        print(f"{'='*70}\n")
        return True

    msg = MIMEMultipart("alternative")
    msg["From"] = f"{config['sender_name']} <{config['sender_email']}>"
    msg["To"] = contact["email"]
    msg["Subject"] = subject

    # Attach plain text and HTML versions
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # Attach resume
    resume_path = config["resume_path"]
    if os.path.exists(resume_path):
        with open(resume_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="Shubham_Bhati_Resume.pdf"',
            )
            msg.attach(part)
    else:
        print(f"  [WARNING] Resume not found at: {resume_path}")

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(config["sender_email"], config["app_password"])
        server.sendmail(config["sender_email"], contact["email"], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to send to {contact['email']}: {e}")
        return False


def show_status(csv_path, log_path):
    """Show current sending progress."""
    total = {"TIER1": 0, "TIER2": 0, "TIER3": 0, "TIER4": 0}
    sent = {"TIER1": 0, "TIER2": 0, "TIER3": 0, "TIER4": 0}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tier = row["tier"]
            total[tier] = total.get(tier, 0) + 1
            if row["sent"].strip().upper() == "YES":
                sent[tier] = sent.get(tier, 0) + 1

    today_count = get_sent_today(log_path)

    print("\n" + "=" * 50)
    print("  EMAIL CAMPAIGN STATUS")
    print("=" * 50)
    for tier in ["TIER1", "TIER2", "TIER3", "TIER4"]:
        remaining = total[tier] - sent[tier]
        pct = (sent[tier] / total[tier] * 100) if total[tier] > 0 else 0
        bar = "#" * int(pct / 5) + "-" * (20 - int(pct / 5))
        print(f"  {tier}: [{bar}] {sent[tier]}/{total[tier]} sent ({pct:.0f}%)")

    total_all = sum(total.values())
    sent_all = sum(sent.values())
    print(f"\n  TOTAL: {sent_all}/{total_all} sent")
    print(f"  Sent today: {today_count}")
    print(f"  Remaining: {total_all - sent_all}")
    print("=" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(description="HR Cold Email Sender Tool")
    parser.add_argument("--count", type=int, help="Number of emails to send (overrides config)")
    parser.add_argument("--tier", choices=["TIER1", "TIER2", "TIER3", "TIER4"], help="Send only to specific tier")
    parser.add_argument("--preview", action="store_true", help="Preview emails without sending")
    parser.add_argument("--status", action="store_true", help="Show sending progress")
    parser.add_argument("--test", action="store_true", help="Send test email to yourself")
    args = parser.parse_args()

    config = load_config()
    csv_path = os.path.join(SCRIPT_DIR, config["contacts_csv"])
    log_path = os.path.join(SCRIPT_DIR, config["sent_log"])

    # Show status
    if args.status:
        show_status(csv_path, log_path)
        return

    # Test mode — send to yourself
    if args.test:
        test_contact = {
            "name": "Shubham (Test)",
            "email": config["sender_email"],
            "company": "Test Company Pvt Ltd",
            "title": "HR Head",
            "tier": "TIER1",
        }
        print("\n[TEST MODE] Sending test email to yourself...")
        success = send_email(test_contact, config)
        if success:
            print("[OK] Test email sent! Check your inbox.\n")
        else:
            print("[FAILED] Could not send test email. Check your app password.\n")
        return

    # Check daily limit
    today_sent = get_sent_today(log_path)
    daily_limit = args.count or config["daily_limit"]
    remaining_today = daily_limit - today_sent

    if remaining_today <= 0 and not args.preview:
        print(f"\n[LIMIT] Already sent {today_sent} emails today. Daily limit: {daily_limit}")
        print("Try again tomorrow or increase daily_limit in config.json\n")
        return

    # Get pending contacts
    already_sent = get_all_sent_emails(log_path)
    pending = get_pending_contacts(csv_path, args.tier)
    # Filter out already sent (in case CSV wasn't updated)
    pending = [c for c in pending if c["email"].lower() not in already_sent]

    if not pending:
        print("\n[DONE] All contacts have been emailed! No pending contacts.\n")
        show_status(csv_path, log_path)
        return

    batch_size = remaining_today if not args.preview else min(5, len(pending))
    batch = pending[:batch_size]

    print(f"\n{'='*50}")
    if args.preview:
        print(f"  PREVIEW MODE — Showing {len(batch)} emails")
    else:
        print(f"  SENDING {len(batch)} EMAILS")
        print(f"  Sent today: {today_sent} | Limit: {daily_limit}")
    print(f"  Pending: {len(pending)} | Tier filter: {args.tier or 'ALL'}")
    print(f"{'='*50}\n")

    sent_count = 0
    for i, contact in enumerate(batch, 1):
        tier_label = contact["tier"]
        print(f"  [{i}/{len(batch)}] {tier_label} | {contact['company']} | {contact['name']} | {contact['email']}")

        success = send_email(contact, config, preview=args.preview)

        if success and not args.preview:
            log_sent(log_path, contact, "SENT")
            update_contacts_csv(csv_path, contact["email"])
            sent_count += 1
            print(f"           [OK] Sent successfully")

            # Delay between emails
            if i < len(batch):
                delay = config["delay_between_emails_seconds"]
                print(f"           Waiting {delay}s before next email...")
                time.sleep(delay)
        elif not success and not args.preview:
            log_sent(log_path, contact, "FAILED")
            print(f"           [FAILED] Could not send")

    if not args.preview:
        print(f"\n{'='*50}")
        print(f"  BATCH COMPLETE: {sent_count}/{len(batch)} sent successfully")
        print(f"{'='*50}\n")
        show_status(csv_path, log_path)


if __name__ == "__main__":
    main()
