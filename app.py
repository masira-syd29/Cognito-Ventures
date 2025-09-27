import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from tasks import analyze_startup_task # Import the task
import uuid 


# # Import the functions from your separate analyst.py file
# from analyst import extract_text_from_pdf, scrape_text_from_url, get_startup_analysis

load_dotenv() # Create a .env file and put GOOGLE_API_KEY="your_key_here"
# api_key = os.getenv('GOOGLE_API_KEY')
app = Flask(__name__)

# --- Create a temporary folder for uploads ---
UPLOAD_FOLDER = 'temp_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

SYSTEM_PROMPT = """
You are "VentureGPT", an expert AI analyst for a top-tier venture capital firm.
Your task is to analyze a startup based on its pitch deck text and website content.
Your ONLY output must be a single, valid JSON object.
Do not include any text, explanations, or markdown formatting before or after the JSON object.

Analyze the provided startup content and generate a JSON object with the following keys:
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
    # New: Add file extension validation
    if not pitch_deck.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Invalid file type. Please upload a PDF."}), 400

    # --- New Logic: Save file and pass path ---
    # Generate a unique filename to avoid conflicts
    unique_filename = str(uuid.uuid4()) + '.pdf'
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    # Save the uploaded file to the temporary location
    pitch_deck.save(file_path)

    # Pass the FILE PATH to the task, not the file's content
    task = analyze_startup_task.delay(file_path, website_url, SYSTEM_PROMPT)
    return jsonify({'task_id': task.id})

@app.route('/status/<task_id>')
def task_status(task_id):
    # """This route is polled by the frontend to check the task's status."""
    # task = analyze_startup_task.AsyncResult(task_id)
    
    # if task.state == 'PENDING':
    #     response = {'state': task.state, 'status': 'Pending...'}
    # elif task.state != 'FAILURE':
    #     response = {
    #         'state': task.state,
    #         'status': task.info.get('status', '') if isinstance(task.info, dict) else str(task.info),
    #     }
    #     if 'result' in task.info:
    #         response['result'] = task.info['result']
    #     # If the task is successful, the result is in task.result
    #     if task.state == 'SUCCESS':
    #         response['result'] = task.result
    # else:
    #     # Something went wrong in the background task
    #     response = {
    #         'state': task.state,
    #         'status': str(task.info),  # The exception raised
    #     }
    # return jsonify(response)
    """A more robust route to check the task's status."""
    task = analyze_startup_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Pending...'}
    elif task.state == 'SUCCESS':
        response = {'state': task.state, 'result': task.result}
    elif task.state != 'FAILURE':
        response = {'state': task.state, 'status': 'In progress...'}
    else: # The task failed
        response = {'state': task.state, 'status': str(task.info)}
        
    return jsonify(response)

    

# --- 3. Main Execution ---
if __name__ == "__main__":
    app.run(debug=True)