import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify

# Import the functions from your separate analyst.py file
from analyst import extract_text_from_pdf, scrape_text_from_url, get_startup_analysis

load_dotenv() # Create a .env file and put GOOGLE_API_KEY="your_key_here"
api_key = os.getenv("GOOGLE_API_KEY")
app = Flask(__name__)

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

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # 1. Get data from the form
    pitch_deck = request.files.get('pitch_deck')
    website_url = request.form.get('website_url')

    if not pitch_deck:
        return jsonify({"error": "No pitch deck provided."}), 400

    try:
        # 2. Extract text
        deck_text = extract_text_from_pdf(pitch_deck)
        web_text = scrape_text_from_url(website_url) if website_url else "No website provided."
    except Exception as e:
        return jsonify({"error": f"Error processing file: {e}"}), 500
    # 3. Get AI analysis
    analysis_json = get_startup_analysis(deck_text, web_text)
    
    # 4. Return JSON to the frontend
    return jsonify(analysis_json)
    


# --- 3. Main Execution ---
if __name__ == "__main__":
    app.run(debug=True)