# CV Enhancement & Skill-Gap Analysis System

A comprehensive Flask-based CV analyzer that identifies areas for improvement, performs skill-gap analysis, and enhances CVs with AI assistance.

## Features

✅ **CV Upload & Analysis**
- Accepts PDF and DOCX formats
- Extracts and clusters skills
- Analyzes useful vs. filler content
- Detects employment gaps
- Auto-classifies job category

✅ **Areas of Improvement**
- Identifies weak/missing CV sections
- Suggests structural improvements
- Recommends language enhancements
- Highlights missing quantifiable metrics

✅ **Skill-Gap Analysis**
- Compares user skills against job requirements
- Identifies missing skills
- Shows present vs. required skills for target roles

✅ **CV Enhancement & Rewriting**
- LLM-powered polishing (uses Google Generative AI)
- Incorporates selected missing skills
- Improves language and structure
- Fallback template-based enhancement

## Installation

```bash
# Clone or setup the project
cd "d:\Cv Project"

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration (Optional: For LLM Enhancement)

To enable AI-powered CV enhancement via Google Generative AI (Gemini):

1. Get a free API key: https://ai.google.dev/tutorials/python_quickstart
2. Set environment variable:
   ```powershell
   # Windows PowerShell
   $env:GOOGLE_API_KEY = "your-api-key-here"
   
   # Or in Command Prompt
   set GOOGLE_API_KEY=your-api-key-here
   ```

Without this, the system uses template-based enhancement (still very effective).

## Usage

```bash
python app.py
```

Then open: `http://localhost:5000`

### Workflow

1. **Upload CV** → PDF or DOCX file
2. **View Analysis** → Job category, skills extracted, useful/useless content ratio
3. **Review Areas of Improvement** → Get specific suggestions
4. **Run Skill-Gap Analysis** → Pick target role (Data Science, Marketing, etc.) or enter custom
5. **Select Missing Skills** → Choose which skills you actually have
6. **Get Enhanced CV** → AI-polished, skill-enriched version ready to use

## How It Works

### Areas of Improvement Analysis
- Checks Experience, Education, Projects, Summary sections
- Counts action verbs and quantifiable metrics
- Analyzes filler word ratio
- Provides specific, actionable suggestions

### Skill-Gap Analysis
- Extracts skills from explicit "Skills" section
- Falls back to lexicon-based detection across full CV
- Compares against job role requirements
- Shows exactly what's missing

### CV Enhancement (LLM)
- Uses Google's Gemini AI to rewrite and polish CV
- Incorporates user-selected skills naturally
- Improves language, structure, and ATS compatibility
- Preserves original content while strengthening presentation

### CV Enhancement (Template Fallback)
- Strengthens each section with templates
- Adds action verbs to experience bullets
- Consolidates and deduplicates skills
- Reorganizes sections for better flow

## Tech Stack

- **Backend**: Flask
- **NLP**: sentence-transformers, scikit-learn, NLTK
- **Text Extraction**: PyPDF2, python-docx
- **AI**: Google Generative AI (Gemini)
- **Visualization**: Matplotlib, Chart.js
- **Frontend**: HTML, JavaScript (Chart.js)

## Supported File Formats

- **PDF** (.pdf) — with OCR fallback for scanned PDFs
- **Word** (.docx)

## Notes

- All uploaded files are stored in the `uploads/` folder
- Generated visualizations are saved in `static/` folder
- The system is designed to work with any CV format/structure
- LLM enhancement is optional but recommended for best results
