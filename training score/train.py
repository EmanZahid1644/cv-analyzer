# Step 4 & 6: Train ML Models & Predict new CVs (DOCX + PDF)

# ----------------------------
# 1️⃣ Libraries
# ----------------------------
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from docx import Document
import pdfplumber
import os
import re

# ----------------------------
# 2️⃣ Load ML-ready dataset
# ----------------------------
df = pd.read_csv("ml_ready_cvs.csv")

# Features & target
X = df[["skill_score", "experience_depth", "project_richness", "keyword_alignment", "formatting_balance"]]
y = df["CV_score"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ----------------------------
# 3️⃣ Baseline: Linear Regression
# ----------------------------
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)

# Predict & Evaluate
y_pred_lr = lr_model.predict(X_test)
print("Linear Regression - MSE:", mean_squared_error(y_test, y_pred_lr))
print("Linear Regression - R²:", r2_score(y_test, y_pred_lr))

# Save Linear Regression model
joblib.dump(lr_model, "cv_lr_model.pkl")

# ----------------------------
# 4️⃣ Advanced: ANN
# ----------------------------
ann_model = Sequential()
ann_model.add(Dense(64, input_dim=X_train.shape[1], activation='relu'))
ann_model.add(Dense(32, activation='relu'))
ann_model.add(Dense(1, activation='linear'))  # CV_score output

# Compile
ann_model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# Train
ann_model.fit(X_train, y_train, validation_split=0.2, epochs=50, batch_size=16, verbose=1)

# Evaluate ANN
loss, mae = ann_model.evaluate(X_test, y_test)
print("ANN - Test MAE:", mae)

# Save ANN model
ann_model.save("cv_ann_model.h5")

# ----------------------------
# 5️⃣ Function to preprocess new resume (DOCX or PDF)
# ----------------------------
def preprocess_cv(file_path, target_skills, job_keywords):
    full_text = ""
    
    if file_path.endswith(".docx"):
        # DOCX extraction
        doc = Document(file_path)
        full_text = " ".join([para.text for para in doc.paragraphs]).replace("\n", " ").strip()
    
    elif file_path.endswith(".pdf"):
        # PDF extraction
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + " "
        full_text = full_text.strip()
    else:
        raise ValueError("Unsupported file format. Please provide a DOCX or PDF file.")
    
    # Skill score
    skills_in_cv = set(re.findall(r'\b\w+\b', full_text))
    skill_score = len(skills_in_cv & set(target_skills)) / len(target_skills)
    
    # Experience depth
    exp_matches = re.findall(r'(\d+)\s+(years|yrs|year)', full_text, flags=re.I)
    experience_depth = sum([int(match[0]) for match in exp_matches])
    experience_depth = min(experience_depth, 30)  # clip

    # Project richness
    project_count = len(re.findall(r'\bproject\b', full_text, flags=re.I))
    project_count = min(project_count, 20)  # clip

    # Keyword alignment
    keywords_in_cv = set(re.findall(r'\b\w+\b', full_text))
    keyword_score = min(len(keywords_in_cv & set(job_keywords)) / len(job_keywords), 1.0)

    # Formatting balance
    bullet_points = len(re.findall(r'[-*•]', full_text))
    sections = len(re.findall(r'\bexperience\b|\beducation\b|\bprojects\b', full_text, flags=re.I))
    formatting_score = min((bullet_points/10 + sections/3)/2, 1.0)

    return [skill_score, experience_depth, project_count, keyword_score, formatting_score]

# ----------------------------
# 6️⃣ Predict CV score for a new resume
# ----------------------------
target_skills = ["Python", "Java", "Machine Learning", "SQL", "AWS"]
job_keywords = ["ML", "AI", "Backend", "Cloud", "Project"]

new_cv_path = r"D:\training score\Resumes\New_Resume.pdf"  # replace with new CV path (DOCX or PDF)

features = preprocess_cv(new_cv_path, target_skills, job_keywords)
features_df = pd.DataFrame([features], columns=["skill_score", "experience_depth", "project_richness", "keyword_alignment", "formatting_balance"])

# Linear Regression prediction
pred_lr = lr_model.predict(features_df)[0]
print(f"Predicted CV Score (Linear Regression): {pred_lr:.2f}")

# ANN prediction
pred_ann = ann_model.predict(features_df)[0][0]
print(f"Predicted CV Score (ANN): {pred_ann:.2f}")
