import pandas as pd
import re
# Optional: for embeddings
# from sentence_transformers import SentenceTransformer

# ----------------------------
# 1️⃣ Read clean CVs CSV
# ----------------------------
df = pd.read_csv("clean_cvs.csv")

# Optional: initialize embedding model
# model = SentenceTransformer('all-MiniLM-L6-v2')

# ----------------------------
# 2️⃣ Define target job skills & keywords
# ----------------------------
target_skills = ["Python", "Java", "Machine Learning", "SQL", "AWS"]  # example
job_keywords = ["ML", "AI", "Backend", "Cloud", "Project"]  # example

# ----------------------------
# 3️⃣ Initialize feature columns
# ----------------------------
df["skill_score"] = 0.0
df["experience_depth"] = 0.0
df["project_richness"] = 0.0
df["keyword_alignment"] = 0.0
df["formatting_balance"] = 0.0
# df["embedding"] = None  # optional

# ----------------------------
# 4️⃣ Feature extraction loop
# ----------------------------
for idx, row in df.iterrows():
    text = str(row["Text"])
    
    # ---- Skill relevance ----
    skills_in_cv = set(re.findall(r'\b\w+\b', text))
    skill_match = len(skills_in_cv & set(target_skills))
    skill_score = skill_match / len(target_skills)
    df.at[idx, "skill_score"] = skill_score
    
    # ---- Experience depth ----
    # Simple heuristic: count 'years' or numbers near 'experience'
    experience_matches = re.findall(r'(\d+)\s+(years|yrs|year)', text, flags=re.I)
    experience_years = sum([int(match[0]) for match in experience_matches])
    df.at[idx, "experience_depth"] = experience_years
    
    # ---- Project richness ----
    # Count 'project' mentions as simple proxy
    project_count = len(re.findall(r'\bproject\b', text, flags=re.I))
    df.at[idx, "project_richness"] = project_count
    
    # ---- Keyword alignment ----
    keywords_in_cv = set(re.findall(r'\b\w+\b', text))
    keyword_match = len(keywords_in_cv & set(job_keywords))
    keyword_score = keyword_match / len(job_keywords)
    df.at[idx, "keyword_alignment"] = keyword_score
    
    # ---- Formatting balance (simple proxy) ----
    bullet_points = len(re.findall(r'[-*•]', text))
    sections = len(re.findall(r'\bexperience\b|\beducation\b|\bprojects\b', text, flags=re.I))
    formatting_score = (bullet_points/10 + sections/3) / 2  # simple heuristic
    df.at[idx, "formatting_balance"] = min(formatting_score, 1.0)
    
    # ---- Optional embeddings ----
    # embedding_vector = model.encode(text)
    # df.at[idx, "embedding"] = embedding_vector.tolist()

# ----------------------------
# 5️⃣ Assign initial CV score (heuristic)
# ----------------------------
df["CV_score"] = (
    0.4*df["skill_score"] +
    0.3*(df["experience_depth"]/30) +   # normalize years
    0.2*df["project_richness"]/10 +     # normalize projects
    0.1*df["formatting_balance"]
) * 100
df["CV_score"] = df["CV_score"].clip(0, 100)
# ----------------------------
# 6️⃣ Save ML-ready CSV
# ----------------------------
df.to_csv("ml_ready_cvs.csv", index=False)
print("✅ ML-ready dataset saved to 'ml_ready_cvs.csv'")
