# Production Deployment Guide

## Personalized Scholarship Recommendation System Using Machine Learning

This document outlines the steps required to deploy the application into a staging or production environment with zero hard-coded secrets and enterprise-grade security.

---

## 1. Environment Variables Configuration

Create a `.env` file based on `.env.example`. Ensure that **no real secret keys or database credentials are committed to version control**.

| Variable | Required | Default | Description |
| :--- | :---: | :--- | :--- |
| `FLASK_ENV` | Yes | `production` | Environment mode (`production`, `development`, `testing`). |
| `SECRET_KEY` | Yes | *(Must be generated)* | Cryptographically random key for signing session cookies. |
| `DATABASE_PATH` | No | `database/scholarships.db` | Path to local SQLite file or database connection URI. |
| `PORT` | No | `5000` | Port for WSGI web server to bind. |
| `WEIGHT_COURSE` | No | `0.25` | Weight for academic course match in recommendation engine. |
| `WEIGHT_ACADEMIC` | No | `0.25` | Weight for academic percentage / CGPA merit. |
| `WEIGHT_INCOME` | No | `0.20` | Weight for financial need / income criteria. |
| `WEIGHT_CATEGORY` | No | `0.10` | Weight for social reservation category. |
| `WEIGHT_STATE` | No | `0.10` | Weight for state domicile residency match. |
| `WEIGHT_YEAR` | No | `0.05` | Weight for student study year. |
| `WEIGHT_OTHER` | No | `0.05` | Weight for gender/achievements matching. |

### Generating a Strong SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 2. Production Installation & Setup

### Step A: Clone and Set Up Virtual Environment
```bash
git clone <repository_url>
cd scholarship-recommendation-system

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Step B: Initialize and Seed Database
```bash
python database/seed.py
```

### Step C: Fit & Cache ML Similarity Vectors
```bash
python ml/train_model.py
```

---

## 3. WSGI Server Options

Do not use `flask run` or `python app.py` in production. Instead, run behind a production WSGI server.

### Option 1: Gunicorn (Linux / Unix Environments)
```bash
python -m pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:application
```

### Option 2: Waitress (Windows Environments)
```bash
python -m pip install waitress
waitress-serve --port=5000 wsgi:application
```

---

## 4. Database Migration to PostgreSQL

The database schema in `database/schema.sql` was specifically drafted to be ANSI SQL & PostgreSQL compatible.

To connect to a managed PostgreSQL instance (e.g. AWS RDS, GCP Cloud SQL, Supabase, Neon):
1. Install PostgreSQL drivers:
   ```bash
   pip install psycopg2-binary
   ```
2. Set your connection string in environment:
   ```env
   DATABASE_URL=postgresql://user:password@hostname:5432/scholarships_db
   ```
3. Run the schema migrations against PostgreSQL:
   ```bash
   psql -h hostname -U user -d scholarships_db -f database/schema.sql
   ```

---

## 5. Health Check & Uptime Monitoring

The application includes an uptime health-check endpoint that can be monitored by AWS ELB, Kubernetes liveness probes, or UptimeRobot:

* **Endpoint**: `GET /api/health`
* **Expected Status**: `HTTP 200 OK`
* **Response Payload**:
  ```json
  {
    "environment": "production",
    "service": "Personalized Scholarship Recommendation System",
    "status": "healthy",
    "version": "1.0.0"
  }
  ```

---

## 6. Production Security Checklist

- [x] Passwords hashed using modern `scrypt` / `pbkdf2`.
- [x] All SQL queries use parameterized queries (zero SQL injection surface).
- [x] `SESSION_COOKIE_HTTPONLY = True` active.
- [x] `SESSION_COOKIE_SECURE = True` enabled for HTTPS connections.
- [x] `SESSION_COOKIE_SAMESITE = 'Lax'` configured.
- [x] Admin routes strictly gated with role validation (`@admin_required`).
- [x] Expired scholarships pruned from recommendation feeds automatically.
- [x] Disclaimers prominently displayed advising verification with official providers.
