<div align="center">
  <img src="banner.png" alt="Banner" width="80%" height="80%" style="object-fit: cover; border-radius: 12px;"/>
  
  <br><br>
  
  <h1>✉️ Automated Cold Email Engine</h1>
  <i>A High-Performance Python Scripting Pipeline for Outreach Automation</i>
  <br><br>

  <p>
    <img src="https://img.shields.io/badge/Python_3-3776AB?style=for-the-badge&logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" />
    <img src="https://img.shields.io/badge/Automation-FF9900?style=for-the-badge&logo=opslevel&logoColor=white" />
  </p>
</div>

<br>

## 📖 Executive Summary
Designed as a utility for highly scalable tech outreach, this **Python-based Mail Engine** eliminates manual networking by orchestrating asynchronous email processing. It parses dynamic data from CSV contacts and JSON configurations to dispatch bulk personalized communication while navigating rigid SMTP provider limitations.

---

## ⚡ Core Architecture & Engineering
> *Built with functional programming practices and secure OS-level credential management.*

- **Data Aggregation & Mapping:** Dynamically parses lead data from `contacts.csv` and injects contextual variables into templates defined in `config.json`.
- **Zero-Trust Secret Management:** Avoids hard-coded leaks entirely. Relies strictly on `.env` injection at the OS level and `GitHub Secrets` integration for continuous cloud actions.
- **Automated Logging:** Maintains a continuous state machine via `sent_log.csv` to ensure resilient execution and prevent duplicate messaging during unexpected timeouts.
- **Throttling Engine:** Replicates human sending-patterns using time delays to protect domain reputation and prevent IP/SMTP bans.

---

## 🛠️ The Tech Stack Detail
| Layer | Technologies used | Justification |
| --- | --- | --- |
| **Language Engine** | `Python 3` | Leveraging Python's massive capability for data parsing and SMTP integration. |
| **Data Parsing** | `CSV & JSON` | Lightweight data tracking for non-volatile storage without requiring heavy DBs. |
| **CI/CD & DevOps**| `GitHub Actions` & `auto_runner.py` | Automated CRON triggers allowing the code to run in the cloud entirely hands-free. |

---

## 🚀 How to Execute Locally

<details>
  <summary><b>Click to expand deployment steps</b></summary>
  
  <br/>
  
  1. **Clone the Source Code**
     ```bash
     git clone https://github.com/Shubh2-0/cold-email-automation.git
     ```
  2. **Set the Config Files**
     Ensure `config.json` and `contacts.csv` mirror your target formats.
  3. **Provide Secrets**
     Ensure your SMTP email and App Password are provided securely.
  4. **Launch the Engine**
     ```bash
     python email_sender.py
     ```
</details>

<br>

<div align="center">
  <b>Built by Shubham Bhati</b> — <i>Software Engineer (Java/Python Backend)</i>
</div>
