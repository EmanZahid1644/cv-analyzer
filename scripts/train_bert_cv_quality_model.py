# Train BERT-based CV Quality Score Model
# This script extracts BERT embeddings for each CV, trains an MLP regressor, and saves the model.

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

# 1. Load labeled CV data (expects columns: 'Text', 'CV_score')
data_path = r'd:/Cv Project/training score/ml_ready_cvs.csv'
df = pd.read_csv(data_path)

# 2. Use the raw CV text for embeddings, and CV_score as target
df = df.dropna(subset=['Text', 'CV_score'])
texts = df['Text'].astype(str).tolist()
y = df['CV_score'].astype(float).tolist()

# 3. Load BERT model
bert_model = SentenceTransformer('all-MiniLM-L6-v2')

print('Extracting BERT embeddings for all CVs...')
X = bert_model.encode(texts, show_progress_bar=True)

# 4. Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Train MLP regressor
mlp = MLPRegressor(hidden_layer_sizes=(128, 64), max_iter=500, random_state=42)
mlp.fit(X_train, y_train)

# 6. Evaluate
y_pred = mlp.predict(X_test)
print('MLPRegressor - MSE:', mean_squared_error(y_test, y_pred))
print('MLPRegressor - R²:', r2_score(y_test, y_pred))

# 7. Save model
os.makedirs(r'd:/Cv Project/ml_models', exist_ok=True)
model_path = r'd:/Cv Project/ml_models/bert_cv_quality_mlp.pkl'
joblib.dump(mlp, model_path)
print(f'Model saved to {model_path}')
