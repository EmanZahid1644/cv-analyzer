import os
import joblib
import re
import pandas as pd

# Load Linear Regression model
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../training score/cv_lr_model.pkl')
lr_model = joblib.load(MODEL_PATH)

def preprocess_cv_text(text, target_skills=None, job_keywords=None):
    if target_skills is None:
        target_skills = ["Python", "Java", "Machine Learning", "SQL", "AWS"]
    if job_keywords is None:
        job_keywords = ["ML", "AI", "Backend", "Cloud", "Project"]
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

    # Section/heading detection (lines that are likely headings)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    heading_count = 0
    heading_pattern = re.compile(r'^(?:[A-Z][A-Z\s\-&]{2,}|[A-Z][a-z]+\s*:?|[A-Z]{2,})$')
    for line in lines:
        # Heuristic: all-caps, or Title: or short lines with no punctuation
        if (heading_pattern.match(line) and len(line.split()) <= 6) or (len(line) < 30 and line.isupper()):
            heading_count += 1

    # Return new feature: heading_count (section/neutral lines)
    return [skill_score, experience_depth, project_count, keyword_score, formatting_score, heading_count]

def predict_cv_quality_score(text):
    features = preprocess_cv_text(text)
    # For backward compatibility, ignore heading_count for model input
    features_df = pd.DataFrame([features[:5]], columns=["skill_score", "experience_depth", "project_richness", "keyword_alignment", "formatting_balance"])
    pred = lr_model.predict(features_df)[0]
    return round(float(pred), 2)

# Utility: classify each line as Useful, Useless, or Section/Neutral
def classify_cv_lines(text):
    """
    Returns a list of tuples: (line, tag) where tag is 'Useful', 'Useless', or 'Section'
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    heading_pattern = re.compile(r'^(?:[A-Z][A-Z\s\-&]{2,}|[A-Z][a-z]+\s*:?|[A-Z]{2,})$')
    results = []
    for line in lines:
        # Section/heading detection
        if (heading_pattern.match(line) and len(line.split()) <= 6) or (len(line) < 30 and line.isupper()):
            results.append((line, 'Section'))
        # Useless: very short, no verbs, or just symbols
        elif len(line) < 8 or re.match(r'^[\W_]+$', line):
            results.append((line, 'Useless'))
        else:
            results.append((line, 'Useful'))
    return results

