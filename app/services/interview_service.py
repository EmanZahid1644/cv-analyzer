import random
import os
import requests

def generate_market_demand_analysis(role_or_job, n_questions=10):
    """
    Returns a dictionary with market demand analysis for the given role/job:
    - growth
    - skill_demand_trend
    - output (summary)
    - interview_prep (questions)
    - career_insight
    Uses Gemini LLM for dynamic generation.
    """
    gemini_api_key = 'AIzaSyDHqrVCXSLg30kbAeE5QYT1s8mLy8-gY_k'
    base_url = "https://generativelanguage.googleapis.com/v1beta/models/"
    url = f"{base_url}gemini-2.5-flash:generateContent?key={gemini_api_key}"
    headers = {"Content-Type": "application/json"}
    import json
    def gemini_query(prompt):
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            response = requests.post(url, headers=headers, json=data, timeout=15)
            print(f"[Gemini LLM] Request prompt: {prompt}")
            print(f"[Gemini LLM] Response status: {response.status_code}")
            print(f"[Gemini LLM] Response text: {response.text}")
            if response.status_code == 200:
                resp_json = response.json()
                candidates = resp_json.get("candidates", [])
                if candidates:
                    text = candidates[0]["content"]["parts"][0]["text"]
                    if text and text.strip():
                        return text
                    else:
                        print(f"[Gemini LLM] Empty text in response: {json.dumps(resp_json)}")
                else:
                    print(f"[Gemini LLM] No candidates in response: {json.dumps(resp_json)}")
            else:
                print(f"[Gemini LLM] Non-200 response: {response.status_code} {response.text}")
        except Exception as e:
            print(f"[Gemini LLM] Market demand analysis failed: {e}")
        return None

    prompts = {
        "growth": f"You are a career and market analyst. Please provide a detailed, up-to-date summary of the current market growth and future outlook for the job role '{role_or_job}'. Use recent trends and statistics if possible. Respond in 2-3 sentences.",
        "skill_demand_trend": f"You are a career and market analyst. List the top 5 trending skills, technologies, or certifications that are most in demand for the job role '{role_or_job}' in today's market. Respond as a numbered list.",
        "output": f"You are a career and market analyst. Summarize the overall market demand, job opportunities, and hiring trends for '{role_or_job}' in 2-3 sentences. Mention any notable growth areas or industries.",
        "career_insight": f"You are a career coach. Give 2-3 actionable, practical career insights or advice for someone pursuing '{role_or_job}' in today's market. Respond as a numbered list.",
    }

    result = {}
    fallback = {
        "growth": f"The demand for {role_or_job} roles is growing steadily as companies focus on digital transformation, user experience, and product design. The field is expected to expand further in the next 5 years.",
        "skill_demand_trend": "1. Figma\n2. Adobe XD\n3. Prototyping\n4. User Research\n5. Accessibility",
        "output": f"{role_or_job} professionals are in high demand across tech, finance, and e-commerce sectors. Companies seek candidates with strong portfolios and up-to-date design skills.",
        "career_insight": "1. Build a strong portfolio with real projects.\n2. Stay updated with latest design tools and trends.\n3. Network with other designers and join online communities."
    }
    for key, prompt in prompts.items():
        val = gemini_query(prompt)
        if val and val != "Not available.":
            result[key] = val
        else:
            result[key] = fallback[key]

    # Interview prep (reuse existing function)
    result["interview_prep"] = generate_interview_questions(role_or_job, n_questions)
    return result

# Simple static question bank for fallback/demo
QUESTION_BANK = {
    "python": [
        "What are Python decorators and how do you use them?",
        "Explain the difference between lists and tuples in Python.",
        "How does Python's garbage collection work?",
        "What is a lambda function?",
        "How do you manage dependencies in a Python project?",
        "What is the GIL and how does it affect threading?",
        "How do you handle exceptions in Python?",
        "Explain list comprehensions with an example.",
        "What is the difference between deep copy and shallow copy?",
        "How do you optimize performance in Python code?"
    ],
    "machine learning": [
        "What is overfitting and how can you prevent it?",
        "Explain the bias-variance tradeoff.",
        "What is regularization?",
        "How do you handle missing data?",
        "What is cross-validation?",
        "Explain the difference between supervised and unsupervised learning.",
        "What is a confusion matrix?",
        "How do you select important features?",
        "What is gradient descent?",
        "Explain ensemble methods."
    ],
    # Add more roles/topics as needed
}

def generate_interview_questions(role_or_skill, n=10):
    """
    Returns up to n interview questions for the given role or skill.
    Uses OpenAI API (or similar LLM) if available, else falls back to static/generic questions.
    """
    role = role_or_skill.lower()
    questions = []
    for key in QUESTION_BANK:
        if key in role:
            questions = QUESTION_BANK[key]
            break
    if not questions:
        # Try Google Gemini API if key is set
        gemini_api_key = 'AIzaSyAOZ0LVS6OHTEs05rSxPsHSUnrykZ4l6_Q'
        try:
            prompt = f"Generate {n} realistic, role-specific interview questions for a {role_or_skill} job. Only return the questions as a numbered list."
            base_url = "https://generativelanguage.googleapis.com/v1beta/models/"
            url = f"{base_url}gemini-2.5-flash:generateContent?key={gemini_api_key}"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [
                    {"parts": [{"text": prompt}]}
                ]
            }
            response = requests.post(url, headers=headers, json=data, timeout=15)
            if response.status_code == 200:
                candidates = response.json().get("candidates", [])
                if candidates:
                    content = candidates[0]["content"]["parts"][0]["text"]
                    questions = [q.strip().lstrip("0123456789. ") for q in content.split("\n") if q.strip() and any(c.isalpha() for c in q)]
                    questions = [q for q in questions if len(q) > 10]
                    if len(questions) >= n:
                        return questions[:n]
        except Exception as e:
                print(f"[Gemini LLM] Interview question generation failed: {e}")
        # Fallback: generic questions
        questions = [
            "Tell me about yourself.",
            "Why are you interested in this role?",
            "Describe a challenging project you worked on.",
            "How do you handle tight deadlines?",
            "What are your strengths and weaknesses?",
            "How do you stay updated with industry trends?",
            "Describe your teamwork experience.",
            "How do you prioritize tasks?",
            "Where do you see yourself in 5 years?",
            "Why should we hire you?"
        ]
    return random.sample(questions, min(n, len(questions)))
