# 💳 Payment Settlement & Transaction Exception Engine

A full-stack web application built using **Python Flask + SQLAlchemy + SQLite/MySQL** that automates **payment transaction settlement**, detects anomalies, and manages transaction exceptions through a real-time dashboard.

---

## 🚀 Features

- Automated transaction settlement
- Real-time dashboard with analytics
- Exception detection using rule-based engine
- Reconciliation between transactions & settlements
- Full CRUD operations on transactions
- Bulk operations (settle all, resolve all)
- RESTful API support
- Auto database seeding (60 sample records)

---

## 📂 Project Structure

*(Detailed structure available in project files)* :contentReference[oaicite:0]{index=0}

---

## 🛠️ Tech Stack

| Layer       | Technology |
|------------|-----------|
| Backend     | Python, Flask |
| ORM         | SQLAlchemy |
| Database    | SQLite / MySQL / PostgreSQL |
| Frontend    | HTML, CSS, JavaScript |
| Charts      | Chart.js |
| Deployment  | Render / Railway / Heroku |

---

## ⚙️ Quick Start (Local Setup)

### 1️⃣ Clone Repository
```bash
git clone https://github.com/Umang07-cell/payment_engine.git
cd payment_engine
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
python app.py

How It Works
Transactions are created or imported
Engine processes settlement
Exception engine detects anomalies
Reconciliation engine matches records
Dashboard displays insights

Database Support
SQLite (default)
MySQL
PostgreSQL

