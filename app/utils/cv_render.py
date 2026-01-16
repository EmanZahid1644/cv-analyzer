# --- Export Utilities ---
from fpdf import FPDF
from docx import Document
from PIL import Image, ImageDraw, ImageFont
import os

def save_text_as_pdf(text, output_path):
	pdf = FPDF()
	pdf.add_page()
	pdf.set_auto_page_break(auto=True, margin=15)
	pdf.set_font("Arial", size=12)
	section_titles = [
		'SUMMARY', 'CAREER OBJECTIVE', 'WORK EXPERIENCE', 'TECHNICAL  SKILLS', 'PROJECTS', 'EDUCATION', 'CERTIFICATIONS', 'LANGUAGES', 'SKILLS', 'EXPERIENCE', 'OBJECTIVE'
	]
	def clean_ascii(s):
		# Replace en-dash, em-dash, and other special dashes with ASCII dash
		s = s.replace('–', '-').replace('—', '-').replace('−', '-')
		# Replace special quotes with ASCII quotes
		s = s.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
		# Replace bullet and similar with dash
		s = s.replace('•', '-').replace('·', '-')
		# Replace question mark-like unicode with '?'
		s = s.replace('？', '?')
		# Remove any other non-latin1 chars
		return s.encode('latin-1', 'replace').decode('latin-1')

	for line in text.splitlines():
		safe_line = clean_ascii(line)
		stripped = safe_line.strip()
		# Only bold if line is a section heading (not underline or blank)
		if stripped and stripped.upper() in section_titles:
			pdf.set_font("Arial", style="B", size=12)
			pdf.cell(0, 10, safe_line, ln=True)
			pdf.set_font("Arial", style="", size=12)
		else:
			pdf.set_font("Arial", style="", size=12)
			pdf.cell(0, 10, safe_line, ln=True)
	pdf.output(output_path)
	return output_path

def save_text_as_doc(text, output_path):
	doc = Document()
	section_titles = [
		'SUMMARY', 'CAREER OBJECTIVE', 'WORK EXPERIENCE', 'TECHNICAL  SKILLS', 'PROJECTS', 'EDUCATION', 'CERTIFICATIONS', 'LANGUAGES', 'SKILLS', 'EXPERIENCE', 'OBJECTIVE'
	]
	for line in text.splitlines():
		stripped = line.strip()
		if stripped and stripped.upper() in section_titles:
			p = doc.add_paragraph()
			run = p.add_run(line)
			run.bold = True
		else:
			doc.add_paragraph(line)
	doc.save(output_path)
	return output_path

def save_text_as_image(text, output_path, font_path=None, width=900, height=1200):
	font_path = font_path or "arial.ttf"
	img = Image.new('RGB', (width, height), color = (255, 255, 255))
	d = ImageDraw.Draw(img)
	try:
		font = ImageFont.truetype(font_path, 18)
		font_bold = ImageFont.truetype(font_path, 18)
	except:
		font = ImageFont.load_default()
		font_bold = font
	section_titles = [
		'SUMMARY', 'CAREER OBJECTIVE', 'WORK EXPERIENCE', 'TECHNICAL  SKILLS', 'PROJECTS', 'EDUCATION', 'CERTIFICATIONS', 'LANGUAGES', 'SKILLS', 'EXPERIENCE', 'OBJECTIVE'
	]
	lines = text.splitlines()
	y = 30
	for line in lines:
		stripped = line.strip()
		if stripped and stripped.upper() in section_titles:
			d.text((30, y), line, font=font_bold, fill=(0,0,0))
		else:
			d.text((30, y), line, font=font, fill=(30,30,30))
		y += 28
	img.save(output_path)
	return output_path

def render_interview_questions_image(questions, output_path, font_path=None, width=900, height=600):
	font_path = font_path or "arial.ttf"
	img = Image.new('RGB', (width, height), color = (255, 255, 255))
	d = ImageDraw.Draw(img)
	try:
		font = ImageFont.truetype(font_path, 20)
	except:
		font = ImageFont.load_default()
	y = 30
	d.text((30, y), "Interview Questions:", font=font, fill=(30,30,120))
	y += 40
	for idx, q in enumerate(questions, 1):
		d.text((30, y), f"{idx}. {q}", font=font, fill=(30,30,30))
		y += 32
	img.save(output_path)
	return output_path
# --- CV Optimization Logic ---
import re
def optimize_cv_text(original_text, added_skills=None, job_keywords=None):
	"""
	Basic CV optimization: reorder skills, enhance bullet points, inject job-specific keywords/skills.
	- original_text: Raw CV text
	- added_skills: List of user-confirmed/added skills
	- job_keywords: List of job-specific keywords (optional)
	Returns: Optimized CV text (string)
	"""
	if added_skills is None:
		added_skills = []
	if job_keywords is None:
		job_keywords = []

	# 0. Prepare summary section
	summary_lines = []
	if added_skills:
		summary_lines.append('SUMMARY')
		summary_lines.append('Experienced in: ' + ', '.join(added_skills) + '.')
	if job_keywords:
		summary_lines.append('Job-Relevant Keywords: ' + ', '.join(job_keywords) + '.')
	summary_lines.append('')  # Blank line

	# 1. Parse original text into sections
	section_titles = [
		'CAREER OBJECTIVE', 'WORK EXPERIENCE', 'TECHNICAL  SKILLS', 'PROJECTS', 'EDUCATION', 'CERTIFICATIONS', 'LANGUAGES', 'SKILLS', 'EXPERIENCE', 'OBJECTIVE', 'SUMMARY'
	]
	lines = original_text.splitlines()
	formatted_lines = []
	current_section = None
	name_contact_block = []
	found_section = False
	for line in lines:
		line_strip = line.strip()
		if not line_strip:
			continue
		# Detect section headings (match full line, case-insensitive, ignore trailing dashes)
		is_section = False
		for title in section_titles:
			if line_strip.upper() == title or line_strip.upper().startswith(title + ' '):
				is_section = True
				break
		if is_section:
			found_section = True
			current_section = line_strip.upper().split('-')[0].strip()
			formatted_lines.append('')  # Blank line before section
			formatted_lines.append(current_section)
			formatted_lines.append('-' * len(current_section))
			continue
		# Add ASCII bullet for skills section only for short lines (likely skills)
		if current_section and 'SKILL' in current_section and line_strip and not line_strip.startswith('-') and len(line_strip) < 60:
			formatted_lines.append('- ' + line_strip)
		else:
			if not found_section:
				name_contact_block.append(line_strip)
			else:
				formatted_lines.append(line_strip)

	# 2. Inject summary after name/contact block
	output_lines = name_contact_block + [''] + summary_lines + formatted_lines

	# 3. Inject added skills as a bulleted list in TECHNICAL SKILLS section if not present
	skills_section_idx = None
	for idx, l in enumerate(output_lines):
		if l.strip().startswith('TECHNICAL  SKILLS'):
			skills_section_idx = idx
			break
	if skills_section_idx is not None and added_skills:
		# Insert after section heading and underline
		insert_at = skills_section_idx + 2
		output_lines.insert(insert_at, 'Skills Added for Target Role:')
		for skill in added_skills:
			output_lines.insert(insert_at + 1, f'- {skill}')

	# 4. Add job-specific keywords at the end
	if job_keywords:
		output_lines.append('')
		output_lines.append('Job-Specific Keywords: ' + ', '.join(job_keywords))

	# 5. Remove duplicate blank lines
	cleaned_lines = []
	prev_blank = False
	for l in output_lines:
		if l.strip() == '':
			if not prev_blank:
				cleaned_lines.append('')
			prev_blank = True
		else:
			cleaned_lines.append(l)
			prev_blank = False

	return '\n'.join(cleaned_lines)
