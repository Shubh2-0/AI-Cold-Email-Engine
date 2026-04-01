"""
Auto Email Runner
- Runs on PC startup
- Checks if today is Tuesday/Wednesday/Thursday
- Checks if emails already sent today
- If not, waits until 9:30 AM and sends batch
"""

import subprocess
import sys
import os
import time
from datetime import datetime, date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SENT_LOG = os.path.join(SCRIPT_DIR, "sent_log.csv")
EMAIL_SCRIPT = os.path.join(SCRIPT_DIR, "email_sender.py")

SEND_DAYS = [1, 2, 3]  # Tuesday=1, Wednesday=2, Thursday=3
SEND_HOUR = 9
SEND_MINUTE = 30


def already_sent_today():
    today = date.today().isoformat()
    if not os.path.exists(SENT_LOG):
        return False
    with open(SENT_LOG, "r", encoding="utf-8") as f:
        for line in f:
            if today in line:
                return True
    return False


def main():
    now = datetime.now()
    day = now.weekday()  # Monday=0, Tuesday=1, ...

    if day not in SEND_DAYS:
        print(f"Today is not a sending day (Tue/Wed/Thu). Exiting.")
        return

    if already_sent_today():
        print(f"Emails already sent today. Exiting.")
        return

    # Wait until 9:30 AM if before
    target = now.replace(hour=SEND_HOUR, minute=SEND_MINUTE, second=0)
    if now < target:
        wait = (target - now).total_seconds()
        print(f"Waiting until 9:30 AM... ({int(wait//60)} minutes)")
        time.sleep(wait)

    # If after 2 PM, skip (too late)
    if datetime.now().hour >= 14:
        print("Too late today (after 2 PM). Skipping.")
        return

    print("Starting email batch...")
    subprocess.run([sys.executable, EMAIL_SCRIPT, "--count", "25"])


if __name__ == "__main__":
    main()
