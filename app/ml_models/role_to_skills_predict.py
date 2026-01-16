import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

# Paths to model artifacts
MLB_PATH = r'd:/Cv Project/ml_models/role_to_skills_mlb.joblib'

# Load model and binarizer once
role_to_skills_mlb = None

def get_role_to_skills_mlb():
    global role_to_skills_mlb
    if role_to_skills_mlb is None:
        print(f"[PREDICT] Loading MLB from: {MLB_PATH}")
        role_to_skills_mlb = joblib.load(MLB_PATH)
        print(f"[PREDICT] MLB classes (first 20): {role_to_skills_mlb.classes_[:20]}")
    return role_to_skills_mlb

def predict_required_skills_ml(job_role_or_desc):
    """
    Lookup skills for a job title using MLB classes (simple match).
    Returns a list of skills for the given job title.
    """
    mlb = get_role_to_skills_mlb()
    norm_role = job_role_or_desc.lower().strip()
    # Load skills_data CSV to map job title to skills
    import pandas as pd
    csv_path = r'd:/Cv Project/skill training/skills_data - skills_data.csv'
    df = pd.read_csv(csv_path)
    # Filter rows matching the job title (case-insensitive)
    matched = df[df['job title'].str.lower().str.strip() == norm_role]
    if matched.empty:
        return []
    # Aggregate all skills for the job title
    skills = set()
    for skill_list in matched['skills']:
        for skill in str(skill_list).split(','):
            skills.add(skill.strip())
    return sorted(skills)
