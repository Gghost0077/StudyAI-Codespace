from dotenv import load_dotenv
load_dotenv()

import os 
import json 
from datetime import datetime

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from flask import Flask, jsonify, request, render_template
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
import tempfile
from docx import Document
from scheduler import generate_schedule
from flask_cors import CORS

app = Flask(__name__)


#drag and drop file upload

ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"}
MAX_BRIEF_CHARS = 12000

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_docx(path):
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

def extract_text_from_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)

def trim_brief_text(text):
    text = (text or "").strip()
    if len(text) > MAX_BRIEF_CHARS:
        return text[:MAX_BRIEF_CHARS]
    return text

#backend validation
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_payload(data):
    modules = data.get("modules")
    availability = data.get("availability")
    ai_strictness = data.get("ai_strictness", "medium")

    if not isinstance(modules, list) or not modules:
        return "Modules must be a non-empty list."

    if not isinstance(availability, list) or not availability:
        return "Availability must be a non-empty list."

    if ai_strictness not in {"low", "medium", "high"}:
        return "Invalid AI strictness value."

    for module in modules:
        if not module.get("name", "").strip():
            return "Each module must have a name."

        if str(module.get("importance", "")) not in {"1", "2", "3"} and module.get("importance") not in {1, 2, 3}:
            return f"Module '{module.get('name', 'Unknown')}' has invalid importance."

        tasks = module.get("tasks", [])
        if not isinstance(tasks, list) or not tasks:
            return f"Module '{module.get('name', 'Unknown')}' must contain at least one task."

        for task in tasks:
            if not task.get("title", "").strip():
                return f"All tasks in module '{module.get('name', 'Unknown')}' must have a title."

            if not is_valid_date(task.get("deadline", "")):
                return f"Task '{task.get('title', 'Unknown')}' has an invalid deadline."

            try:
                hours = float(task.get("estimated_hours", 0))
                if hours <= 0:
                    return f"Task '{task.get('title', 'Unknown')}' must have positive estimated hours."
            except (TypeError, ValueError):
                return f"Task '{task.get('title', 'Unknown')}' has invalid estimated hours."

    for slot in availability:
        day = slot.get("day", "").strip()
        start = slot.get("start", "")
        end = slot.get("end", "")

        if not day or not start or not end:
            return "All availability slots must include day, start, and end."

        if start >= end:
            return "Availability start time must be before end time."

    return None

#data loggging 
@app.route("/log_event", methods=["POST"])
def log_event():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No log data provided"}), 400

    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    log_path = os.path.join(logs_dir, "events.jsonl")

    log_record = {
        "timestamp_server": datetime.utcnow().isoformat(),
        **data
    }

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_record) + "\n")

    return jsonify({"status": "logged"}), 200

@app.route("/upload_brief", methods=["POST"])
def upload_brief():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF, TXT, and DOCX files are supported"}), 400

    filename = secure_filename(file.filename)
    suffix = "." + filename.rsplit(".", 1)[1].lower()

    temp_path = None

    try:
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)

        file.save(temp_path)

        if suffix == ".txt":
            extracted = extract_text_from_txt(temp_path)
        elif suffix == ".pdf":
            extracted = extract_text_from_pdf(temp_path)
        elif suffix == ".docx":
            extracted = extract_text_from_docx(temp_path)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

        extracted = trim_brief_text(extracted)

        if not extracted.strip():
            return jsonify({"error": "Could not extract readable text from the file"}), 400

        return jsonify({
            "filename": filename,
            "brief_text": extracted
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass

#loads index page 
@app.route("/")
def home():
    return render_template("index.html")

#Sends data to generate schedule from index
@app.route('/generate_schedule', methods=['POST'])
def generate():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    error = validate_payload(data)
    if error:
        return jsonify({"error": error}), 400

    modules = data.get('modules', [])
    availability = data.get('availability', [])
    ai_enabled = data.get('ai_enabled', False)
    ai_strictness = data.get("ai_strictness", "medium")

    if not modules or not availability:
        return jsonify({'error': 'Modules and availability are required'}), 400
    
    schedule = generate_schedule(modules, availability, ai_enabled, ai_strictness)
    
    logger.info(f"Generated schedule with {len(schedule.get('sessions', []))} sessions")
 

    return jsonify(schedule)

if __name__ == "__main__":
    app.run(debug=False)