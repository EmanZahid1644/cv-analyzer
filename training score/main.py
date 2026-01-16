# Step 2: DOCX Resumes → Clean Text → CSV ready

# 1️⃣ Install library if needed
# pip install python-docx pandas

from docx import Document
import os
import pandas as pd

# ----------------------------
# 2️⃣ Folder path for DOCX resumes
# ----------------------------
folder_path = r"D:\training score\Resumes"   # <-- tumhara path yahan

# ----------------------------
# 3️⃣ Initialize storage
# ----------------------------
cv_texts = []

# ----------------------------
# 4️⃣ Loop over all DOCX files
# ----------------------------
for filename in os.listdir(folder_path):
    if filename.endswith(".docx"):
        file_path = os.path.join(folder_path, filename)
        doc = Document(file_path)
        
        # Extract all paragraphs
        full_text = ""
        for para in doc.paragraphs:
            full_text += para.text + " "
        
        # Clean text
        full_text = full_text.replace("\n", " ").strip()
        
        # Store in list as dict
        cv_texts.append({
            "CV_ID": filename,
            "Text": full_text
        })

# ----------------------------
# 5️⃣ Convert to DataFrame
# ----------------------------
df = pd.DataFrame(cv_texts)

# Optional: check first few entries
print(df.head())

# ----------------------------
# 6️⃣ Save to CSV (ML-ready for next step)
# ----------------------------
df.to_csv("clean_cvs.csv", index=False)

print("✅ All DOCX resumes processed and saved to 'clean_cvs.csv'")
