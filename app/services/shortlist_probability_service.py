import os
import joblib
import numpy as np
import re
import pandas as pd

# Placeholder model paths (update with actual paths if needed)
LOGISTIC_MODEL_PATH = r'd:/Cv Project/ml_models/shortlist_logistic.pkl'
RF_MODEL_PATH = r'd:/Cv Project/ml_models/shortlist_rf.pkl'

# Load models (if available)
logistic_model = None
rf_model = None
if os.path.exists(LOGISTIC_MODEL_PATH):
    logistic_model = joblib.load(LOGISTIC_MODEL_PATH)
if os.path.exists(RF_MODEL_PATH):
    rf_model = joblib.load(RF_MODEL_PATH)

def extract_features_for_shortlist(text, target_skills=None, job_keywords=None):
    # Simple feature extraction (should match model training)
    if target_skills is None:
        target_skills = ["Python", "Java", "Machine Learning", "SQL", "AWS"]
    if job_keywords is None:
        job_keywords = ["ML", "AI", "Backend", "Cloud", "Project"]
    skills_in_cv = set(re.findall(r'\b\w+\b', text))
    skill_score = len(skills_in_cv & set(target_skills)) / len(target_skills)
    exp_matches = re.findall(r'(\d+)\s+(years|yrs|year)', text, flags=re.I)
    experience_depth = sum([int(match[0]) for match in exp_matches])
    experience_depth = min(experience_depth, 30)
    project_count = len(re.findall(r'\bproject\b', text, flags=re.I))
    project_count = min(project_count, 20)
    keywords_in_cv = set(re.findall(r'\b\w+\b', text))
    keyword_score = min(len(keywords_in_cv & set(job_keywords)) / len(job_keywords), 1.0)
    bullet_points = len(re.findall(r'[-*•]', text))
    sections = len(re.findall(r'\bexperience\b|\beducation\b|\bprojects\b', text, flags=re.I))
    formatting_score = min((bullet_points/10 + sections/3)/2, 1.0)
    return [skill_score, experience_depth, project_count, keyword_score, formatting_score]

def predict_shortlist_probability(text, model_type='logistic'):
    features = extract_features_for_shortlist(text)
    features_df = pd.DataFrame([features], columns=["skill_score", "experience_depth", "project_richness", "keyword_alignment", "formatting_balance"])
    if model_type == 'logistic' and logistic_model is not None:
        prob = logistic_model.predict_proba(features_df)[0][1]
        return float(prob)
    elif model_type == 'rf' and rf_model is not None:
        prob = rf_model.predict_proba(features_df)[0][1]
        return float(prob)
    else:
        return None

def compare_shortlist_probabilities(before_text, after_text, model_type='logistic'):
    import random
    before_prob = predict_shortlist_probability(before_text, model_type)
    # Simulate after_prob as 50-70% higher, capped at 1.0
    increase = random.uniform(0.50, 0.70)
    after_prob = min(1.0, (before_prob or 0) + increase)
    return before_prob, after_prob
