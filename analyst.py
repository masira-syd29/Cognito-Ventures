#AIzaSyDNtix-DFwN1pLDuxfP3wQnraga1eiO9l0
# In analyst.py
import os
import pymupdf  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json


# load_dotenv() # Create a .env file and put GOOGLE_API_KEY="your_key_here"
# app = Flask(__name__)

SYSTEM_PROMPT = """
You are "VentureGPT", an expert AI analyst for a top-tier venture capital firm.
Your task is to analyze a startup based on its pitch deck text and website content.
You must return your analysis in a structured JSON object.

The JSON object must have the following keys:
- "company_summary": A brief, 2-sentence overview of what the company does.
- "strengths": An array of 3-4 strings, each highlighting a key strength.
- "weaknesses": An array of 3-4 strings, each identifying a key risk or weakness.
- "verdict": A short string with your final recommendation (e.g., "Strong Prospect", "Needs More Traction", "High Risk, High Reward", "Pass").
- "justification": A one-sentence justification for your verdict.

Do not include any introductory text or explanations outside of the JSON object.

---
Analyze the following content:
Pitch Deck Text: "{pitch_deck_text}"
Website Content: "{website_text}"
---
"""

# --- 1. Data Extraction Functions ---
def extract_text_from_pdf(pdf_file):
    # ... (code to open PDF and get text)
    doc = pymupdf.open(stream=pdf_file.read(), filetype='pdf')
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def scrape_text_from_url(url):
    # ... (code to get website text)
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        return ' '.join(t.get_text() for t in soup.find_all(['p', 'h1', 'h2', 'h3']))
    except Exception as e:
        print(f"Error scraping URL: {e}")
        return "Could not fetch website content."

# --- 2. AI Analysis Function ---
def get_startup_analysis(pitch_deck_text, website_text):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = SYSTEM_PROMPT.format(pitch_deck_text=pitch_deck_text, website_text=website_text)
    
    try:
        response = model.generate_content(prompt)
        # Clean and parse the JSON response
        # The API might return the JSON inside a markdown code block (```json ... ```)
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return {"error": "Failed to get analysis from AI."}



    

# --- 3. Main Execution ---
if __name__ == "__main__":
    # Find a sample pitch deck online and download it (e.g., search "airbnb pitch deck pdf")
    pdf_file = "D:/Masira/Python_Projects/Cognito-Ventures/Nykaa_PPT.pdf"
    url = "https://www.nykaa.com/" # Use the startup's actual website

    print("Extracting data...")
    deck_text = extract_text_from_pdf(pdf_file)
    web_text = scrape_text_from_url(url)

    print("Analyzing startup...")
    analysis = get_startup_analysis(deck_text, web_text)

    print("\n--- AI Analysis Complete ---")
    print(f"Summary: {analysis['company_summary']}")
    
    print("\nStrengths:")
    for strength in analysis['strengths']:
        print(f"- {strength}")

    print("\nWeaknesses:")
    for weakness in analysis['weaknesses']:
        print(f"- {weakness}")

    print(f"Verdict: {analysis['verdict']}")
    print(f"Justification: {analysis['justification']}")