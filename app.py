import os
import time
import fitz  # PyMuPDF
import requests
import csv
import io
import openpyxl
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
import uuid

# Load environment variables from a .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# --- Gemini API Configuration ---
API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"
ALLOWED_EXTENSIONS = {'.pdf', '.csv', '.xlsx', '.html'}

# --- Text Extraction Functions ---

def extract_text_from_pdf(stream):
    """Extracts text from a PDF file stream."""
    doc = fitz.open(stream=stream, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_text_from_excel(stream):
    """Extracts text from an XLSX (Excel) file stream."""
    text = ""
    workbook = openpyxl.load_workbook(stream)
    for sheet in workbook.worksheets:
        text += f"Sheet: {sheet.title}\n"
        for row in sheet.iter_rows():
            row_text = [str(cell.value) if cell.value is not None else "" for cell in row]
            text += ", ".join(row_text) + "\n"
    return text

def extract_text_from_csv(stream):
    """Extracts text from a CSV file stream."""
    text = ""
    # We need to decode the byte stream into text
    try:
        data = stream.read().decode('utf-8')
    except UnicodeDecodeError:
        data = stream.read().decode('latin-1') # Fallback encoding
        
    reader = csv.reader(io.StringIO(data))
    for row in reader:
        text += ", ".join(row) + "\n"
    return text

def extract_text_from_html(stream):
    """Extracts visible text from an HTML file stream."""
    soup = BeautifulSoup(stream, "html.parser")
    # Get all visible text
    text = soup.get_text(separator="\n", strip=True)
    return text

def extract_text_from_file(file_stream, filename):
    """Main function to route to the correct text extractor."""
    try:
        file_ext = os.path.splitext(filename)[1].lower()

        if file_ext == '.pdf':
            return extract_text_from_pdf(file_stream)
        elif file_ext == '.xlsx':
            return extract_text_from_excel(file_stream)
        elif file_ext == '.csv':
            return extract_text_from_csv(file_stream)
        elif file_ext == '.html':
            return extract_text_from_html(file_stream)
        else:
            return None
    except Exception as e:
        print(f"Error extracting text from {filename}: {e}")
        return None

# --- Gemini API Function ---

def get_summary_from_gemini(text_content):
    """
    Calls the Gemini API to summarize the given text.
    Implements exponential backoff for retries.
    """
    if not API_KEY:
        return None, "Error: GEMINI_API_KEY is not set in the environment."

    # Truncate text if it's too long for a single API request (adjust as needed)
    # A simple way to avoid hitting request size limits.
    max_chars = 100000 
    if len(text_content) > max_chars:
        text_content = text_content[:max_chars] + "\n... [Content Truncated]"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"Please provide a concise, multi-paragraph summary of the following document content:\n\n---\n\n{text_content}"}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.5,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 2048,
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    max_retries = 3
    delay = 1  # Initial delay in seconds

    for attempt in range(max_retries):
        try:
            response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=60)

            # Successful request
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result:
                    summary = result['candidates'][0]['content']['parts'][0]['text']
                    return summary, None
                else:
                    return None, "Error: Invalid response from API."

            # Rate limiting or server overload
            elif response.status_code in [429, 503]:
                print(f"API rate limit or server error. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            
            # Other client/server errors
            else:
                error_details = response.text
                print(f"API Error: {response.status_code}\n{error_details}")
                return None, f"API Error: {response.status_code}. Check server logs."

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2

    return None, "Error: API request failed after all retries."

def get_chat_response_from_gemini(question, document_text):
    """
    Calls the Gemini API to answer questions about the document.
    """
    if not API_KEY:
        return None, "Error: GEMINI_API_KEY is not set in the environment."

    # Truncate text if it's too long for a single API request
    max_chars = 100000 
    if len(document_text) > max_chars:
        document_text = document_text[:max_chars] + "\n... [Content Truncated]"

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"Based on the following document content, please answer this question: {question}\n\nDocument content:\n---\n{document_text}\n\nPlease provide a detailed and accurate answer based only on the information in the document. If the answer cannot be found in the document, please say so."}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 1024,
        }
    }

    headers = {
        'Content-Type': 'application/json'
    }

    max_retries = 3
    delay = 1

    for attempt in range(max_retries):
        try:
            response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=60)

            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result:
                    answer = result['candidates'][0]['content']['parts'][0]['text']
                    return answer, None
                else:
                    return None, "Error: Invalid response from API."

            elif response.status_code in [429, 503]:
                print(f"API rate limit or server error. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= 2
            
            else:
                error_details = response.text
                print(f"API Error: {response.status_code}\n{error_details}")
                return None, f"API Error: {response.status_code}. Check server logs."

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2

    return None, "Error: API request failed after all retries."

# --- Flask Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    error = None
    document_uploaded = False

    if request.method == 'POST':
        # 1. Check if the file part is in the request
        if 'pdf_file' not in request.files:
            error = "No file part in the request. Please select a file."
            return render_template('index.html', summary=summary, error=error, document_uploaded=document_uploaded)

        file = request.files['pdf_file']

        # 2. Check if a file was actually selected
        if file.filename == '':
            error = "No file selected. Please choose a document to upload."
            return render_template('index.html', summary=summary, error=error, document_uploaded=document_uploaded)

        # 3. Check if the file type is allowed
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file and file_ext in ALLOWED_EXTENSIONS:
            try:
                # Read the file into memory
                file_stream = file.read()

                # 4. Extract text
                text = extract_text_from_file(io.BytesIO(file_stream), file.filename)

                if text:
                    # Store document text in session for chat functionality
                    session['document_text'] = text
                    session['document_filename'] = file.filename
                    document_uploaded = True
                    
                    # 5. Get summary from Gemini
                    summary, error = get_summary_from_gemini(text)
                else:
                    error = f"Could not extract any text from the file. The file might be empty, corrupted, or an unsupported format."
            
            except Exception as e:
                print(f"An error occurred: {e}")
                error = "An unexpected error occurred during processing."
        
        else:
            error = f"Invalid file type. Allowed types are: {', '.join(ALLOWED_EXTENSIONS)}"

    return render_template('index.html', summary=summary, error=error, document_uploaded=document_uploaded)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat questions about the uploaded document."""
    if 'document_text' not in session:
        return jsonify({'error': 'No document uploaded. Please upload a document first.'}), 400
    
    data = request.get_json()
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({'error': 'Please provide a question.'}), 400
    
    # Get the answer from Gemini
    answer, error = get_chat_response_from_gemini(question, session['document_text'])
    
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({'answer': answer})

if __name__ == '__main__':
    # Use 0.0.0.0 to make it accessible on your network, or keep 127.0.0.1
    app.run(host='127.0.0.1', port=5000, debug=True)


