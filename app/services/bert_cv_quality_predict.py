import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

# Load models
best_model = joblib.load(r'd:/Cv Project/ml_models/bert_cv_quality_best.pkl')
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Predict function for a single CV text
def predict_cv_quality_score_bert(cv_text):
    embedding = embedder.encode([cv_text])
    score = best_model.predict(np.array(embedding))[0]
    score = max(0, min(100, score))
    return round(float(score), 2)

# Example usage:
# cv_text = 'Paste or load your CV text here.'
# print(predict_cv_quality_score_bert(cv_text))
