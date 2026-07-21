# 🧠 Adaptive Emotional Ecosystem (AEE)

<div align="center">

![AEE Platform](https://img.shields.io/badge/AEE-Adaptive%20Emotional%20Ecosystem-5b8ef0?style=for-the-badge)
![Course](https://img.shields.io/badge/Course-CSE307%20System%20Analysis%20%26%20Design-7c6ff7?style=for-the-badge)
![Semester](https://img.shields.io/badge/Semester-Spring%202026-22d3a5?style=for-the-badge)
![Group](https://img.shields.io/badge/Group-05%20%7C%20Section%2001-f0b429?style=for-the-badge)

**A non-clinical, privacy-first emotional well-being platform for university students.**  
No diagnoses. No physical sensors. Just thoughtful, adaptive care.

[🚀 Quick Start](#-quick-start) · [📐 Architecture](#-architecture) · [🔗 API Docs](#-api-endpoints) · [🖥️ Dashboards](#️-dashboards) · [👥 Team](#-team)

</div>

---

## 📖 About

The **Adaptive Emotional Ecosystem (AEE)** is a full-stack web platform designed to support the emotional well-being of university students. It collects anonymous mood data, runs rule-based risk analysis, and delivers personalized micro-interventions — all without clinical diagnosis, physical sensors, or storing personally identifiable information.

Built as a final group project for **CSE307 — System Analysis and Design** at **Independent University, Bangladesh (IUB)**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **Secure Authentication** | JWT-based login for 5 distinct user roles |
| 😊 **Mood Check-In** | Students submit anonymous mood scores (1–10) with optional notes |
| 📊 **Risk Analysis** | Rule-based engine classifies mood as LOW / MODERATE / HIGH |
| 💡 **Micro-Interventions** | Instant personalized suggestions (breathing, focus tips, motivation) |
| ⚠️ **High-Risk Alerts** | Auto-notifications sent to counselors when HIGH risk is detected |
| 📈 **Mood Trends** | Charts of aggregated mood data over time |
| 📝 **Guidance Notes** | Counselors create, edit, delete professional guidance (full CRUD) |
| 🔔 **Notifications** | System alerts for counselors and advisors, with read/unread tracking |
| 🏛️ **Institutional Reports** | Anonymized campus-wide data for university management |
| 🛡️ **Admin Control** | Full user management (create, read, update, delete all roles) |
| 🔒 **Privacy First** | All student data stored with anonymous IDs, never identifiable |

---

## 🏗️ Architecture

```
aee_project/
│
├── backend/                          ← Python (FastAPI) — single unified backend
│   ├── main.py                       ← Entry point — registers all 8 routers
│   ├── requirements.txt
│   ├── .env.example
│   ├── seed_demo_users.py            ← Creates demo accounts for all 5 roles
│   │
│   └── app/
│       ├── core/
│       │   ├── config.py             ← Settings (SQLite default, PostgreSQL optional)
│       │   ├── security.py           ← PBKDF2-SHA256 hashing + JWT tokens
│       │   └── deps.py               ← Auth guards: get_current_user, require_roles()
│       │
│       ├── db/
│       │   └── database.py           ← SQLAlchemy engine (SQLite/PostgreSQL)
│       │
│       ├── models/                   ← Database tables (match Class Diagram)
│       │   ├── student.py            ← Unified users table (all 5 roles)
│       │   ├── emotion_data.py       ← EmotionData class
│       │   ├── risk_analysis.py      ← RiskAnalysis class
│       │   ├── intervention.py       ← Intervention class
│       │   ├── report.py             ← Report class
│       │   ├── guidance.py           ← GuidanceNote (counselor notes — CRUD)
│       │   └── notification.py       ← System notifications
│       │
│       ├── schemas/                  ← Pydantic request/response validation
│       │   ├── student.py
│       │   ├── emotion.py
│       │   └── counselor.py
│       │
│       ├── services/                 ← Business logic layer
│       │   ├── risk_engine.py        ← Rule-based LOW/MODERATE/HIGH analysis
│       │   └── report_service.py     ← Aggregated reports + weekly trends
│       │
│       └── api/routes/               ← REST API endpoints (8 routers)
│           ├── auth.py               ← /auth/register  /auth/login  /auth/me
│           ├── mood.py               ← /mood/submit  /history  PUT  DELETE
│           ├── counselor.py          ← /counselor/alerts  /guidance (CRUD)
│           ├── reports.py            ← /reports/aggregated  /weekly-trend
│           ├── management.py         ← /management/summary  /monthly  /departments
│           ├── notifications.py      ← /notifications/ (CRUD + read/unread)
│           ├── admin.py              ← /api/admin/users (CRUD)  /metrics
│           └── ui.py                 ← Serves all HTML pages
│
└── frontend/                         ← HTML + CSS + JavaScript (no framework)
    └── templates/
        ├── login.html                ← Role-based login (5 roles)
        ├── register.html             ← Account creation
        ├── student/dashboard.html    ← Mood check-in, history, goals, breathing
        ├── counselor/dashboard.html  ← Alerts, trends, guidance CRUD, notifications
        ├── admin/dashboard.html      ← Full user CRUD, system metrics, service status
        └── management/dashboard.html ← Campus overview, monthly report, departments
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | FastAPI (Python) | REST API, routing, middleware |
| **Database** | SQLite (default) / PostgreSQL | Data persistence |
| **ORM** | SQLAlchemy | Database models and queries |
| **Authentication** | JWT (python-jose) | Token-based auth for all roles |
| **Password Hashing** | PBKDF2-HMAC-SHA256 | Secure password storage |
| **Validation** | Pydantic v2 | Request/response schema validation |
| **Frontend** | HTML5 + CSS3 + Vanilla JS | No framework — pure web standards |
| **Charts** | Chart.js 4.4 | Bar, line, doughnut visualizations |
| **Report Gen** | ReportLab / openpyxl | PDF and Excel report exports |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- No other dependencies needed (SQLite is built-in)

### 1. Clone the repository
```bash
git clone https://github.com/your-username/aee-platform.git
cd aee-platform
```

### 2. Install Python dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure environment (optional — SQLite works with zero config)
```bash
cp .env.example .env
# Edit .env if you want to change settings
```

### 4. Seed demo accounts
```bash
python seed_demo_users.py
```

This creates one demo account per role:

| Role | Email | Password |
|---|---|---|
| 🎓 Student | `student@aee.edu` | `demo1234` |
| 💚 Counselor | `counselor@aee.edu` | `demo1234` |
| 💜 Advisor | `advisor@aee.edu` | `demo1234` |
| 🛡️ Admin | `admin@aee.edu` | `demo1234` |
| 🏛️ Management | `management@aee.edu` | `demo1234` |

### 5. Run the server
```bash
uvicorn main:app --reload
```

| URL | Purpose |
|---|---|
| `http://localhost:8000` | Redirects to login page |
| `http://localhost:8000/ui/login` | Login page |
| `http://localhost:8000/docs` | Interactive Swagger API docs |
| `http://localhost:8000/health` | Health check |

---

## 🔗 API Endpoints

### Authentication (Public)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Create a new account (any role) |
| `POST` | `/auth/login` | Login → returns JWT token |
| `GET` | `/auth/me` | Get current user profile |

### Mood Tracking (Student + Staff)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/mood/submit` | Submit mood check-in → returns intervention |
| `GET` | `/mood/history` | Fetch mood history (students see own only) |
| `PUT` | `/mood/{id}` | Update a check-in (re-runs risk engine) |
| `DELETE` | `/mood/{id}` | Delete a check-in (cascades) |

### Counselor / Advisor
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/counselor/alerts` | High-risk alerts (anonymized) |
| `GET` | `/counselor/guidance` | List all guidance notes |
| `POST` | `/counselor/guidance` | Create guidance note |
| `PUT` | `/counselor/guidance/{id}` | Edit own guidance note |
| `DELETE` | `/counselor/guidance/{id}` | Delete own guidance note |

### Reports (Staff Roles)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/reports/aggregated` | Campus-wide anonymized statistics |
| `GET` | `/reports/weekly-trend` | Daily average mood last 7 days |

### University Management
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/management/summary` | Campus well-being snapshot |
| `GET` | `/management/monthly-report` | Last 30 days detailed breakdown |
| `GET` | `/management/departments` | Mood by academic department |

### Notifications (Staff Roles)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/notifications/` | List all notifications for my role |
| `GET` | `/notifications/unread` | Unread count (for badge) |
| `PUT` | `/notifications/{id}/read` | Mark one as read |
| `PUT` | `/notifications/read-all` | Mark all as read |
| `DELETE` | `/notifications/{id}` | Delete a notification |

### Admin Only
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/admin/users` | List all users (all roles) |
| `POST` | `/api/admin/users` | Create user (any role) |
| `PUT` | `/api/admin/users/{id}` | Edit user (name, role, department) |
| `DELETE` | `/api/admin/users/{id}` | Delete user |
| `GET` | `/api/admin/metrics` | System-wide metrics |

---

## 🔒 Role-Based Access Control

| Endpoint Group | Student | Counselor / Advisor | Admin | Management |
|---|:---:|:---:|:---:|:---:|
| `/mood/submit` | ✅ | ✅ | ✅ | ❌ |
| `/mood/history` | ✅ own | ✅ all | ✅ all | ❌ |
| `/counselor/*` | ❌ | ✅ | ✅ | ❌ |
| `/reports/*` | ❌ | ✅ | ✅ | ✅ |
| `/management/*` | ❌ | ❌ | ✅ | ✅ |
| `/notifications/*` | ❌ | ✅ | ✅ | ❌ |
| `/api/admin/*` | ❌ | ❌ | ✅ | ❌ |
| `/auth/me` | ✅ | ✅ | ✅ | ✅ |

All enforcement is done via `app/core/deps.py → require_roles(...)` — a single reusable FastAPI dependency.

---

## 🖥️ Dashboards

### 🎓 Student Dashboard
- Mood check-in (1–10 scale with emoji feedback)
- Real-time intervention message based on risk level
- Session mood history bar chart
- Personal mood trend (from backend)
- Daily goals tracker (check-in, score ≥ 6, breathing, notes)
- Full check-in history table with Edit / Delete
- Guided box-breathing exercise with animated timer
- Wellness resources panel

### 💚 Counselor / Advisor Dashboard
- Campus risk overview (High / Moderate / Low counts)
- Anonymized high-risk student alerts (by anonymous ID only)
- Weekly mood trend chart (live from backend)
- Guidance notes — full CRUD (create, view, edit, delete)
- System notifications with read/unread state
- Aggregated institutional report

### 🛡️ Admin Dashboard
- System-wide metrics (users, logs, risk breakdown)
- Role distribution chart
- Complete user management — full CRUD with search/filter
- Create users for any role
- Service health status (FastAPI, SQLite, Risk Engine, Auth)
- API endpoint status table
- Security log
- Weekly DAU chart

### 🏛️ University Management Dashboard
- Campus well-being snapshot (students, avg mood, participation, interventions)
- Risk distribution doughnut chart
- Monthly institutional report (last 30 days)
- Department mood breakdown (horizontal bar chart)
- Well-being trends (live line chart)
- Privacy compliance and uptime gauges
- Export report button

---

## 🗂️ Database Schema

```
students              ← All users (5 roles in one table)
  └── emotion_data    ← Mood check-ins (FK: students.id)
      └── risk_analysis  ← Risk levels (FK: emotion_data.id)
          └── interventions  ← Suggestions (FK: risk_analysis.id)

guidance_notes        ← Counselor notes (FK: counselor_id → students.id)
notifications         ← System alerts (role-targeted, not user-targeted)
reports               ← Generated report metadata
```

---

## 🔄 Assignment Mapping

| Assignment Section | Code Location |
|---|---|
| Class Diagram (6 classes) | `backend/app/models/` |
| DFD Level-0 (Context Diagram) | `main.py` + CORS config |
| DFD Level-1 (5 processes) | `app/api/routes/mood.py` comments |
| Sequence Diagram (12 steps) | `app/api/routes/mood.py` step comments |
| RiskAnalysis.analyzeEmotionData() | `app/services/risk_engine.py` |
| Report.generateReport() | `app/services/report_service.py` |
| Micro-Intervention (Activity Diagram) | `mood.py` step 3 |
| Use Case: Submit Mood | `POST /mood/submit` |
| Use Case: High-Risk Alert | `POST /counselor/alerts` + auto-notifications |
| Use Case: Register | `POST /auth/register` |
| Use Case: Generate Report | `GET /reports/aggregated` |
| Deployment Diagram (3 layers) | Client → FastAPI → SQLite |

---

## 🌐 Switching to PostgreSQL

SQLite is the default (zero setup). To switch to PostgreSQL:

```bash
# 1. Install driver
pip install psycopg2-binary

# 2. Create database
psql -U postgres
CREATE DATABASE aee_db;
CREATE USER aee_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE aee_db TO aee_user;

# 3. Update .env
DATABASE_URL=postgresql://aee_user:yourpassword@localhost:5432/aee_db
```

No code changes needed — `database.py` handles both automatically.

---

## 👥 Team

**CSE307 — System Analysis and Design | Section 01 | Group 05 | Spring 2026**  
**Independent University, Bangladesh (IUB)**

| Contribution | Name | Student ID |
|:---:|---|:---:|
| 25% | Raisa Tafannum | 2211425 |
| 25% | Tasnia Anjum | 2321147 |
| 25% | Jugumaya Saha Disha | 2320434 |
| 25% | Israt Jahan Samanta | 2320481 |

---

## 📜 License

This project was created for academic purposes at Independent University, Bangladesh.  
© 2026 CSE307 Group 05. All rights reserved.

---

<div align="center">

**Built with 💙 by Group 05 · CSE307 · IUB · Spring 2026**

*"Teacheth man that which he knew not"*

</div>
