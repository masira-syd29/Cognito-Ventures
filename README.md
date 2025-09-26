Cognito Ventures 🤖
AI Analyst for Startup Evaluation
Cognito Ventures is a web application that harnesses the power of artificial intelligence to provide in-depth analysis of startup ventures. By simply uploading a pitch deck (in PDF format) and providing a website URL, the application's AI analyst generates a comprehensive executive summary, providing key insights into the startup's problem, solution, business model, and more.

Features
PDF Analysis: Extracts text content directly from a startup's pitch deck.

Website Scraping: Scrapes and analyzes textual data from the startup's public website.

AI-Powered Analysis: Utilizes the Gemini API to intelligently process the extracted data and produce a structured, detailed summary.

Asynchronous Processing: Leverages a Celery task queue and a Redis broker to handle resource-intensive analysis in the background, ensuring a smooth user experience.

Scalable Backend: Designed to handle multiple analysis requests without blocking the main application.

Live Demo
You can see the application in action here:
https://cognito-ventures-29m09s02.up.railway.app/

Technology Stack
Frontend: HTML, CSS, & JavaScript

Backend: Python (Flask)

AI Model: Gemini API

Task Queue: Celery

Broker & Backend: Redis (Upstash)

PDF Processing: PyMuPDF (fitz)

Web Scraping: BeautifulSoup4 (bs4)

Environment Management: python-dotenv

Local Setup
To run this project locally, follow these steps:

Clone the repository:

git clone [https://github.com/masira-syd29/Cognito-Ventures](https://github.com/masira-syd29/Cognito-Ventures)
cd cognito-ventures

Set up a virtual environment and install dependencies:

python3 -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
pip install -r requirements.txt

Create a .env file in the project's root directory and add your API keys and Redis URL:

GOOGLE_API_KEY=your_gemini_api_key
REDIS_URL=rediss://default:<your_upstash_password>@<your_upstash_host>:<port>

Start the Celery worker and the Flask application in separate terminal windows:

# Terminal 1: Start Celery worker
celery -A tasks worker --loglevel=info

# Terminal 2: Start Flask app
flask run

Open your browser and navigate to http://127.0.0.1:5000.
