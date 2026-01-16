# CV Impact Attribution (Explainability Engine)
# Explains model decisions using feature importance and SHAP values for RandomForest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import joblib
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import shap

# Load best model and BERT embedder
model = joblib.load(r'd:/Cv Project/ml_models/bert_cv_quality_best.pkl')
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Optionally, load feature-based model for classic explainability
try:
    feature_model = joblib.load(r'd:/Cv Project/training score/cv_lr_model.pkl')
except Exception:
    feature_model = None

# Explain a single CV

def explain_cv_score(cv_text, feature_names=None):
    embedding = embedder.encode([cv_text])
    # SHAP for RandomForest
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(embedding)
    base_value = explainer.expected_value
    pred = model.predict(embedding)[0]
    # If feature_names not provided, use generic
    if feature_names is None:
        feature_names = [f'BERT_{i}' for i in range(embedding.shape[1])]
    # Get top contributing BERT dimensions (not human-friendly)
    top_idx = np.argsort(np.abs(shap_values[0]))[::-1][:3]
    top_contribs = [(feature_names[i], shap_values[0][i]) for i in top_idx]
    # For user-friendly output, fallback to classic features if available
    classic_msg = ''
    if feature_model is not None:
        # Try to extract classic features
        from app.services.cv_quality_score_service import preprocess_cv_text
        features = preprocess_cv_text(cv_text)
        feature_labels = ["Skills mismatch", "Experience depth", "Project richness", "Keyword alignment", "Formatting"]
        # Use feature_model.coef_ if linear, else fallback to feature importances
        try:
            importances = feature_model.coef_[0]
        except Exception:
            importances = [1]*len(features)
        contrib = np.abs(np.array(features) * np.array(importances))
        contrib = contrib / contrib.sum()
        classic_msg = "\n".join([f"- {feature_labels[i]} ({int(round(100*contrib[i]))}%)" for i in np.argsort(-contrib)])
    else:
        classic_msg = "- Top BERT embedding dimensions contributed most to this score."
    # Compose message
    msg = f"Your CV score is explained as:\n{classic_msg}"
    return msg, pred

# Example usage:
if __name__ == "__main__":
    sample_text = "Experienced Python developer with strong ML background. Led 5 projects. Skills: Python, SQL, AWS."
    explanation, score = explain_cv_score(sample_text)
    print(f"Predicted Score: {score:.2f}")
    print(explanation)
