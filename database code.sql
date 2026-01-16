USE cv_analysis_system;
-- 1️⃣ Users
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2️⃣ CVs
CREATE TABLE CVs (
    cv_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    file_name VARCHAR(255),
    file_type ENUM('pdf','docx','image'),
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- 3️⃣ CV_Analysis
CREATE TABLE CV_Analysis (
    analysis_id INT AUTO_INCREMENT PRIMARY KEY,
    cv_id INT,
    job_category VARCHAR(255),
    quality_score FLOAT,
    useful_content JSON,
    useless_content JSON,
    clusters JSON,
    gap_analysis JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cv_id) REFERENCES CVs(cv_id)
);

-- 4️⃣ Job_Roles
CREATE TABLE Job_Roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    role_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- 5️⃣ Skill_Gap
CREATE TABLE Skill_Gap (
    gap_id INT AUTO_INCREMENT PRIMARY KEY,
    cv_id INT,
    required_skills JSON,
    present_skills JSON,
    missing_skills JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cv_id) REFERENCES CVs(cv_id)
);

-- 6️⃣ Optimization_Results
CREATE TABLE Optimization_Results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    cv_id INT,
    optimized_cv_file VARCHAR(255),
    score_before FLOAT,
    score_after FLOAT,
    comparison JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cv_id) REFERENCES CVs(cv_id)
);

-- 7️⃣ Interview_Questions
CREATE TABLE Interview_Questions (
    iq_id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT,
    questions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES Job_Roles(role_id)
);

-- 8️⃣ Feedback
CREATE TABLE Feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    cv_id INT,
    rating INT,
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (cv_id) REFERENCES CVs(cv_id)
);

-- 9️⃣ user_skill_feedback
CREATE TABLE IF NOT EXISTS user_skill_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    cv_id INT,
    job_title VARCHAR(255),
    added_skills TEXT,
    rejected_skills TEXT,
    feedback_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
