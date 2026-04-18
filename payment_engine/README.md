# Payment Settlement & Transaction Exception Engine

A full-stack web application built with **Python Flask + SQLAlchemy + SQLite/MySQL** that automates payment transaction settlement, detects anomalies, and manages transaction exceptions through a real-time dashboard.

---

## Project Structure

```
payment_engine/
├── app.py                        # Flask app factory & entry point
├── database.py                   # Shared SQLAlchemy instance
├── requirements.txt              # Python dependencies
├── Procfile                      # For Render / Heroku deployment
├── render.yaml                   # One-click Render deployment config
├── railway.toml                  # Railway deployment config
├── .env.example                  # Environment variable template
├── .gitignore
│
├── models/
│   ├── __init__.py
│   ├── transaction.py            # Transaction model
│   ├── settlement.py             # Settlement record model
│   ├── exception.py              # TransactionException model
│   └── reconciliation.py        # ReconciliationRun log model
│
├── routes/
│   ├── __init__.py
│   ├── dashboard.py              # Dashboard stats API + index page
│   ├── transactions.py           # Full CRUD + settle/retry actions
│   ├── settlements.py            # Settlement listing + summary
│   ├── exceptions.py             # Exception log + resolve + detect
│   └── reconciliation.py        # Reconciliation run + history
│
├── utils/
│   ├── __init__.py
│   ├── seeder.py                 # Auto-seeds DB with 60 sample records
│   ├── exception_engine.py       # Rule-based anomaly detection engine
│   └── reconciliation_engine.py # Transaction ↔ settlement matching
│
└── templates/
    └── index.html                # Full SPA frontend (Chart.js + Fetch API)
```

---

## Tech Stack

| Layer       | Technology                    |
|-------------|-------------------------------|
| Backend     | Python 3.10+, Flask 3.x       |
| ORM         | Flask-SQLAlchemy, SQLAlchemy  |
| Database    | SQLite (dev) / MySQL / PostgreSQL (prod) |
| Frontend    | HTML5, CSS3, Vanilla JS       |
| Charts      | Chart.js 4.x                  |
| Server      | Gunicorn (production)         |
| Deployment  | Render / Railway / Heroku     |

---

## Quick Start (Local Development)

### Step 1 — Clone / Extract the project
```bash
# If you downloaded the ZIP, extract it first
unzip payment_engine.zip
cd payment_engine
```

### Step 2 — Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Set up environment variables
```bash
# Copy the example file
cp .env.example .env

# Open .env and set your SECRET_KEY (everything else works by default)
```

### Step 5 — Run the application
```bash
python app.py
```

Open your browser and go to: **http://localhost:5000**

The database is auto-created and seeded with 60 sample transactions on first run.

---

## API Reference

All API endpoints return JSON.

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | KPIs, charts data, recent activity |

### Transactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/transactions/` | List all (filter: search, status, type, channel) |
| GET | `/api/transactions/<id>` | Get single transaction with exceptions & settlement |
| POST | `/api/transactions/` | Create new transaction |
| PATCH | `/api/transactions/<id>/status` | Update transaction status |
| POST | `/api/transactions/actions/settle-all-pending` | Bulk settle all pending |
| DELETE | `/api/transactions/<id>` | Delete a transaction |

### Settlements
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/settlements/` | List all settlements |
| GET | `/api/settlements/summary` | Summary stats |
| GET | `/api/settlements/<id>` | Get single settlement |

### Exceptions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/exceptions/` | List all (filter: severity, status) |
| GET | `/api/exceptions/<id>` | Get single exception |
| POST | `/api/exceptions/<id>/resolve` | Resolve an exception |
| POST | `/api/exceptions/actions/resolve-all` | Bulk resolve all open |
| POST | `/api/exceptions/actions/detect` | Run exception detection engine |
| GET | `/api/exceptions/summary` | Summary by severity |

### Reconciliation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/reconciliation/run` | Run reconciliation engine |
| GET | `/api/reconciliation/history` | All reconciliation run logs |
| GET | `/api/reconciliation/latest` | Most recent run result |

---

## Exception Detection Rules

The `ExceptionEngine` automatically applies 5 rules:

| Rule | Severity | Description |
|------|----------|-------------|
| Duplicate Entry | Critical | Same sender + receiver + amount + date |
| High Value Anomaly | High | Amount > ₹90,000 |
| Transaction Failed | High | Status = Failed |
| Stale Pending | Medium | Pending for > 24 hours |
| Round-Trip Amount | Medium | Matching back-and-forth amounts |

---

## Connecting to MySQL (Production Database)

### Step 1 — Install MySQL driver
```bash
pip install pymysql
pip freeze > requirements.txt
```

### Step 2 — Create MySQL database
```sql
CREATE DATABASE payment_engine CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'payuser'@'localhost' IDENTIFIED BY 'StrongPassword123!';
GRANT ALL PRIVILEGES ON payment_engine.* TO 'payuser'@'localhost';
FLUSH PRIVILEGES;
```

### Step 3 — Update .env
```env
DATABASE_URL=mysql+pymysql://payuser:StrongPassword123!@localhost:3306/payment_engine
```

### Step 4 — Run app (tables auto-created)
```bash
python app.py
```

---

## Deployment Guide

### Option A — Render (Recommended, Free Tier Available)

1. Push your project to GitHub
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/payment-engine.git
   git push -u origin main
   ```

2. Go to **https://render.com** → Sign up → **New Web Service**

3. Connect your GitHub repo

4. Render auto-detects `render.yaml` — click **Deploy**

5. Set environment variables in Render dashboard:
   - `SECRET_KEY` → any long random string
   - `FLASK_ENV` → `production`

6. Your app is live at `https://your-app-name.onrender.com` 🎉

---

### Option B — Railway (Very Simple)

1. Go to **https://railway.app** → New Project → Deploy from GitHub

2. Select your repo

3. Add environment variables:
   - `SECRET_KEY` → random string
   - `PORT` → `5000`

4. Railway reads `railway.toml` automatically → deploys in ~2 minutes

---

### Option C — Heroku

```bash
# Install Heroku CLI, then:
heroku login
heroku create payment-engine-yourname
heroku config:set SECRET_KEY=your-secret-key FLASK_ENV=production
git push heroku main
heroku open
```

---

### Option D — VPS / Ubuntu Server (DigitalOcean, AWS EC2, etc.)

```bash
# 1. SSH into your server
ssh root@YOUR_SERVER_IP

# 2. Install Python & Nginx
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx -y

# 3. Upload your project (or git clone)
git clone https://github.com/YOUR_USERNAME/payment-engine.git
cd payment-engine

# 4. Setup virtual env
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Create .env
cp .env.example .env
nano .env  # set SECRET_KEY and DATABASE_URL

# 6. Test it works
python app.py

# 7. Run with Gunicorn
gunicorn "app:create_app()" --bind 0.0.0.0:5000 --workers 2 --daemon

# 8. Configure Nginx as reverse proxy
sudo nano /etc/nginx/sites-available/payment_engine
```

Paste this Nginx config:
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN_OR_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/payment_engine /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Your app is now live on **http://YOUR_DOMAIN_OR_IP** !

---

## Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: flask` | Run `pip install -r requirements.txt` inside your virtual environment |
| Port 5000 already in use | Run `python app.py` with `--port 8000` or kill the process |
| Database locked (SQLite) | Restart the app; don't run multiple workers with SQLite |
| 500 error on Render | Check Render logs; ensure `SECRET_KEY` env var is set |
| Tables not created | Delete `payment_engine.db` and restart — it auto-recreates |

---

## License
MIT — free to use, modify, and distribute.
