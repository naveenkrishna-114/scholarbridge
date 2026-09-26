-- ====================================================================
-- SUPABASE POSTGRESQL SCHEMA & INITIAL DATA SEED
-- Personalized Scholarship Recommendation System
-- Run this entire script in your Supabase SQL Editor (SQL Editor -> New Query -> Run)
-- ====================================================================

-- 1. Create Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'student' CHECK (role IN ('student', 'admin')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create Student Profiles Table
CREATE TABLE IF NOT EXISTS student_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    age INTEGER,
    gender VARCHAR(50) CHECK (gender IN ('Male', 'Female', 'Other', 'Prefer not to say', NULL)),
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100),
    course VARCHAR(100) NOT NULL,
    branch VARCHAR(100),
    year INTEGER NOT NULL CHECK (year BETWEEN 1 AND 8),
    percentage NUMERIC(5,2) NOT NULL CHECK (percentage >= 0.0 AND percentage <= 100.0),
    cgpa NUMERIC(4,2),
    income NUMERIC(12,2) NOT NULL CHECK (income >= 0.0),
    category VARCHAR(50) DEFAULT 'General',
    disability_status VARCHAR(10) DEFAULT 'No',
    achievements TEXT,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Create Scholarships Table
CREATE TABLE IF NOT EXISTS scholarships (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    provider VARCHAR(255) NOT NULL,
    description TEXT,
    amount NUMERIC(12,2),
    course VARCHAR(100) NOT NULL DEFAULT 'ALL',
    min_percentage NUMERIC(5,2) DEFAULT 0.0,
    max_income NUMERIC(12,2) DEFAULT 10000000.0,
    state VARCHAR(100) NOT NULL DEFAULT 'ALL',
    category VARCHAR(50) NOT NULL DEFAULT 'ALL',
    gender VARCHAR(50) NOT NULL DEFAULT 'ALL',
    year INTEGER,
    age_min INTEGER,
    age_max INTEGER,
    other_requirements TEXT,
    start_date DATE,
    deadline DATE,
    official_url TEXT NOT NULL,
    source_url TEXT,
    last_verified DATE,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'EXPIRED', 'PENDING_VERIFICATION')),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Create Saved Scholarships Table (Bookmarks)
CREATE TABLE IF NOT EXISTS saved_scholarships (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scholarship_id INTEGER NOT NULL REFERENCES scholarships(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_scholarship UNIQUE(user_id, scholarship_id)
);

-- 5. Create Recommendations History Table
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    scholarship_id INTEGER NOT NULL REFERENCES scholarships(id) ON DELETE CASCADE,
    score NUMERIC(5,3) NOT NULL,
    explanation_json JSONB,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_profiles_user ON student_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_scholarships_status ON scholarships(status);
CREATE INDEX IF NOT EXISTS idx_scholarships_course ON scholarships(course);
CREATE INDEX IF NOT EXISTS idx_scholarships_state ON scholarships(state);
CREATE INDEX IF NOT EXISTS idx_saved_user ON saved_scholarships(user_id);

-- ====================================================================
-- SEED DATA: Verified Scholarships Repository
-- ====================================================================

INSERT INTO scholarships (
    name, provider, description, amount, course, min_percentage, max_income,
    state, category, gender, year, age_min, age_max, other_requirements,
    start_date, deadline, official_url, source_url, last_verified, status
) VALUES 
(
    'AICTE Pragati Scholarship for Girls', 'AICTE',
    'Financial support to young women pursuing technical diploma or undergraduate degree education.',
    50000.00, 'B.Tech', 60.0, 800000.00, 'ALL', 'ALL', 'Female', 1, NULL, 30,
    'Family income under 8 LPA; max 2 girls per family',
    '2026-08-01', '2026-11-30', 'https://www.aicte-india.org/schemes/students-development-schemes/Pragati',
    'https://nsp.gov.in', '2026-09-01', 'ACTIVE'
),
(
    'Reliance Foundation Undergraduate Scholarship', 'Reliance Foundation',
    'Empowering first-generation and high-merit students across India pursuing undergraduate degrees.',
    200000.00, 'ALL', 75.0, 1500000.00, 'ALL', 'ALL', 'ALL', 1, NULL, 25,
    'Aptitude test score + household income verification',
    '2026-08-15', '2026-10-15', 'https://www.scholarships.reliancefoundation.org/',
    'https://www.reliancefoundation.org', '2026-09-10', 'ACTIVE'
),
(
    'Central Sector Scheme of Scholarships (CSSS)', 'Department of Higher Education (MHRD)',
    'Merit-cum-means scholarship for top percentile college and university students.',
    20000.00, 'ALL', 80.0, 450000.00, 'ALL', 'ALL', 'ALL', 1, 18, 25,
    'Above 80th percentile in relevant stream in Class XII',
    '2026-07-01', '2026-10-31', 'https://scholarships.gov.in/',
    'https://nsp.gov.in', '2026-08-20', 'ACTIVE'
),
(
    'Post Matric Scholarship for SC Students', 'Ministry of Social Justice and Empowerment',
    'Full tuition and maintenance allowance for Scheduled Caste students pursuing higher education.',
    75000.00, 'ALL', 50.0, 250000.00, 'ALL', 'SC', 'ALL', NULL, 17, 35,
    'Valid caste certificate and income certificate',
    '2026-06-01', '2026-12-31', 'https://scholarships.gov.in/',
    'https://socialjustice.gov.in', '2026-09-05', 'ACTIVE'
),
(
    'Post Matric Scholarship for OBC Students', 'Ministry of Social Justice and Empowerment',
    'State-administered financial support for Other Backward Classes students.',
    45000.00, 'ALL', 55.0, 250000.00, 'ALL', 'OBC', 'ALL', NULL, 17, 35,
    'Valid OBC non-creamy layer certificate',
    '2026-07-01', '2026-12-15', 'https://scholarships.gov.in/',
    'https://socialjustice.gov.in', '2026-08-30', 'ACTIVE'
),
(
    'Tamil Nadu Chief Minister Merit Scholarship', 'Government of Tamil Nadu',
    'Merit-based financial aid for undergraduate students domiciled in Tamil Nadu.',
    30000.00, 'ALL', 70.0, 300000.00, 'Tamil Nadu', 'ALL', 'ALL', 2, 17, 25,
    'Resident of Tamil Nadu with native certificate',
    '2026-08-01', '2026-11-15', 'https://www.tn.gov.in/scholarships',
    'https://tnscholarships.gov.in', '2026-09-12', 'ACTIVE'
),
(
    'Maharashtra Post-Matric Scholarship (MahaDBT)', 'Government of Maharashtra',
    'Financial assistance to undergraduate students domiciled in Maharashtra state.',
    40000.00, 'ALL', 60.0, 300000.00, 'Maharashtra', 'ALL', 'ALL', NULL, 17, 28,
    'Valid Maharashtra domicile certificate',
    '2026-07-15', '2026-11-30', 'https://mahadbt.maharashtra.gov.in/',
    'https://mahadbt.maharashtra.gov.in/', '2026-08-25', 'ACTIVE'
),
(
    'Siemens Scholarship Program', 'Siemens India',
    'Four-year comprehensive scholarship covering tuition and books for 1st year engineering students.',
    100000.00, 'B.Tech', 60.0, 200000.00, 'ALL', 'ALL', 'ALL', 1, NULL, 20,
    'First year Govt/Govt-aided engineering college students',
    '2026-08-01', '2026-10-05', 'https://www.siemens.com/in/en/company/sustainability/siemens-scholarship.html',
    'https://www.siemens.com', '2026-08-15', 'ACTIVE'
),
(
    'Adobe India Women-in-Technology Scholarship', 'Adobe India',
    'Stipend and mentoring for female undergraduates enrolled in computer science or related branches.',
    150000.00, 'B.Tech', 75.0, 1200000.00, 'ALL', 'ALL', 'Female', 3, NULL, 26,
    'Major in Computer Science / IT or related discipline',
    '2026-08-01', '2026-09-30', 'https://www.adobe.com/careers/university/india-scholarship.html',
    'https://adobe.com', '2026-09-01', 'ACTIVE'
),
(
    'HDFC Badhte Kadam Scholarship', 'HDFC Bank Parivartan',
    'Support for high performing students from financially disadvantaged families facing distress.',
    50000.00, 'ALL', 60.0, 600000.00, 'ALL', 'ALL', 'ALL', NULL, 16, 28,
    'Family income under 6 LPA, preference to hardship cases',
    '2026-07-01', '2026-10-31', 'https://www.hdfcbank.com/personal/about-us/corporate-social-responsibility',
    'https://www.buddy4study.com', '2026-09-15', 'ACTIVE'
),
(
    'Sitaram Jindal Foundation Scholarship', 'Sitaram Jindal Foundation',
    'Financial assistance for poor and meritorious students pursuing polytechnic, degree, and PG courses.',
    24000.00, 'ALL', 65.0, 400000.00, 'ALL', 'ALL', 'ALL', NULL, 15, 30,
    'Merit cum means criterion with income certificate',
    '2026-01-01', '2026-12-31', 'https://www.sitaramjindalfoundation.org/scholarships.php',
    'https://sitaramjindalfoundation.org', '2026-07-10', 'ACTIVE'
),
(
    'Expired Previous Cycle Grant (Demo Check)', 'Department of Science & Technology',
    'Archived national fellowship record for testing expired status handling.',
    35000.00, 'B.Sc', 70.0, 500000.00, 'ALL', 'ALL', 'ALL', 1, 18, 25,
    'Archived test record',
    '2025-01-01', '2025-06-30', 'https://dst.gov.in/expired-scheme',
    'https://dst.gov.in', '2025-07-01', 'EXPIRED'
)
ON CONFLICT DO NOTHING;

-- ====================================================================
-- SEED DATA: Demo Users & Profiles (Password: Password123!)
-- Password hash generated using Werkzeug scrypt format
-- ====================================================================

-- 1. Demo Student: Aarav Sharma
INSERT INTO users (id, name, email, password_hash, role)
VALUES (
    1,
    'Aarav Sharma',
    'aarav.sharma@example.com',
    'scrypt:32768:8:1$Y6L2dsqbkW1jP0uR$ee6bb9a44c4fae85cf55d143c74c1064d4ec6b4bc9da43399fcb60d00a12e5ebf899eeea63ba317730e6bb2a92612a20b3322fb753d0623a311b7df36e053f36',
    'student'
) ON CONFLICT (email) DO NOTHING;

INSERT INTO student_profiles (user_id, age, gender, state, district, course, branch, year, percentage, cgpa, income, category, disability_status, achievements)
VALUES (
    1, 20, 'Male', 'Tamil Nadu', 'Chennai', 'B.Tech', 'Computer Science', 2, 84.0, 8.7, 200000.00, 'General', 'No', 'Hackathon winner, College coding club lead'
) ON CONFLICT (user_id) DO NOTHING;

-- 2. Demo Student: Priya Patel
INSERT INTO users (id, name, email, password_hash, role)
VALUES (
    2,
    'Priya Patel',
    'priya.patel@example.com',
    'scrypt:32768:8:1$Y6L2dsqbkW1jP0uR$ee6bb9a44c4fae85cf55d143c74c1064d4ec6b4bc9da43399fcb60d00a12e5ebf899eeea63ba317730e6bb2a92612a20b3322fb753d0623a311b7df36e053f36',
    'student'
) ON CONFLICT (email) DO NOTHING;

INSERT INTO student_profiles (user_id, age, gender, state, district, course, branch, year, percentage, cgpa, income, category, disability_status, achievements)
VALUES (
    2, 19, 'Female', 'Maharashtra', 'Pune', 'B.Tech', 'Information Technology', 1, 88.5, 9.2, 350000.00, 'OBC', 'No', 'National Science Olympiad finalist'
) ON CONFLICT (user_id) DO NOTHING;

-- 3. Demo Admin: Vikram Singh
INSERT INTO users (id, name, email, password_hash, role)
VALUES (
    3,
    'Vikram Singh',
    'vikram.admin@example.com',
    'scrypt:32768:8:1$Y6L2dsqbkW1jP0uR$ee6bb9a44c4fae85cf55d143c74c1064d4ec6b4bc9da43399fcb60d00a12e5ebf899eeea63ba317730e6bb2a92612a20b3322fb753d0623a311b7df36e053f36',
    'admin'
) ON CONFLICT (email) DO NOTHING;

-- Reset sequence counters to prevent key collisions
SELECT setval('users_id_seq', (SELECT COALESCE(MAX(id), 1) FROM users));
SELECT setval('student_profiles_id_seq', (SELECT COALESCE(MAX(id), 1) FROM student_profiles));
SELECT setval('scholarships_id_seq', (SELECT COALESCE(MAX(id), 1) FROM scholarships));
