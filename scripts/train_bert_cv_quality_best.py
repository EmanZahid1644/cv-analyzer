# Train and compare multiple regressors for BERT-based CV quality scoring
# Will save the best model as bert_cv_quality_best.pkl

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

# 1. Load labeled CV data
data_path = r'd:/Cv Project/training score/ml_ready_cvs.csv'
df = pd.read_csv(data_path)
df = df.dropna(subset=['Text', 'CV_score'])
texts = df['Text'].astype(str).tolist()
y = df['CV_score'].astype(float).tolist()

# 2. BERT embeddings
bert_model = SentenceTransformer('all-MiniLM-L6-v2')
print('Extracting BERT embeddings for all CVs...')
X = bert_model.encode(texts, show_progress_bar=True)

# 3. Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

results = {}
models = {}

# 4. MLPRegressor (tuned)
mlp = MLPRegressor(hidden_layer_sizes=(256,128,64), learning_rate_init=0.001, max_iter=2000, random_state=42, early_stopping=True, n_iter_no_change=20)
mlp.fit(X_train, y_train)
y_pred_mlp = mlp.predict(X_test)
results['MLPRegressor'] = r2_score(y_test, y_pred_mlp)
models['MLPRegressor'] = mlp
print(f"MLPRegressor R²: {results['MLPRegressor']:.3f}")

# 5. RandomForestRegressor
rf = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
results['RandomForestRegressor'] = r2_score(y_test, y_pred_rf)
models['RandomForestRegressor'] = rf
print(f"RandomForestRegressor R²: {results['RandomForestRegressor']:.3f}")

# 6. Select best model
best_model_name = max(results, key=results.get)
best_model = models[best_model_name]
print(f"Best model: {best_model_name} (R²={results[best_model_name]:.3f})")

# 7. Save best model
os.makedirs(r'd:/Cv Project/ml_models', exist_ok=True)
model_path = r'd:/Cv Project/ml_models/bert_cv_quality_best.pkl'
joblib.dump(best_model, model_path)
print(f'Best model saved to {model_path}')

# 8. (Optional) Save all models for comparison
joblib.dump(mlp, r'd:/Cv Project/ml_models/bert_cv_quality_mlp.pkl')
joblib.dump(rf, r'd:/Cv Project/ml_models/bert_cv_quality_rf.pkl')
