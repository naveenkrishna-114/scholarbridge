-- Database Schema for Personalized Scholarship Recommendation System
-- Supports SQLite development and is PostgreSQL compatible.

PRAGMA foreign_keys = ON;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'admin')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Student Profiles Table
CREATE TABLE IF NOT EXISTS student_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    age INTEGER,
    gender TEXT CHECK (gender IN ('Male', 'Female', 'Other', 'Prefer not to say', NULL)),
    state TEXT NOT NULL,
    district TEXT,
    course TEXT NOT NULL,
    branch TEXT,
    year INTEGER NOT NULL,
    percentage REAL NOT NULL CHECK (percentage >= 0.0 AND percentage <= 100.0),
    cgpa REAL,
    income REAL NOT NULL CHECK (income >= 0.0),
    category TEXT DEFAULT 'General',
    disability_status TEXT DEFAULT 'No',
    achievements TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 3. Scholarships Table
CREATE TABLE IF NOT EXISTS scholarships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    description TEXT,
    amount REAL,
    course TEXT NOT NULL DEFAULT 'ALL',
    min_percentage REAL DEFAULT 0.0,
    max_income REAL DEFAULT 10000000.0,
    state TEXT NOT NULL DEFAULT 'ALL',
    category TEXT NOT NULL DEFAULT 'ALL',
    gender TEXT NOT NULL DEFAULT 'ALL',
    year INTEGER DEFAULT NULL,
    age_min INTEGER DEFAULT NULL,
    age_max INTEGER DEFAULT NULL,
    other_requirements TEXT,
    start_date TEXT,
    deadline TEXT,
    official_url TEXT NOT NULL,
    source_url TEXT,
    last_verified TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'EXPIRED', 'PENDING_VERIFICATION')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Saved Scholarships Table (Bookmarks)
CREATE TABLE IF NOT EXISTS saved_scholarships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    scholarship_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, scholarship_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (scholarship_id) REFERENCES scholarships (id) ON DELETE CASCADE
);

-- 5. Recommendations History Table
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    scholarship_id INTEGER NOT NULL,
    score REAL NOT NULL,
    explanation_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (scholarship_id) REFERENCES scholarships (id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_profiles_user ON student_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_scholarships_status ON scholarships(status);
CREATE INDEX IF NOT EXISTS idx_scholarships_course ON scholarships(course);
CREATE INDEX IF NOT EXISTS idx_scholarships_state ON scholarships(state);
CREATE INDEX IF NOT EXISTS idx_saved_user ON saved_scholarships(user_id);
