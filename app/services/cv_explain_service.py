# Service to provide explainability for uploaded CVs
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
import shap
from app.services.cv_quality_score_service import preprocess_cv_text

# Load models
model = joblib.load(r'd:/Cv Project/ml_models/bert_cv_quality_best.pkl')
embedder = SentenceTransformer('all-MiniLM-L6-v2')
try:
    feature_model = joblib.load(r'd:/Cv Project/training score/cv_lr_model.pkl')
except Exception:
    feature_model = None

def explain_cv_score(cv_text):
    embedding = embedder.encode([cv_text])
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(embedding)
    pred = model.predict(embedding)[0]
    # Classic features
    classic_msg = ''
    if feature_model is not None:
        features = preprocess_cv_text(cv_text)
        # Dynamically match feature_labels to features
        default_labels = ["Skills mismatch", "Experience depth", "Project richness", "Keyword alignment", "Formatting", "Section Headings"]
        feature_labels = default_labels[:len(features)]
        if len(feature_labels) < len(features):
            # Add generic labels if needed
            feature_labels += [f"Feature {i+1}" for i in range(len(feature_labels), len(features))]
        try:
            importances = feature_model.coef_[0]
        except Exception:
            importances = [1]*len(features)
        contrib = np.abs(np.array(features) * np.array(importances))
        if contrib.sum() == 0:
            contrib = np.ones_like(contrib)
        contrib = contrib / contrib.sum()
        # Only use as many labels as features/contrib
        classic_msg = "\n".join([f"- {feature_labels[i]} ({int(round(100*contrib[i]))}%)" for i in np.argsort(-contrib)[:len(contrib)]])
    else:
        classic_msg = "- Top BERT embedding dimensions contributed most to this score."
    msg = f"Your CV score is explained as:\n{classic_msg}"
    return msg, pred
