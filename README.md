🛡️ Email & Link Security Analyzer

<p align="center">
  <b>A Flask-based cybersecurity application for detecting potential phishing threats in emails and URLs.</b>
</p>

<p align="center">
  Analyze • Detect • Score • Investigate
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-000000?style=for-the-badge\&logo=flask\&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge\&logo=sqlite\&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-Frontend-E34F26?style=for-the-badge\&logo=html5\&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-Frontend-F7DF1E?style=for-the-badge\&logo=javascript\&logoColor=black)
![CSS3](https://img.shields.io/badge/CSS3-Styling-1572B6?style=for-the-badge\&logo=css3\&logoColor=white)

</p>

---

🔎 Overview

**Email & Link Security Analyzer** is a web-based cybersecurity application that helps identify potentially malicious emails and URLs using rule-based phishing detection techniques.

The system analyzes submitted content, identifies suspicious indicators, calculates a **risk score**, and classifies the result into a threat level.

It was developed to demonstrate practical knowledge of:

* 🐍 Python application development
* 🌐 Flask web development
* 🔐 Authentication and session management
* 🗄️ Database integration
* 📁 File parsing and processing
* 🛡️ Phishing detection concepts
* 📊 Risk scoring
* 🧩 Modular application architecture

> **Note:** This project uses heuristic/rule-based analysis and should not be considered a replacement for enterprise-grade threat intelligence or antivirus systems.

---

✨ Key Features

| Feature                      | Description                                           |
| ---------------------------- | ----------------------------------------------------- |
| 🔐 **User Authentication**   | Registration, login, logout and session management    |
| 📧 **Email Analysis**        | Analyze email content for phishing indicators         |
| 🔗 **URL Analysis**          | Detect suspicious characteristics in links            |
| 📁 **File Analysis**         | Process supported email and document formats          |
| 🎯 **Risk Scoring**          | Calculate a threat score based on detected indicators |
| 🚦 **Threat Classification** | Categorize results from Safe to Critical              |
| 📊 **Analysis Results**      | Present detected indicators and security findings     |
| 🕒 **Analysis History**      | Maintain previous analysis records                    |
| 🗃️ **SQLite Database**      | Store application and user data                       |
| 📝 **Application Logging**   | Maintain application activity logs                    |

---

🧠 How It Works

The application follows a simple security-analysis pipeline:

```text
                         USER INPUT
                             │
               ┌─────────────┴─────────────┐
               │                           │
             EMAIL                        URL
               │                           │
               └─────────────┬─────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Input Parsing  │
                    └────────┬────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │ Suspicious Indicator  │
                 │      Detection        │
                 └───────────┬───────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
          Keywords          URLs         Patterns
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌─────────────────┐
                    │   Risk Scoring  │
                    └────────┬────────┘
                             │
                             ▼
                  ┌────────────────────┐
                  │ Threat Classification│
                  └─────────┬──────────┘
                            │
                            ▼
                    SECURITY REPORT
```

---

🚦 Threat Classification

The analyzer converts detected indicators into an overall risk level.

```text
┌─────────────────────────────────────────────┐
│              THREAT LEVELS                  │
├─────────────────────────────────────────────┤
│                                             │
│   🟢 SAFE        → Minimal indicators       │
│   🟡 LOW         → Low-risk indicators      │
│   🟠 MEDIUM      → Multiple warning signs   │
│   🔴 HIGH        → Strong phishing signals  │
│   🚨 CRITICAL    → Severe risk indicators   │
│                                             │
└─────────────────────────────────────────────┘
```

Examples of suspicious indicators include:

* Urgent or threatening language
* Requests for credentials
* Suspicious links
* Account-verification requests
* Prize/reward scams
* Unusual URLs
* Social-engineering patterns
* Suspicious keywords

---

🏗️ System Architecture

```text
                         ┌────────────────────┐
                         │      Browser       │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │    Flask Server    │
                         │      app.py        │
                         └─────────┬──────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
       ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
       │    Auth     │      │   Parsers   │      │   Analyzer  │
       │  auth.py    │      │ parsers.py  │      │ analyzer.py │
       └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │   SQLite Database  │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │ Analysis Results   │
                         │ Risk / Indicators  │
                         └────────────────────┘
```

---

# 📂 Project Structure

```text
Email-Link-Security-Analyzer/
│
├── app.py                     # Flask application entry point
├── config.py                  # Application configuration
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── .gitignore                 # Git ignored files
│
├── src/
│   ├── __init__.py
│   ├── auth.py                # Authentication logic
│   ├── analyzer.py            # Phishing analysis engine
│   └── parsers.py             # File/content parsing
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── results.html
│   └── history.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
└── data/
    ├── test_emails.csv
    ├── test_emails.json
    ├── test_emails.txt
    ├── test_links.csv
    └── link.txt
```

---

🛠️ Tech Stack

 Backend

* **Python**
* **Flask**
* **Werkzeug**

Frontend

* **HTML5**
* **CSS3**
* **JavaScript**
* Database

* **SQLite**
Development Tools

* **VS Code**
* **Git**
* **GitHub**

---

⚙️ Getting Started

1. Clone the Repository

```bash
git clone https://github.com/gunasagar123/Email-Link-Security-Analyzer.git
```

```bash
cd Email-Link-Security-Analyzer
```

---

 2. Create a Virtual Environment

Windows

```bash
python -m venv venv
```

Activate:

```bash
venv\Scripts\activate
```

 macOS / Linux

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

---

3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

4. Run the Application

```bash
python app.py
```

The application will start locally at:

```text
http://127.0.0.1:5000
```

Open the URL in your browser.

---

 🧪 Testing

Sample test data is included in the `data/` directory.

```text
data/
├── test_emails.csv
├── test_emails.json
├── test_emails.txt
├── test_links.csv
└── link.txt
```

Suggested testing flow

```text
Login
  ↓
Dashboard
  ↓
Select Analysis
  ↓
Upload Test File / Submit URL
  ↓
Analyze
  ↓
Risk Score
  ↓
Threat Level
  ↓
View Results
  ↓
Analysis History
```

---

🔐 Security Design

The project incorporates several basic security practices:

* User authentication
* Password handling using Werkzeug utilities
* Session-based access control
* File validation
* Controlled file processing
* Input analysis
* Application logging
* Separation of authentication, parsing and analysis logic

 Production Hardening

For production deployment, the application should additionally implement:

* Environment-based secret management
* HTTPS
* CSRF protection
* Rate limiting
* Stronger password hashing configuration
* Secure cookie configuration
* Upload size restrictions
* Malware scanning
* Input sanitization
* Production WSGI server
* Centralized logging
* Threat-intelligence integrations

---

📈 Future Improvements

The current rule-based engine can be extended into a more advanced phishing detection platform.

Planned Enhancements

* 🤖 Machine Learning phishing classification
* 🧠 NLP-based email analysis
* 🔗 URL reputation analysis
* 🌐 Domain and WHOIS intelligence
* 🛡️ Threat-intelligence API integration
* 📊 Advanced analytics dashboard
* 📄 Automated security reports
* 📧 Email-client integration
* 🔔 Real-time threat alerts
* 🐳 Docker support
* ☁️ Cloud deployment
* 🔑 Role-based access control
* 🔌 REST API

---

💡 Why This Project?

Phishing remains one of the most common forms of social engineering.

This project focuses on the **detection and analysis side of cybersecurity**, providing an understandable workflow for identifying suspicious characteristics in emails and URLs.

The project demonstrates how cybersecurity concepts can be combined with full-stack development to create a practical security-oriented application.

---

🎯 Learning Outcomes

Through this project, the following concepts were implemented and practiced:

```text
Python
   │
   ├── Flask Web Development
   ├── Authentication
   ├── File Processing
   ├── Regular Expressions
   ├── Risk Analysis
   │
   └── Cybersecurity
          │
          ├── Phishing Detection
          ├── URL Analysis
          └── Threat Classification

Database
   │
   └── SQLite

Frontend
   │
   ├── HTML
   ├── CSS
   └── JavaScript

Development
   │
   ├── Git
   └── GitHub
```

---



🚀 Project Highlights

> **Cybersecurity + Full-Stack Development**

| Area            | Implementation                       |
| --------------- | ------------------------------------ |
| Web Development | Flask + HTML/CSS/JavaScript          |
| Security        | Phishing detection and risk analysis |
| Backend         | Modular Python architecture          |
| Database        | SQLite                               |
| Authentication  | Login / Registration / Sessions      |
| Data Processing | Email, URL and file parsing          |
| Risk Engine     | Rule-based scoring                   |
| Version Control | Git + GitHub                         |

---

👨‍💻 Author

Padum Guna Sagar

**B.Tech – Computer Science & Engineering | Cybersecurity**

Interested in:

`Java` • `Python` • `Spring Boot` • `React` • `Cloud` • `Cybersecurity`

---

#📄 License

This project is intended for **educational, research, and authorized defensive-security purposes**.

Do not use this application to analyze or interact with systems, accounts, files, or communications without appropriate authorization.

---

<p align="center">
  <b>🛡️ Analyze. Detect. Understand. Secure.</b>
</p>

<p align="center">
  ⭐ If you find this project useful, consider starring the repository.
</p>
