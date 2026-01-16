import os
from flask import Flask, render_template, request
from utils.file_handler import extract_text
from db.connection import conn, cursor
import imgkit  # HTML → Image

# -----------------------------
# Flask App Setup
# -----------------------------
app = Flask(__name__, template_folder="templates")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
PROCESSED_FOLDER = os.path.join(os.path.dirname(__file__), "processed")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# -----------------------------
# wkhtmltoimage config (Windows)
# -----------------------------
WKHTMLTOIMAGE_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe"  # apna path
IMGKIT_CONFIG = imgkit.config(wkhtmltoimage=WKHTMLTOIMAGE_PATH)

# -----------------------------
# CV Upload & DB Insert
# -----------------------------
def upload_cv(user_id, file_path):
    file_name = os.path.basename(file_path)
    ext = os.path.splitext(file_name)[1].lower().replace('.', '')

    # Extract text
    try:
        text = extract_text(file_path)
    except Exception as e:
        print("Error extracting text:", e)
        return None, None

    # Insert CV metadata
    sql = "INSERT INTO CVs (user_id, file_name, file_type) VALUES (%s, %s, %s)"
    cursor.execute(sql, (user_id, file_name, ext))
    conn.commit()
    cv_id = cursor.lastrowid

    # Insert placeholder analysis
    sql_analysis = """
    INSERT INTO CV_Analysis (cv_id, job_category, quality_score, useful_content, useless_content, clusters, gap_analysis)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql_analysis, (cv_id, "Not Classified", 0.0, "[]", "[]", "[]", "[]"))
    conn.commit()

    return cv_id, text

# -----------------------------
# Render CV as one-page image
# -----------------------------
def render_cv_image(text, cv_id):
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial; margin: 20px; }}
            pre {{ white-space: pre-wrap; word-wrap: break-word; }}
            h2 {{ text-align: center; }}
        </style>
    </head>
    <body>
        <h2>CV ID: {cv_id}</h2>
        <pre>{text}</pre>
    </body>
    </html>
    """
    image_path = os.path.join(app.config['PROCESSED_FOLDER'], f"cv_{cv_id}.png")
    try:
        imgkit.from_string(html_content, image_path, options={'width': 1240}, config=IMGKIT_CONFIG)
    except Exception as e:
        print("Error generating image:", e)
        return None
    return image_path

# -----------------------------
# Routes
# -----------------------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'cv_file' not in request.files:
            return "No file uploaded!"
        file = request.files['cv_file']
        if file.filename == '':
            return "No selected file!"

        # Save file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Dummy user_id = 1
        user_id = 1
        cv_id, text = upload_cv(user_id, file_path)

        if cv_id:
            image_path = render_cv_image(text, cv_id)
            if image_path:
                return render_template("result.html", cv_id=cv_id, image_path=os.path.basename(image_path))
            else:
                return "Error generating CV image"
        else:
            return "Error processing CV"

    return render_template('index.html')

# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
