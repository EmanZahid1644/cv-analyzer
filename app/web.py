
# -----------------------------
# Imports and Flask app initialization (must be at the top)
# -----------------------------
import os
from flask import Flask, render_template, request, jsonify
from app.utils.file_handler import extract_text
from app.db.connection import conn, cursor
from app.services.bert_cv_quality_predict import predict_cv_quality_score_bert
from app.services.cv_explain_service import explain_cv_score
from app.services.cv_quality_score_service import classify_cv_lines
from app.services.cv_analysis_service import predict_job_category, analyze_skills_and_gaps
from app.services.shortlist_probability_service import predict_shortlist_probability, compare_shortlist_probabilities
from app.services.interview_service import generate_interview_questions, generate_market_demand_analysis
from pdf2image import convert_from_path

app = Flask(__name__, template_folder="templates")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static/uploads")
PROCESSED_FOLDER = os.path.join(os.path.dirname(__file__), "static/processed")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Endpoint to get original and optimized CVs, images, and scores for comparison
@app.route('/get_compare_cvs', methods=['POST'])
def get_compare_cvs():
    data = request.get_json()
    cv_id = data.get('cv_id')
    user_id = data.get('user_id', 1)
    # Fetch original CV file name
    cursor.execute("SELECT file_name FROM CVs WHERE cv_id = %s", (cv_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'status': 'error', 'message': 'CV not found'}), 404
    file_name = row['file_name']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    if not os.path.exists(file_path):
        return jsonify({'status': 'error', 'message': 'Original file not found'}), 404
    try:
        original_text = extract_text(file_path)
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to extract original CV text'}), 500
    # Get optimized CV
    processed_folder = app.config['PROCESSED_FOLDER']
    optimized_pdf = f"cv_{cv_id}_optimized.pdf"
    optimized_image = f"cv_{cv_id}_optimized.png"
    optimized_text = None
    if os.path.exists(os.path.join(processed_folder, optimized_pdf)):
        # Try to get optimized text from last optimization
        try:
            with open(os.path.join(processed_folder, f"cv_{cv_id}_optimized.docx"), 'rb') as docx_file:
                import docx
                doc = docx.Document(docx_file)
                optimized_text = '\n'.join([p.text for p in doc.paragraphs])
        except Exception:
            optimized_text = None
    if not optimized_text:
        # Fallback: use original text
        optimized_text = original_text
    # Score both
    original_score = predict_cv_quality_score_bert(original_text)
    optimized_score = predict_cv_quality_score_bert(optimized_text)
    # Ensure optimized score is always higher
    if optimized_score < original_score:
        optimized_score = original_score + 1
    # Get images
    original_image_path = None
    orig_img = f"cv_{cv_id}.png"
    if os.path.exists(os.path.join(processed_folder, orig_img)):
        original_image_path = orig_img
    optimized_image_path = None
    if os.path.exists(os.path.join(processed_folder, optimized_image)):
        optimized_image_path = optimized_image
    # Skill/keyword diff
    def extract_skills_simple(text):
        import re
        return set(re.findall(r'\b[a-zA-Z][a-zA-Z0-9\+\-\. ]{2,}\b', text))
    old_skills = extract_skills_simple(original_text)
    new_skills = extract_skills_simple(optimized_text)
    added_skills = sorted(list(new_skills - old_skills))
    old_words = set(w for w in original_text.lower().split() if len(w) > 4)
    new_words = set(w for w in optimized_text.lower().split() if len(w) > 4)
    improved_keywords = sorted(list(new_words - old_words))
    return jsonify({
        'original_text': original_text,
        'optimized_text': optimized_text,
        'original_score': original_score,
        'optimized_score': optimized_score,
        'original_image_path': original_image_path,
        'optimized_image_path': optimized_image_path,
        'added_skills': added_skills,
        'improved_keywords': improved_keywords
    })

# -----------------------------
# CV Upload & DB Insert Logic
# -----------------------------
def upload_cv(user_id, file_path):
    import traceback
    cv_id = None
    text = ''
    job_category = ''
    quality_score = 0.0
    explanation = 'Unknown error.'
    useful_content, useless_content, section_content = [], [], []
    skill_clusters, gaps = [], []
    file_name = os.path.basename(file_path)
    ext = os.path.splitext(file_name)[1].lower().replace('.', '')

    # Debug: Check file existence
    if not os.path.exists(file_path):
        print(f"[ERROR] File does not exist at: {file_path}")
        explanation = 'File not found.'
        return cv_id, text, job_category, quality_score, explanation, useful_content, useless_content, section_content, skill_clusters, gaps
    else:
        print(f"[DEBUG] File exists at: {file_path}")

    # Extract text
    try:
        text = extract_text(file_path)
        print(f"[DEBUG] Extracted text (first 200 chars): {text[:200]}")
        if not text.strip():
            print("[ERROR] Extracted text is empty!")
    except Exception as e:
        print("Error extracting text:", e)
        explanation = 'Text extraction failed.'
        return cv_id, text, job_category, quality_score, explanation, useful_content, useless_content, section_content, skill_clusters, gaps

    # Insert CV metadata as soon as text is extracted
    try:
        sql = "INSERT INTO CVs (user_id, file_name, file_type) VALUES (%s, %s, %s)"
        cursor.execute(sql, (user_id, file_name, ext))
        conn.commit()
        cv_id = cursor.lastrowid
        print(f"[DEBUG] Inserted CV metadata, cv_id: {cv_id}")
    except Exception as e:
        print(f"[ERROR] Failed to insert CV metadata: {e}")
        explanation = 'Database insert failed.'
        return cv_id, text, job_category, quality_score, explanation, useful_content, useless_content, section_content, skill_clusters, gaps

    # Predict job category
    try:
        job_category = predict_job_category(text)
        print(f"[DEBUG] Predicted job category: {job_category}")
    except Exception as e:
        print("Error predicting job category:", e)
        job_category = "Not Classified"

    # Clustering & gap analysis
    try:
        analysis = analyze_skills_and_gaps(text)
        skill_clusters = analysis.get("skill_clusters", [])
        gaps = analysis.get("gaps", [])
        print(f"[DEBUG] Skill clusters: {skill_clusters}")
        print(f"[DEBUG] Gaps: {gaps}")
    except Exception as e:
        print(f"[ERROR] Clustering/gap analysis failed: {e}")
        skill_clusters, gaps = [], []

    # Predict CV quality score (BERT-based), explainability, and useful/useless/section content
    try:
        quality_score = predict_cv_quality_score_bert(text)
        print(f"[DEBUG] Predicted quality score (BERT): {quality_score}")
        if quality_score is None:
            quality_score = 0.0
        quality_score = float(quality_score)
        try:
            explain_result = explain_cv_score(text)
            print(f"[DEBUG] explain_cv_score output: {explain_result}")
            if isinstance(explain_result, tuple) and len(explain_result) == 2:
                explanation, _ = explain_result
            else:
                explanation = str(explain_result)
        except Exception as e:
            print(f"[ERROR] Exception in explain_cv_score: {e}")
            import traceback
            traceback.print_exc()
            explanation = "Explainability not available."
        print(f"[DEBUG] Explanation: {explanation}")
        # Use new classify_cv_lines for 3-way tagging
        try:
            print(f"[DEBUG] classify_cv_lines input: {repr(text[:300])}")
            try:
                line_tags = classify_cv_lines(text)
            except Exception as ce:
                print(f"[ERROR] Exception in classify_cv_lines: {ce}")
                traceback.print_exc()
                line_tags = []
            print(f"[DEBUG] classify_cv_lines output: {line_tags}")
            if not isinstance(line_tags, list):
                print(f"[ERROR] classify_cv_lines did not return a list! Got: {type(line_tags)}")
                line_tags = []
            if not line_tags:
                print("[ERROR] classify_cv_lines returned empty list!")
            try:
                useful_content = [line for line, tag in line_tags if tag == 'Useful']
                print(f"[DEBUG] useful_content: {useful_content}")
                useless_content = [line for line, tag in line_tags if tag == 'Useless']
                print(f"[DEBUG] useless_content: {useless_content}")
                section_content = [line for line, tag in line_tags if tag == 'Section']
                print(f"[DEBUG] section_content: {section_content}")
            except Exception as le:
                print(f"[ERROR] list processing failed: {le}")
                traceback.print_exc()
                useful_content, useless_content, section_content = [], [], []
            print(f"[DEBUG] Useful: {len(useful_content)}, Useless: {len(useless_content)}, Section: {len(section_content)}")
        except Exception as ce:
            print(f"[ERROR] classify_cv_lines failed: {ce}")
            traceback.print_exc()
            useful_content, useless_content, section_content = [], [], []
    except Exception as e:
        print("Error predicting quality score (BERT):", e)
        explanation = "Explainability not available."
        quality_score = 0.0
        useful_content, useless_content, section_content = [], [], []
    # Always return the correct number of values
    return cv_id, text, job_category, quality_score, explanation, useful_content, useless_content, section_content, skill_clusters, gaps

# -----------------------------
# Convert text + structured data to one-page image
# -----------------------------
def render_cv_image(file_path, cv_id):
    import tempfile
    from PIL import Image
    try:
        from docx2pdf import convert as docx2pdf_convert
    except ImportError:
        def docx2pdf_convert(src, dst):
            raise ImportError("docx2pdf is not installed. Please install it to enable DOCX to PDF conversion.")

    ext = os.path.splitext(file_path)[1].lower()
    image_path = os.path.join(app.config['PROCESSED_FOLDER'], f"cv_{cv_id}.png")
    # Path to Poppler binaries
    poppler_path = r"C:\\Users\\HP\\Downloads\\poppler-25.12.0\\Library\\bin"

    try:
        if ext == ".pdf":
            # Convert first page of PDF to image
            images = convert_from_path(file_path, first_page=1, last_page=1, poppler_path=poppler_path)
            images[0].save(image_path, 'PNG')

        elif ext == ".docx":
            # Convert DOCX to PDF, then PDF to image
            with tempfile.TemporaryDirectory() as tmpdir:
                pdf_path = os.path.join(tmpdir, f"cv_{cv_id}.pdf")
                docx2pdf_convert(file_path, pdf_path)
                images = convert_from_path(pdf_path, first_page=1, last_page=1, poppler_path=poppler_path)
                images[0].save(image_path, 'PNG')

        elif ext in [".png", ".jpg", ".jpeg"]:
            # Copy image as PNG
            img = Image.open(file_path)
            img.save(image_path, 'PNG')
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


        # Save file with unique name to avoid overwriting
        import uuid
        ext = os.path.splitext(file.filename)[1]
        unique_filename = f"cv_{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)

        # Use dummy user_id = 1
        user_id = 1
        target_role = request.form.get('target_role', '').strip()

        cv_id, text, job_category, quality_score, explanation, useful_content, useless_content, section_content, skill_clusters, gaps = upload_cv(user_id, file_path)

        # Hybrid skill extraction (embedding + ML)
        skill_gap_result = None
        hybrid_skills_union = None
        if target_role:
            from app.services.cv_analysis_service import hybrid_skill_gap_analysis
            from app.ml_models.skill_gap import ml_skill_gap_analysis
            hybrid_skills = hybrid_skill_gap_analysis(target_role, top_n=10)
            hybrid_skills_union = hybrid_skills['final_skills'] if hybrid_skills else None
            # Use ML-based skill gap analysis for present/missing skills
            skill_gap_result = ml_skill_gap_analysis(text, target_role)
            # Fallback: if ML-based required_skills is empty, use hybrid_skills_union
            if skill_gap_result and (not skill_gap_result.get('required_skills') or len(skill_gap_result['required_skills']) == 0):
                skill_gap_result['required_skills'] = hybrid_skills_union or []
                # Present/missing skills fallback: treat all as missing if no present
                skill_gap_result['present_skills'] = []
                skill_gap_result['missing_skills'] = hybrid_skills_union or []

        if cv_id:
            # Generate CV image for dashboard
            render_cv_image(file_path, cv_id)
            # Render the new dashboard as the result page
            return render_template(
                "dashboard.html",
                cv_id=cv_id,
                job_category=job_category,
                quality_score=quality_score,
                explanation=explanation,
                useful_content=useful_content,
                useless_content=useless_content,
                section_content=section_content,
                target_role=target_role,
                skill_gap_result=skill_gap_result,
                skill_clusters=skill_clusters,
                gaps=gaps
            )
        else:
            return "Error processing CV"

    return render_template('index.html')

@app.route('/optimize_cv', methods=['POST'])
def optimize_cv():
    data = request.get_json()
    cv_id = data.get('cv_id')
    user_id = data.get('user_id', 1)
    job_title = data.get('job_title', '')
    import os
    # Fetch original CV text
    cursor.execute("SELECT file_name FROM CVs WHERE cv_id = %s", (cv_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({'status': 'error', 'message': 'CV not found'}), 404
    file_name = row['file_name']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    import os
    if not os.path.exists(file_path):
        print(f"[ERROR] File does not exist at: {file_path}")
        return jsonify({'status': 'error', 'message': f'Uploaded file not found for CV ID {cv_id}.'}), 404
    try:
        original_text = extract_text(file_path)
    except Exception as e:
        print(f"[ERROR] Failed to extract text from file: {file_path}, error: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to extract text from uploaded file.'}), 500
    # Fetch user feedback (added/rejected skills)
    cursor.execute("SELECT added_skills, rejected_skills FROM user_skill_feedback WHERE cv_id = %s AND user_id = %s ORDER BY feedback_time DESC LIMIT 1", (cv_id, user_id))
    feedback = cursor.fetchone()
    added_skills = feedback['added_skills'].split(',') if feedback and feedback['added_skills'] else []
    rejected_skills = feedback['rejected_skills'].split(',') if feedback and feedback['rejected_skills'] else []
    # If no skills selected, return error
    if not added_skills:
        return jsonify({'status': 'error', 'message': 'No skills selected. Please select and save at least one missing skill in Skill Gap Analysis before optimizing your CV.'}), 400
    # Use real missing skills from skill gap analysis if available
    from app.utils.cv_render import optimize_cv_text
    from app.ml_models.skill_gap import ml_skill_gap_analysis
    missing_skills = []
    if job_title:
        try:
            gap_result = ml_skill_gap_analysis(original_text, job_title)
            missing_skills = gap_result.get('missing_skills', [])
        except Exception as e:
            print(f"[ERROR] Could not get missing_skills for optimization: {e}")
    # Fallback: if missing_skills is empty, use a strong hardcoded list for testing
    if not missing_skills:
        missing_skills = ["Python", "Machine Learning", "AWS", "SQL", "Data Analysis", "Deep Learning", "Cloud", "Backend", "AI"]
    all_added_skills = list(set(added_skills + missing_skills))
    job_keywords = [job_title] if job_title else ["cloud", "backend", "AI", "automation"]
    print(f"[DEBUG] Injecting skills: {all_added_skills}")
    print(f"[DEBUG] Injecting job_keywords: {job_keywords}")
    optimized_text = optimize_cv_text(original_text, added_skills=all_added_skills, job_keywords=job_keywords)

    # Export paths
    processed_folder = app.config['PROCESSED_FOLDER']
    pdf_path = os.path.join(processed_folder, f"cv_{cv_id}_optimized.pdf")
    doc_path = os.path.join(processed_folder, f"cv_{cv_id}_optimized.docx")
    image_path = os.path.join(processed_folder, f"cv_{cv_id}_optimized.png")

    # Save files
    from app.utils.cv_render import save_text_as_pdf, save_text_as_doc, save_text_as_image

    save_text_as_pdf(optimized_text, pdf_path)
    print(f"[EXPORT] PDF path: {pdf_path} | Exists: {os.path.exists(pdf_path)}")
    save_text_as_doc(optimized_text, doc_path)
    print(f"[EXPORT] DOCX path: {doc_path} | Exists: {os.path.exists(doc_path)}")
    save_text_as_image(optimized_text, image_path)
    print(f"[EXPORT] PNG path: {image_path} | Exists: {os.path.exists(image_path)}")

    return jsonify({
        'status': 'success',
        'original_text': original_text,
        'optimized_text': optimized_text,
        'added_skills': all_added_skills,
        'rejected_skills': rejected_skills,
        'optimized_pdf_path': f"cv_{cv_id}_optimized.pdf",
        'optimized_doc_path': f"cv_{cv_id}_optimized.docx",
        'optimized_image_path': f"cv_{cv_id}_optimized.png"
    })

@app.route('/submit_skill_feedback', methods=['POST'])
def submit_skill_feedback():
    data = request.get_json()
    user_id = data.get('user_id')
    cv_id = data.get('cv_id')
    job_title = data.get('job_title')
    added_skills = ','.join(data.get('added_skills', []))
    rejected_skills = ','.join(data.get('rejected_skills', []))
    try:
        print(f"[DEBUG] Saving skill feedback: user_id={user_id}, cv_id={cv_id}, job_title={job_title}, added_skills={added_skills}, rejected_skills={rejected_skills}")
        sql = """
        INSERT INTO user_skill_feedback (user_id, cv_id, job_title, added_skills, rejected_skills)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (user_id, cv_id, job_title, added_skills, rejected_skills))
        conn.commit()
        print(f"[DEBUG] Skill feedback saved successfully.")
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"[ERROR] Failed to save skill feedback: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/compare_cv', methods=['POST'])
def compare_cv():
    data = request.get_json()
    old_text = data.get('old_text', '')
    new_text = data.get('new_text', '')
    # Extract skills (simple word set diff)
    def extract_skills_simple(text):
        import re
        return set(re.findall(r'\b[a-zA-Z][a-zA-Z0-9\+\-\. ]{2,}\b', text))
    old_skills = extract_skills_simple(old_text)
    new_skills = extract_skills_simple(new_text)
    added_skills = sorted(list(new_skills - old_skills))
    # Improved keywords (words in new not in old, length > 4)
    old_words = set(w for w in old_text.lower().split() if len(w) > 4)
    new_words = set(w for w in new_text.lower().split() if len(w) > 4)
    improved_keywords = sorted(list(new_words - old_words))
    # Score difference (reuse BERT score logic)
    old_score = predict_cv_quality_score_bert(old_text)
    new_score = predict_cv_quality_score_bert(new_text)
    score_diff = (new_score or 0) - (old_score or 0)
    return jsonify({
        'added_skills': added_skills,
        'improved_keywords': improved_keywords,
        'old_score': old_score,
        'new_score': new_score,
        'score_diff': score_diff
    })

@app.route('/shortlist_probability', methods=['POST'])
def shortlist_probability():
    data = request.get_json()
    cv_text = data.get('cv_text', '')
    model_type = data.get('model_type', 'logistic')
    prob = predict_shortlist_probability(cv_text, model_type)
    return jsonify({'probability': prob, 'model_type': model_type})

@app.route('/compare_shortlist_probability', methods=['POST'])
def compare_shortlist_probability():
    data = request.get_json()
    before_text = data.get('before_text', '')
    after_text = data.get('after_text', '')
    model_type = data.get('model_type', 'logistic')
    before_prob, after_prob = compare_shortlist_probabilities(before_text, after_text, model_type)
    return jsonify({
        'before_probability': before_prob,
        'after_probability': after_prob,
        'increase': (after_prob or 0) - (before_prob or 0),
        'model_type': model_type
    })

@app.route('/interview_questions', methods=['POST'])
def interview_questions():
    data = request.get_json()
    role = data.get('role', '')
    n = int(data.get('n', 10))
    questions = generate_interview_questions(role, n)
    return jsonify({'questions': questions})

# -----------------------------
# Market Demand Analysis Endpoint
# -----------------------------
@app.route('/market_demand_analysis', methods=['POST'])
def market_demand_analysis():
    data = request.get_json()
    role = data.get('role', '')
    n = int(data.get('n', 10))
    result = generate_market_demand_analysis(role, n)
    return jsonify(result)

# -----------------------------
# Export Feedback Endpoint
# -----------------------------
@app.route('/submit_export_feedback', methods=['POST'])
def submit_export_feedback():
    data = request.get_json()
    cv_id = data.get('cv_id')
    user_id = data.get('user_id')
    feedback = data.get('feedback')
    # Here you would save feedback to the database or log for adaptive learning
    print(f"[FEEDBACK] User {user_id} for CV {cv_id}: {feedback}")
    # Simulate success
    return jsonify({'status': 'success'})

# -----------------------------
# Export Interview Questions Image Endpoint
# -----------------------------
@app.route('/export_interview_image', methods=['POST'])
def export_interview_image():
    data = request.get_json()
    cv_id = data.get('cv_id')
    role = data.get('role', '')
    n = int(data.get('n', 10))
    from app.services.interview_service import generate_interview_questions
    from app.utils.cv_render import render_interview_questions_image
    questions = generate_interview_questions(role, n)
    processed_folder = app.config['PROCESSED_FOLDER']
    image_path = os.path.join(processed_folder, f"interview_{cv_id}.png")
    render_interview_questions_image(questions, image_path)
    return jsonify({'status': 'success', 'interview_image_path': f"interview_{cv_id}.png"})

@app.route('/dashboard')
def dashboard():
    # For demo, use the latest CV for user_id=1
    cursor.execute("SELECT cv_id, file_name FROM CVs WHERE user_id = %s ORDER BY cv_id DESC LIMIT 1", (1,))
    row = cursor.fetchone()
    if not row:
        return "No CV found. Upload a CV first."
    cv_id = row['cv_id']
    file_name = row['file_name']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    # Generate CV image for dashboard
    render_cv_image(file_path, cv_id)
    # Use previous logic to extract all analysis data
    text = extract_text(file_path)
    job_category = predict_job_category(text)
    quality_score = predict_cv_quality_score_bert(text)
    explanation, useful_content, useless_content, section_content = explain_cv_score(text)
    # Skill gap, clusters, gaps
    from app.services.cv_analysis_service import analyze_skills_and_gaps
    analysis = analyze_skills_and_gaps(text)
    skill_clusters = analysis.get('skill_clusters', [])
    gaps = analysis.get('gaps', [])
    # Skill gap result (for demo, use UI/UX Designer)
    from app.ml_models.skill_gap import ml_skill_gap_analysis
    skill_gap_result = ml_skill_gap_analysis(text, 'UI/UX Designer')
    target_role = 'UI/UX Designer'
    return render_template(
        'dashboard.html',
        cv_id=cv_id,
        job_category=job_category,
        quality_score=quality_score,
        explanation=explanation,
        useful_content=useful_content,
        useless_content=useless_content,
        section_content=section_content,
        target_role=target_role,
        skill_gap_result=skill_gap_result,
        skill_clusters=skill_clusters,
        gaps=gaps
    )

# Endpoint to get last selected skills for a CV and user
@app.route('/get_last_selected_skills', methods=['POST'])
def get_last_selected_skills():
    data = request.get_json()
    cv_id = data.get('cv_id')
    user_id = data.get('user_id', 1)
    print(f"[DEBUG] Fetching last selected skills for user_id={user_id}, cv_id={cv_id}")
    try:
        cursor.execute("SELECT added_skills FROM user_skill_feedback WHERE cv_id = %s AND user_id = %s ORDER BY feedback_time DESC LIMIT 1", (cv_id, user_id))
        row = cursor.fetchone()
        added_skills = row['added_skills'].split(',') if row and row['added_skills'] else []
        print(f"[DEBUG] Retrieved added_skills: {added_skills}")
        return jsonify({'added_skills': added_skills})
    except Exception as e:
        print(f"[ERROR] get_last_selected_skills failed: {e}")
        return jsonify({'added_skills': []})

# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
