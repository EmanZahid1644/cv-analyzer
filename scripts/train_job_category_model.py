import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib
import re
from sentence_transformers import SentenceTransformer
import numpy as np

# 1. Load data
csv_path = r'd:/Cv Project/Resumes/Resume.csv'
df = pd.read_csv(csv_path)

# 2. Preprocess text (simple cleaning)
def clean_text(text):
    text = str(text)
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9 ]', ' ', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

df['Resume_clean'] = df['Resume_str'].apply(clean_text)

# 3. Prepare features and labels
X = df['Resume_clean']
y = df['Category']

# 4. Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 5. BERT Embeddings
print('Loading BERT model (all-MiniLM-L6-v2)...')
bert_model = SentenceTransformer('all-MiniLM-L6-v2')
print('Encoding training data...')
X_train_vec = bert_model.encode(X_train.tolist(), show_progress_bar=True)
print('Encoding test data...')
X_test_vec = bert_model.encode(X_test.tolist(), show_progress_bar=True)

# 6. Train model
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train_vec, y_train)

# 7. Evaluate
y_pred = model.predict(X_test_vec)
print('Accuracy:', accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# 8. Save model and BERT model name
joblib.dump(model, r'd:/Cv Project/ml_models/job_category_model.pkl')
with open(r'd:/Cv Project/ml_models/bert_model_name.txt', 'w') as f:
    f.write('all-MiniLM-L6-v2')
print('Model and BERT model name saved!')

# Show all unique roles/categories in the dataset
print('Unique job categories in Resume.csv:')
print(sorted(df['Category'].unique()))

# NOTE: To use this model for prediction, load the same BERT model and use encode() on new CVs before passing to model.predict().
# Install sentence-transformers if not already: pip install sentence-transformers