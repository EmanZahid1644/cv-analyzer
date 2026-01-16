import os
import re
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model

# -----------------------------
# Load ANN Model
# -----------------------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../training score/cv_ann_model.h5')
ann_model = load_model(MODEL_PATH, compile=False)

def extract_features(text, target_skills=None, job_keywords=None):
    if target_skills is None:
        target_skills = ["Python", "Java", "Machine Learning", "SQL", "AWS"]
    if job_keywords is None:
        job_keywords = ["ML", "AI", "Backend", "Cloud", "Project"]

    text = str(text)
    # Skill score
    skills_in_cv = set(re.findall(r'\b\w+\b', text))
    skill_score = len(skills_in_cv & set(target_skills)) / len(target_skills)

    # Experience depth
    exp_matches = re.findall(r'(\d+)\s+(years|yrs|year)', text, flags=re.I)
    experience_depth = sum([int(match[0]) for match in exp_matches])
    experience_depth = min(experience_depth, 30)

    # Project richness
    project_count = len(re.findall(r'\bproject\b', text, flags=re.I))
    project_count = min(project_count, 20)

    # Keyword alignment
    keywords_in_cv = set(re.findall(r'\b\w+\b', text))
    keyword_score = min(len(keywords_in_cv & set(job_keywords)) / len(job_keywords), 1.0)

    # Formatting balance
    bullet_points = len(re.findall(r'[-*•]', text))
    sections = len(re.findall(r'\bexperience\b|\beducation\b|\bprojects\b', text, flags=re.I))
    formatting_score = min((bullet_points/10 + sections/3)/2, 1.0)

    return [skill_score, experience_depth, project_count, keyword_score, formatting_score]

def predict_cv_quality_score_ann(text):
    features = extract_features(text)
    features_df = pd.DataFrame([features], columns=["skill_score", "experience_depth", "project_richness", "keyword_alignment", "formatting_balance"])
    pred_ann = ann_model.predict(features_df)[0][0]
    score = max(0, min(100, pred_ann))
    return round(float(score), 1)
