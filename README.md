# 🚀 Cognito Ventures: AI-Powered Startup Analyst

**Cognito Ventures** is a high-performance, asynchronous data pipeline designed to automate the initial vetting process for Venture Capitalists. By ingesting unstructured data from pitch decks (PDFs) and live company websites, the system synthesizes deep investment insights using Generative AI.

---

## 🏗️ System Architecture
Unlike standard "wrapper" apps, Cognito Ventures utilizes an **Asynchronous Task Queue** architecture. This ensures the web server remains responsive while the heavy lifting—PDF parsing, web scraping, and LLM reasoning—happens in a decoupled background process.



1. **Producer (Flask):** Handles file uploads, URL inputs, and state management.
2. **Broker (Redis/Upstash):** Manages the message queue with TLS encryption.
3. **Consumer (Celery):** Executes long-running extraction and analysis tasks.
4. **Intelligence (Gemini 2.x):** Performs context-aware analysis via structured prompting.

---

## 🛠️ Tech Stack
- **Backend:** Python, Flask (RESTful API)
- **Task Orchestration:** Celery (Asynchronous processing)
- **Message Broker:** Redis via Upstash (Cloud-native, TLS secured)
- **AI Engine:** Google Gemini API (`gemini-flash-latest`)
- **Data Extraction:** PyMuPDF (PDF parsing), BeautifulSoup4 (Web scraping)
- **Environment:** Docker-ready, python-dotenv

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- A Google AI Studio API Key
- An Upstash Redis instance (TLS enabled)

### 2. Installation
```bash
# Clone the repository
git clone [https://github.com/masira-syd29/Cognito-Ventures.git](https://github.com/masira-syd29/Cognito-Ventures.git)
cd Cognito-Ventures

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

3. Configuration
Create a .env file in the root directory:

GOOGLE_API_KEY=your_gemini_api_key
REDIS_URL=rediss://default:your_password@your_endpoint.upstash.io:6379

4. Running the Application
You need to run two separate processes:

Terminal 1 (The Worker):
celery -A tasks worker --loglevel=info -P solo

Terminal 2 (The Web App):
flask run