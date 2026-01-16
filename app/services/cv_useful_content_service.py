# Useful vs Useless Content Analysis for CVs
# Splits CV into sentences, classifies each as useful or useless using embeddings + ML

import re
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression

# Load or train a simple classifier (for demo, you can retrain with your own data)
try:
    clf = joblib.load(r'd:/Cv Project/ml_models/cv_sentence_usefulness_clf.pkl')
except Exception:
    clf = None  # Will fallback to rule-based if not found

embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Example rule-based fallback (for demo)
def rule_based_useful(sentence):
    # Broader set of technical/action/impact keywords
    keywords = [
        "experience", "project", "developed", "achieved", "managed", "skills", "education", "certification", "responsible", "analysis", "designed", "implemented", "award", "publication", "research",
        "engineered", "optimized", "improved", "reduced", "increased", "boosted", "led", "mentored", "reviewed", "integrated", "collaborated", "deployed", "launched", "built", "created", "enhanced", "resolved", "contributed", "delivered", "coordinated", "streamlined", "automated", "performance", "scalable", "api", "cloud", "aws", "azure", "gcp", "react", "node", "python", "typescript", "database", "sql", "matplotlib", "pandas", "saas", "b2b", "transactions", "deployment", "production", "team", "cross-functional", "agile", "scrum", "devops", "mentored", "reviewed", "best practices", "security", "compliance", "ci/cd", "testing", "debugged", "fixed", "bug", "issue", "feature", "requirement", "stakeholder", "user", "customer", "impact", "result", "outcome", "growth", "retention", "revenue", "cost", "efficiency", "scalability", "uptime", "availability", "reliability", "latency", "response time", "query", "indexing", "api", "endpoint", "integration", "stripe", "hubspot", "crm", "payment", "ux", "ui", "design", "accessibility", "consistency", "deployment", "production", "release", "sprint", "planning", "stand-up", "collaboration", "teamwork", "leadership", "ownership", "initiative", "award", "recognition", "commendation", "publication", "conference", "presentation", "workshop", "training", "certification", "language", "english", "urdu", "python", "react", "node", "express", "nestjs", "typescript", "material ui", "redux", "aws", "lambda", "s3", "cognito", "cloud", "gcp", "azure", "iot", "mqtt", "postgre", "sql", "mongodb", "parse", "matplotlib", "seaborn", "pandas", "scikit", "machine learning", "ai", "ml", "data", "analysis", "visualization", "insight", "report", "dashboard", "metric", "kpi", "result", "impact", "growth", "improvement", "optimization", "efficiency", "automation", "scalability", "performance", "security", "compliance", "testing", "debugging", "deployment", "production", "release", "support", "maintenance", "documentation", "training", "mentoring", "leadership", "collaboration", "communication", "stakeholder", "requirement", "user", "customer", "feedback", "iteration", "agile", "scrum", "kanban", "sprint", "planning", "stand-up", "retrospective", "demo", "presentation", "workshop", "conference", "award", "recognition", "commendation", "publication", "language", "english", "urdu"
    ]
    # Useful if contains numbers, %, $, or technical/impact keywords
    s = sentence.lower()
    if any(char.isdigit() for char in s) or any(sym in s for sym in ["%", "$", "+", "-"]):
        return True
    if any(kw in s for kw in keywords):
        return True
    # Useful if sentence is a bullet point and >40 chars
    if (s.strip().startswith("-") or s.strip().startswith("•")) and len(s) > 40:
        return True
    return False

def split_sentences(text):
    # Improved: split on newlines, bullets, and sentence end
    sents = re.split(r'[\n\r]+|(?<=[.!?])\s+|(?<=•)|(?<=- )', text.strip())
    # Remove empty and strip
    return [s.strip() for s in sents if s.strip()]

def analyze_useful_useless(text):
    sentences = split_sentences(text)
    useful, useless = [], []
    if clf is not None:
        embeddings = embedder.encode(sentences)
        preds = clf.predict(embeddings)
        for sent, label in zip(sentences, preds):
            (useful if label == 1 else useless).append(sent)
    else:
        # Fallback: rule-based
        for sent in sentences:
            if rule_based_useful(sent):
                useful.append(sent)
            else:
                useless.append(sent)
    return useful, useless

# Example usage:
if __name__ == "__main__":
    sample = """Experienced Python developer. Loves cricket. Developed ML models for finance. Managed a team of 5. Enjoys pizza. BSc in Computer Science."""
    useful, useless = analyze_useful_useless(sample)
    print("Useful:", useful)
    print("Useless:", useless)
