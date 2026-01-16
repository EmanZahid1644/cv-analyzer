import os
from utils.file_handler import extract_text
import mysql.connector

# -----------------------------
# 1️⃣ Database Connection
# -----------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ILovePakistan@786",  # Change to your root password
    database="cv_analysis_system"
)
cursor = conn.cursor(dictionary=True)
print("Connected to database!")

# -----------------------------
# 2️⃣ Upload CV & Extract Text
# -----------------------------
def upload_cv(user_id, file_path):
    file_name = os.path.basename(file_path)
    ext = os.path.splitext(file_name)[1].lower().replace('.', '')

    # Extract text
    try:
        text = extract_text(file_path)
    except Exception as e:
        print("Error extracting text:", e)
        return

    # Save CV metadata to CVs table
    sql = "INSERT INTO CVs (user_id, file_name, file_type) VALUES (%s, %s, %s)"
    cursor.execute(sql, (user_id, file_name, ext))
    conn.commit()
    cv_id = cursor.lastrowid
    print(f"CV uploaded! CV ID: {cv_id}")

    # Initial placeholder analysis
    sql_analysis = """
    INSERT INTO CV_Analysis (cv_id, job_category, quality_score, useful_content, useless_content, clusters, gap_analysis)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql_analysis, (
        cv_id,
        "Not Classified",      # job_category placeholder
        0.0,                   # quality_score placeholder
        "[]",                  # useful_content placeholder
        "[]",                  # useless_content placeholder
        "[]",                  # clusters placeholder
        "[]"                   # gap_analysis placeholder
    ))
    conn.commit()
    print(f"Initial CV analysis entry created for CV ID: {cv_id}")

    return cv_id, text

# -----------------------------
# 3️⃣ Example Usage
# -----------------------------
if __name__ == "__main__":
    user_id = 1  # Existing user in Users table
    file_path = r"D:\Cv Project\sample cv\eman zahid cv.pdf"

    # Call the function
    cv_id, extracted_text = upload_cv(user_id, file_path)

    print("Extracted Text (first 500 chars):\n", extracted_text[:500], "...")
