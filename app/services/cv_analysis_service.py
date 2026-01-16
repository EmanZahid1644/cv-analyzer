from app.ml_models.skill_gap import hybrid_skill_extraction

import os
import joblib
import re
from app.ml_models.skill_gap import extract_skills, extract_experience_years, cluster_skills, detect_gaps, semantic_skill_gap_analysis, ml_skill_gap_analysis
from app.ml_models.skill_gap import hybrid_skill_extraction

def clean_text(text):
    text = str(text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9 ]', ' ', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()



# Load job category model and BERT model name
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../../ml_models/job_category_model.pkl')
BERT_NAME_PATH = os.path.join(os.path.dirname(__file__), '../../ml_models/bert_model_name.txt')
model = joblib.load(MODEL_PATH)
with open(BERT_NAME_PATH, 'r') as f:
    bert_model_name = f.read().strip()
from sentence_transformers import SentenceTransformer
bert_model = SentenceTransformer(bert_model_name)


# Advanced feature extraction for job prediction
def extract_advanced_features(text, target_skills=None, job_keywords=None):
    if target_skills is None:
        target_skills = ["python", "java", "sql", "machine learning", "aws", "excel", "c++", "javascript", "project management", "data analysis"]
    if job_keywords is None:
        job_keywords = ["developer", "engineer", "analyst", "manager", "designer", "teacher", "consultant", "finance", "marketing", "sales"]

    text = text.lower()
    # Skills extraction
    skills_in_cv = set(re.findall(r'\b\w+\b', text))
    skill_score = len(skills_in_cv & set(target_skills)) / len(target_skills)

    # Keyword alignment
    keywords_in_cv = set(re.findall(r'\b\w+\b', text))
    keyword_score = len(keywords_in_cv & set(job_keywords)) / len(job_keywords)

    # Section detection
    sections = ["education", "experience", "skills", "projects", "summary"]
    section_count = sum(1 for s in sections if s in text)

    # Length features
    length = len(text)
    word_count = len(text.split())

    return [skill_score, keyword_score, section_count, length, word_count]

# Predict job category using advanced features (for future model)
def predict_job_category_advanced(resume_text):
    clean_resume = clean_text(resume_text)
    # Use BERT embeddings for prediction
    try:
        X = bert_model.encode([clean_resume])
        pred = model.predict(X)[0]
        return pred
    except Exception as e:
        print("Prediction error:", e)
        return "Prediction Error"

def predict_job_category(resume_text):
    # For now, use advanced features for future, but keep current model for prediction
    return predict_job_category_advanced(resume_text)

# --- Hybrid Skill Extraction (Embedding + ML) ---
def hybrid_skill_gap_analysis(job_desc_text, top_n=10):
    """
    Returns a dict with embedding-based, ML-based, and combined skill predictions for a job description.
    """
    return hybrid_skill_extraction(job_desc_text, top_n=top_n)
# --- New: Clustering & Gap Analysis ---
# --- New: Clustering & Gap Analysis ---
def analyze_skills_and_gaps(cv_text, job_desc_text=None):
    # Extract skills from CV
    cv_skills = extract_skills(cv_text)
    years = extract_experience_years(cv_text)
    labels, skill_clusters = cluster_skills(cv_skills)
    gaps = detect_gaps(years)
    # If job_desc_text is provided, run semantic skill gap analysis
    if job_desc_text:
        job_desc_skills = extract_skills(job_desc_text)
        gap_result = semantic_skill_gap_analysis(cv_skills, job_desc_skills)
    else:
        gap_result = None
    return {
        "skills": cv_skills,
        "skill_clusters": skill_clusters,
        "gaps": gaps,
        "years": years,
        "semantic_gap": gap_result
    }

# --- ML-Based Skill Gap Analysis ---

# Optionally, keep the old semantic version for reference
def ml_skill_gap_analysis_semantic(cv_text, job_desc_text):
    cv_skills = extract_skills(cv_text)
    job_desc_skills = extract_skills(job_desc_text)
    return semantic_skill_gap_analysis(cv_skills, job_desc_skills)
