from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Example skill bank (expand as needed)
SKILL_BANK = [
    "python", "java", "sql", "machine learning", "aws", "excel", "c++", "javascript",
    "project management", "data analysis", "cloud", "backend", "frontend", "react", "nodejs",
    "docker", "linux", "git", "tensorflow", "pytorch", "nlp", "deep learning",
    "teaching", "lesson planning", "classroom management", "communication", "subject expertise",
    "assessment", "student engagement", "marketing", "seo", "content creation", "social media",
    "analytics", "branding", "campaign management", "api development", "data visualization",
    "statistics", "pandas"
]

# Load BERT model once
bert_model = None
def get_bert_model():
    global bert_model
    if bert_model is None:
        bert_model = SentenceTransformer('all-MiniLM-L6-v2')
    return bert_model

def embedding_skill_retrieval(job_desc, top_n=10, skill_bank=SKILL_BANK):
    """
    Given a job description, return top_n most semantically similar skills from the skill bank.
    """
    model = get_bert_model()
    job_emb = model.encode([job_desc])[0]
    skill_embs = model.encode(skill_bank)
    sims = cosine_similarity([job_emb], skill_embs)[0]
    top_idx = np.argsort(sims)[::-1][:top_n]
    return [skill_bank[i] for i in top_idx]
