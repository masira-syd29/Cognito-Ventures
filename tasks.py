# tasks.py
import os
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
from celery import Celery
import io

# Import load_dotenv to correctly load environment variables in the Celery worker process
from dotenv import load_dotenv

# --- Load Environment Variables ---
# This is the crucial line to ensure the Celery worker can access the API key
load_dotenv()


# --- Celery Configuration ---
# The connection string points to our Redis server.
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
celery_app = Celery('tasks', broker=redis_url, backend=redis_url)

def extract_text_from_pdf(pdf_bytes):
    # Now takes bytes instead of a file object
    doc = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def scrape_text_from_url(url):
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        return ' '.join(t.get_text() for t in soup.find_all(['p', 'h1', 'h2', 'h3']))
    except Exception:
        return "Could not fetch website content."

def get_startup_analysis(pitch_deck_text, website_text, system_prompt):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    # New: Configure lower safety settings for this specific request
    # This makes the model less likely to block a response.
    safety_settings = {
        'HATE': 'BLOCK_NONE',
        'HARASSMENT': 'BLOCK_NONE',
        'SEXUAL': 'BLOCK_NONE',
        'DANGEROUS': 'BLOCK_NONE'
    }

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = system_prompt.format(pitch_deck_text=pitch_deck_text, website_text=website_text)
    
    try:
        response = model.generate_content(prompt, safety_settings=safety_settings)
        
        # New: Add a check to see *why* a response might be empty
        if not response.parts:
            # This happens if the response was blocked by safety filters
            print("DEBUG: Response was blocked. Feedback:", response.prompt_feedback)
            return {"error": f"AI analysis failed! Reason: {response.prompt_feedback}"}
        
        # Now, we can safely access the text
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        
        # Add another check in case the cleaned response is empty
        if not cleaned_response:
             print("DEBUG: API returned an empty text response.")
             return {"error": "AI analysis failed, API returned an empty response."}

        return json.loads(cleaned_response)

    except json.JSONDecodeError as e:
        # New: This block now prints the problematic text that failed to parse
        print("DEBUG: Failed to decode JSON. Raw response text was:")
        print("--------------------")
        print(response.text)
        print("--------------------")
        return {"error": f"AI analysis failed. Details: Invalid JSON format. {e}"}

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": f"An unexpected error occurred. Details: {str(e)}"}

# --- The Celery Task ---
@celery_app.task(bind=True)
def analyze_startup_task(self, pdf_bytes, website_url, system_prompt):
    """This is the function that will run in the background."""
    try:
        deck_text = extract_text_from_pdf(pdf_bytes)
        web_text = scrape_text_from_url(website_url) if website_url else "No website provided."
        analysis_json = get_startup_analysis(deck_text, web_text, system_prompt)

        # If the AI returns an error, raise an exception to trigger FAILURE state
        if 'error' in analysis_json:
            raise Exception(analysis_json['error'])
        
        return analysis_json
    except Exception as e:
        # This will catch errors from PDF parsing, web scraping, or the AI
        # and cause the Celery task to enter a 'FAILURE' state.
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        raise e