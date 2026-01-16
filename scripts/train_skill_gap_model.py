# Train skill gap model using skills_data - skills_data.csv
# This script creates a MultiLabelBinarizer for skills and saves it for use in skill gap analysis.

import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
import joblib
import os

# 1. Load skills data
csv_path = r'd:/Cv Project/skill training/skills_data - skills_data.csv'
df = pd.read_csv(csv_path)

# 2. Parse skills
# Each row: job_role, skills (comma-separated)
roles = df['job title']
skills = df['skills'].apply(lambda x: [s.strip() for s in str(x).split(',')])

# 3. Fit MultiLabelBinarizer
mlb = MultiLabelBinarizer()
mlb.fit(skills)

# 4. Save MLB
os.makedirs(r'd:/Cv Project/ml_models', exist_ok=True)
mlb_path = r'd:/Cv Project/ml_models/role_to_skills_mlb.joblib'
joblib.dump(mlb, mlb_path)
print(f'MultiLabelBinarizer saved to {mlb_path}')

# 5. Save all unique skills for reference
with open(r'd:/Cv Project/ml_models/all_skills.txt', 'w') as f:
    for skill in sorted(mlb.classes_):
        f.write(skill + '\n')
print('All unique skills saved to all_skills.txt')
