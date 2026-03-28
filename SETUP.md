# HR Email Sender Tool — Setup Guide

## Step 1: Gmail App Password banao

Gmail direct password se kaam nahi karega. App Password banana padega:

1. Go to: https://myaccount.google.com/security
2. "2-Step Verification" ON karo (agar nahi hai)
3. Phir jao: https://myaccount.google.com/apppasswords
4. App name daalo: "Email Sender"
5. 16-digit password milega (e.g., `abcd efgh ijkl mnop`)
6. Wo password `config.json` mein `app_password` mein daalo (spaces hata ke)

## Step 2: config.json update karo

```json
{
    "app_password": "abcdefghijklmnop"  <-- yahan apna app password daalo
}
```

## Step 3: Commands

```bash
# Pehle test email bhejo (khud ko)
python email_sender.py --test

# Preview dekho (bina bheje)
python email_sender.py --preview

# Sirf TIER1 ko bhejo (highest match)
python email_sender.py --tier TIER1

# Aaj ke 30 emails bhejo
python email_sender.py

# Sirf 10 bhejo
python email_sender.py --count 10

# Progress dekho
python email_sender.py --status
```

## Best Time to Send (India)

- **Best Days:** Tuesday, Wednesday, Thursday
- **Best Time:** 9:00 AM - 11:00 AM IST
- **Avoid:** Monday morning (inbox flooded), Friday afternoon, Weekends

## Strategy

- Week 1: TIER1 (36 contacts) — 20/day
- Week 2-3: TIER2 (120 contacts) — 30/day
- Week 3-4: TIER3 (123 contacts) — 30/day
