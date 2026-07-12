# Odoo Hackathon 2026 - Team: 

Welcome to our team's repository for the Odoo Hackathon 2026 Online Round. 

## 🚀 Project Overview


AssetFlow is an Enterprise Asset & Resource Management System that helps organizations track, allocate, and maintain physical assets and shared resources — replacing manual spreadsheets and paper logs with a centralized, role-based platform.

Any organization with equipment, furniture, vehicles, or shared spaces (offices, schools, hospitals, factories, agencies) can use it to get real-time visibility into who holds what, where it is, and its condition.


 ## ? Features

- 🔐 Role-based authentication — self-signup creates employee accounts only; Admin/Manager/Dept Head roles are assigned by an Admin, never self-elevated

- 🏠 Live KPI dashboard — available/allocated/maintenance/overdue asset counts, active bookings, pending requests

- 📦 Asset registry — register assets with auto-generated tags, categories, condition, and location tracking

- 👥 Asset allocation & transfers — allocate assets to employees, with automatic conflict detection ("currently held by X") and a structured transfer request → approval workflow

- 🔧 Maintenance workflow — raise, approve, and resolve maintenance requests with automatic asset status updates

- 🏢 Organization setup — manage departments and asset categories (Admin only)

- 👤 User management — promote employees to Dept Head / Asset Manager / Admin (Admin only)

- 🔔 Notifications — per-user activity and alert feed


## 🛠️ Tech Stack
- *Frontend/Backend:* Streamlit (Python)
- *Database:* SQLite (Local)
- *AI Engine:* Groq API


## 👥 Team Members & Contributions
Every team member is tracking progress via individual hourly commits.
- *Jiya (Leader)* - Backend/Integration
- *Tanisha*- Frontend
- *Gyanesh* - Testing & debugging
- *Namrata*-Frontend

## 📁 Project Structure


odoo-hackathon-2026/
├── app.py              # Main entry point — login, signup, sidebar, routing
├── auth.py             # Authentication — signup, login, password hashing
├── db.py               # SQLite schema & connection handling
├── frontend.py         # All page views (dashboard, assets, allocations, etc.)
├── utils.py             # Business logic & DB queries
├── setup.py             # Seeds demo users for all 4 roles
├── data.db               # SQLite database (auto-generated, gitignored)
├── .env                 # Environment variables (gitignored)
└── requirements.txt


---


## ⚙️ How to Run the Project
1. Clone the repository:
   bash
   git clone https://github.com/jish-06/odoo-hackathon-2026.git


 2. Install dependencies

bash
pip install -r requirements.txt


3. Set up environment variables

Create a .env file in the project root:


GROQ_API_KEY=your_groq_api_key_here


 4. Seed demo accounts (recommended for first run)

bash
python setup.py


This creates the database tables and seeds one account per role:

| Role | Email | Password |
|---|---|---|
| Admin | admin@assetflow.com | admin@123 |
| Asset Manager | manager@assetflow.com | manager@123 |
| Dept Head | head@assetflow.com | head@123 |
| Employee | emp@assetflow.com | emp@123 |

You can re-run python setup.py anytime to reset back to these 4 clean accounts.

### 5. Run the app

bash
streamlit run app.py


The app opens at http://localhost:8501.

### 6. (Optional) Share with teammates on a different network

bash
ngrok http 8501

Send the generated https://...ngrok-free.app link to your team.


## 🔑 User Roles

| Role | Access |
|---|---|
| *Admin* | Full access — Organization Setup, User Management, all modules |
| *Asset Manager* | Registers/allocates assets, approves maintenance & transfers |
| *Dept Head* | Views department allocations, approves department-level requests |
| *Employee* | Views assigned assets, raises maintenance requests, requests transfers |



# ??? Asset Lifecycle

text
Available
    ¦
    ?
Allocated
    ¦
    ?
Reserved
    ¦
    ?
Under Maintenance
    ¦
    ?
Available

Other States:
Lost
Retired
Disposed
```

---

# ?? Core Modules

- Authentication
- Dashboard
- Organization Setup
- Employee Directory
- Asset Registration
- Asset Allocation
- Resource Booking
- Maintenance Management
- Asset Audits
- Reports & Analytics
- Notifications
- Activity Logs

---


# ?? Future Improvements

- QR Code Scanner
- Barcode Support
- Mobile App
- AI-Based Asset Prediction
- Email Notifications
- SMS Alerts
- Cloud Deployment
- Multi-Organization Support


# ?? License

This project was developed for a College Hackathon and is intended for educational purposes.

---

# ?? Acknowledgements

- College Hackathon Organizers
- Mentors
- Faculty Members
- Open Source Community

---
