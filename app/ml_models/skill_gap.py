from app.ml_models.embedding_skill_retrieval import embedding_skill_retrieval

def hybrid_skill_extraction(job_desc, top_n=10):
    """
    Hybrid approach: combine embedding-based retrieval and ML classifier for skill prediction.
    1. Use embedding retrieval to get top-N semantic skills.
    2. Use ML classifier to get predicted skills.
    3. Combine (union) both sets for final prediction.
    """
    # Step 1: Embedding-based retrieval
    retrieved_skills = set(embedding_skill_retrieval(job_desc, top_n=top_n))
    # Step 2: ML classifier prediction
    ml_pred_skills = set(predict_required_skills_ml(job_desc))
    # Step 3: Union
    final_skills = sorted(retrieved_skills | ml_pred_skills)
    return {
        "embedding_skills": sorted(retrieved_skills),
        "ml_pred_skills": sorted(ml_pred_skills),
        "final_skills": final_skills
    }
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load BERT model once
bert_model = None
def get_bert_model():
    global bert_model
    if bert_model is None:
        bert_model = SentenceTransformer('all-MiniLM-L6-v2')
    return bert_model

def semantic_skill_gap_analysis(cv_skills, job_desc_skills):
    """
    Compare CV skills and job description skills using semantic similarity (BERT embeddings).
    Returns: required_skills, present_skills, missing_skills, similarity_scores
    """
    model = get_bert_model()
    # Embed required skills
    req_embs = model.encode(job_desc_skills)
    # Embed CV candidate phrases
    cv_embs = model.encode(cv_skills)
    present_skills = []
    missing_skills = []
    similarity_scores = {}
    threshold = 0.82  # Increased for stricter matching
    for i, req_skill in enumerate(job_desc_skills):
        req_emb = req_embs[i]
        # Compute similarity to all CV phrases
        sims = cosine_similarity([req_emb], cv_embs)[0]
        best_score = sims.max() if len(sims) > 0 else 0.0
        similarity_scores[req_skill] = best_score
        if best_score > threshold:
            present_skills.append(req_skill)
        else:
            missing_skills.append(req_skill)
    return {
        "required_skills": job_desc_skills,
        "present_skills": present_skills,
        "missing_skills": missing_skills,
        "similarity_scores": similarity_scores
    }

# --- ML-based required skills prediction and skill gap analysis ---
from app.ml_models.role_to_skills_predict import predict_required_skills_ml
# Add this at the end of the file to allow direct execution for testing
if __name__ == "__main__":
    print("skill_gap.py loaded successfully. Add test code here if needed.")

def ml_skill_gap_analysis(cv_text, job_role_or_desc):
    """
    Use the trained ML model to predict required skills for a job role/description,
    then compare with CV skills to find present and missing skills.
    Returns: required_skills, present_skills, missing_skills
    """
    from .role_to_skills_predict import get_role_to_skills_mlb
    mlb = get_role_to_skills_mlb()
    skill_list = list(mlb.classes_)
    cv_skills = extract_skills(cv_text, skill_list=skill_list)
    required_skills = predict_required_skills_ml(job_role_or_desc)
    present_skills = [skill for skill in required_skills if skill in cv_skills]
    missing_skills = [skill for skill in required_skills if skill not in cv_skills]
    return {
        "required_skills": required_skills,
        "present_skills": present_skills,
        "missing_skills": missing_skills
    }
import re
import numpy as np
from sklearn.cluster import KMeans

def extract_skills(text, skill_list=None):
    """
    Extracts candidate phrases from CV text for semantic skill matching.
    Filters out short/generic phrases.
    """
    import re
    text_phrases = re.findall(r'\b[\w\-\(\)\/\+\.]+(?: [\w\-\(\)\/\+\.]+){0,3}\b', text)
    ignore_words = set([
        'and', 'or', 'the', 'of', 'in', 'on', 'to', 'for', 'by', 'at', 'is', 'as', 'with', 'a', 'an', 'be', 'are', 'was', 'were', 'it', 'from', 'that', 'this', 'but', 'not', 'has', 'have', 'had', 'will', 'can', 'may', 'do', 'does', 'did', 'so', 'if', 'then', 'than', 'which', 'who', 'whom', 'whose', 'how', 'what', 'when', 'where', 'why'
    ])
    filtered_phrases = []
    for phrase in text_phrases:
        phrase_clean = phrase.strip().lower()
        if len(phrase_clean) < 3:
            continue
        if phrase_clean in ignore_words:
            continue
        filtered_phrases.append(phrase.strip())
    return list(set(filtered_phrases))

def extract_experience_years(text):
	"""
	Extracts years of experience from CV text using regex.
	Returns a list of (year, description) tuples.
	"""
	exp_matches = re.findall(r'(\d{4})', text)
	return [int(year) for year in exp_matches if 1900 < int(year) < 2100]

def cluster_skills(skills, n_clusters=3):
    """
    Clusters skills using BERT embeddings for semantic grouping.
    Returns cluster labels and skill groups.
    """
    if not skills:
        return [], []
    # Get BERT embeddings for each skill
    model = SentenceTransformer('all-MiniLM-L6-v2')
    X = model.encode(skills)
    # KMeans clustering
    kmeans = KMeans(n_clusters=min(n_clusters, len(skills)), random_state=42)
    labels = kmeans.fit_predict(X)
    clusters = {}
    for label, skill in zip(labels, skills):
        clusters.setdefault(label, []).append(skill)
    return labels.tolist(), list(clusters.values())

def detect_gaps(years):
	years_sorted = sorted(set(years))
	gaps = []
	for i in range(1, len(years_sorted)):
		if years_sorted[i] - years_sorted[i-1] > 1:
			gaps.append((years_sorted[i-1], years_sorted[i]))
	return gaps
