import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load data
csv_path = r'd:/Cv Project/training score/ml_ready_cvs.csv'
df = pd.read_csv(csv_path)

# Features and target
feature_cols = [
    'skill_score', 'experience_depth', 'project_richness', 'keyword_alignment', 'formatting_balance'
]
# Create binary target: shortlisted = 1 if CV_score >= 50 else 0
df['shortlisted'] = (df['CV_score'] >= 50).astype(int)
target_col = 'shortlisted'

X = df[feature_cols]
y = df[target_col]

# Train Logistic Regression
logreg = LogisticRegression(max_iter=1000)
logreg.fit(X, y)
joblib.dump(logreg, r'd:/Cv Project/ml_models/shortlist_logistic.pkl')
print('Saved Logistic Regression model.')

# Train Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X, y)
joblib.dump(rf, r'd:/Cv Project/ml_models/shortlist_rf.pkl')
print('Saved Random Forest model.')
