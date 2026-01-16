import requests

API_KEY = "AIzaSyAOZ0LVS6OHTEs05rSxPsHSUnrykZ4l6_Q"  # Replace with your Gemini API key if needed
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/"
MODEL = "gemini-2.5-flash"

prompt = "For the job role 'Data Scientist', provide a concise summary of current market growth and future outlook. Respond in 2-3 sentences."

url = f"{BASE_URL}{MODEL}:generateContent?key={API_KEY}"
headers = {"Content-Type": "application/json"}
data = {
    "contents": [
        {"parts": [{"text": prompt}]}
    ]
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=15)
    print("Status Code:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Request failed:", e)
