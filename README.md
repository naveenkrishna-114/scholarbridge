# Personalized Scholarship Recommendation System Using Machine Learning

A production-ready web platform that analyzes student information and scholarship eligibility criteria to recommend suitable opportunities using a hybrid architecture of rule-based eligibility filtering and content-based machine learning (TF-IDF & Cosine Similarity).

> **Important Principle**: The system is a recommendation and discovery assistant, not an official scholarship granting authority. Final eligibility, deadlines, and application requirements must always be verified on the official scholarship provider's portal.

---

## Key Features

1. **Secure Student Authentication & Profiling**:
   - Secure account creation and login using cryptographic password hashing (`scrypt` / `pbkdf2`).
   - Granular profiling capturing academic percentage/CGPA, enrolled degree, study year, family income ceiling, state domicile, social category, and achievements.

2. **Hard Rule-Based Eligibility Engine**:
   - Strictly prunes incompatible schemes based on non-negotiable criteria (minimum percentage cutoffs, income limits, state residency, course eligibility, year of study, and gender quotas).
   - Automatically detects and hides expired or inactive scholarship opportunities.

3. **Machine Learning & Content-Based Similarity**:
   - Feature engineering pipeline (`TfidfVectorizer` + `cosine_similarity`) that captures semantic affinity between student profile highlights and scholarship opportunity details.
   - Evaluated using classical ranking metrics: **Precision@K**, **Recall@K**, and **Hit Rate@K**.

4. **Explainable AI & Transparent Match Insights**:
   - Every recommendation provides a clear checklist of matching criteria (e.g., *"Direct course match for B.Tech"*, *"Strong academic merit (84% exceeds 60% minimum)"*, *"Household income qualifies"*).
   - Highlights verification items, deadlines, and direct links to official application portals.

5. **Student Bookmarking & Management**:
   - Instant save/bookmark toggle to monitor opportunities.

6. **Role-Protected Admin Management Portal**:
   - Dedicated administrative dashboard to verify, add, edit, or deactivate scholarships, monitor deadlines, and audit source URLs.

---

## Technology Stack

- **Backend**: Python 3.10+, Flask, REST API
- **Data & ML**: Scikit-Learn, Pandas, NumPy
- **Database**: SQLite (local development) / PostgreSQL-ready ANSI SQL schema
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Bootstrap Icons
- **Testing**: Pytest (44 automated unit, integration, and security tests)
- **Deployment**: Production WSGI (`wsgi.py`), Gunicorn / Waitress support

---

## Project Structure

```
├── app.py                      # Application factory & API routes
├── config.py                   # Configuration classes & recommendation weights
├── wsgi.py                     # Production WSGI entry point
├── requirements.txt            # Python dependencies
├── DEPLOYMENT.md               # Production deployment & migration guide
├── README.md                   # System documentation
├── .env.example                # Template for environment configuration
├── data/
│   ├── scholarships.csv        # Verified sample scholarship dataset
│   └── sample_students.csv     # Benchmark student profiles
├── database/
│   ├── schema.sql              # Relational database schema with foreign keys
│   ├── db.py                   # Thread-safe database connection helpers
│   └── seed.py                 # Automated DB initialization & CSV data seeder
├── models/
│   ├── user.py                 # User authentication & StudentProfile DAO
│   └── scholarship.py          # Scholarship, SavedScholarship & Audit DAO
├── routes/
│   ├── auth.py                 # Register, login, logout, session routes
│   ├── student.py              # Profile retrieval and update API
│   ├── scholarships.py         # Recommendation, listing, and saved APIs
│   ├── admin.py                # Admin dashboard & scholarship CRUD
│   └── views.py                # Web template view controllers
├── services/
│   ├── eligibility_service.py  # Rule-based hard eligibility filter
│   ├── recommendation_service.py # Hybrid multi-attribute & ML ranking
│   └── explanation_service.py  # Transparent match reason generator
├── ml/
│   ├── preprocessing.py        # Tokenization & feature engineering
│   ├── recommend.py            # TF-IDF vectorizer & Cosine Similarity model
│   ├── train_model.py          # Model persistence & fitting script
│   └── metrics.py              # Precision@K, Recall@K, HitRate@K metrics
├── templates/                  # Jinja2 responsive templates
│   ├── base.html, index.html, login.html, register.html,
│   ├── profile.html, recommendations.html, scholarship.html,
│   ├── saved.html, scholarships_list.html, admin.html
├── static/                     # CSS, JS, and image assets
└── tests/                      # Automated test suite (44 tests)
```

---

## Quick Start & Setup

### 1. Initialize Virtual Environment & Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 2. Initialize and Seed the Database
```bash
python database/seed.py
```

### 3. Run Automated Tests
```bash
python -m pytest tests/
```

### 4. Run the Development Server
```bash
python app.py
```
Open **`http://127.0.0.1:5000`** in your browser.

---

## Demo Accounts for Evaluation

| Role | Email | Password | Access Details |
| :--- | :--- | :--- | :--- |
| **Demo Student** | `aarav.sharma@example.com` | `Password123!` | B.Tech, 2nd Year, 84% marks, Tamil Nadu resident. Has active matches! |
| **Administrator** | `vikram.admin@example.com` | `Password123!` | Access to `/admin` to add, edit, or archive scholarships. |

---

## Phased Execution Status

- [x] **Phase 1: Foundation** (Flask architecture, configs, health check)
- [x] **Phase 2: Database Layer** (Relational schema, CRUD, verified CSV datasets, seed script)
- [x] **Phase 3: Authentication & Profile** (Hashed credentials, validation, session management)
- [x] **Phase 4: Eligibility Engine** (Rule-based filtering, boundary cutoffs, deadline checks)
- [x] **Phase 5: Recommendation Scoring** (Weighted multi-attribute scoring, explainability)
- [x] **Phase 6: Machine Learning Module** (TF-IDF + Cosine similarity, metrics Precision@K)
- [x] **Phase 7: Responsive Frontend UI** (Bootstrap 5 templates, recommendation cards)
- [x] **Phase 8: Admin Management Portal** (CRUD, verification date, status management)
- [x] **Phase 9: Testing & Security Audit** (SQLi immunity, XSS mitigation, secure cookies)
- [x] **Phase 10: Deployment Preparation** (Production WSGI, migration guide, E2E flow test)
