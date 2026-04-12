# this file is the main entrypoint for the Flask application, handling routes 
# for file uploads, schedule generation, and event logging. It also includes 
# validation for incoming data and ensures that uploaded files are processed securely.


# loads environment variables from a .env file into the application, allowing for configuration without hardcoding sensitive information.
from dotenv import load_dotenv 
load_dotenv()


import os # provides a way to interact with the operating system, such as handling file paths and environment variables.
import json # allows for parsing and generating JSON data, which is used for communication between the frontend and backend and logging events.
from datetime import datetime # used for validating date formats in the incoming data and for timestamping logged events.

# imports pythons logging system to log important information about the application's behavior, such as when schedules are 
# generated and how many sessions they contain. 
# This can be helpful for debugging and monitoring the application in production.
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Flask creates app
#jsonify is used to return JSON responses from the API endpoints, while request is used to access incoming data from the client.
# render_template is used to serve the index.html file for the frontend
# send_file lets us downlaod log files securely for render
from flask import Flask, jsonify, request, render_template, send_file

from werkzeug.utils import secure_filename # is used to securely handle filenames when saving uploaded files, preventing directory traversal attacks and other security issues.
from PyPDF2 import PdfReader # is used to extract text from PDF files, allowing the application to process uploaded briefs in PDF format.
import tempfile # is used to create temporary files for processing uploaded briefs, ensuring that they are handled securely and cleaned up after use.
from docx import Document # is used to extract text from DOCX files, allowing the application to process uploaded briefs in Word format.
from scheduler import generate_schedule # imports the generate_schedule function from the scheduler module, which contains the core logic for creating study schedules 



app = Flask(__name__) # creates a new Flask application instance, which will be used to define routes and handle incoming requests.

# ================================
# AI USAGE LIMIT helpers 
# ================================

AI_USAGE_LIMIT = 20 # set limit 
# stores the path to the JSON file that persists per-participant usage counts, located in the logs directory
AI_USAGE_FILE = os.path.join(os.path.dirname(__file__), "logs", "ai_usage.json") 

# reads the current AI usage data form the JSON file
# returns participants IDs usage counts
# recovers gracefully if any error occurs
def load_ai_usage():
    if not os.path.exists(AI_USAGE_FILE):
        return {}
    with open(AI_USAGE_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

# writes the AI usage back to the JSON file
# creating the logs directory first if it does not already exist 
# this ensures that usage counts persist through requests
def save_ai_usage(usage):
    os.makedirs(os.path.dirname(AI_USAGE_FILE), exist_ok=True)
    with open(AI_USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(usage, f)

# gets the current number of AI assisted generations used by given participant 
def get_ai_usage_count(participant_id):
    return load_ai_usage().get(participant_id, 0)

# adds the tally of AI usages by 1 called after a succesful AI-assisted generated schedule 
def increment_ai_usage(participant_id):
    usage = load_ai_usage()
    usage[participant_id] = usage.get(participant_id, 0) + 1
    save_ai_usage(usage)


# ======================================
# Brief upload configuration and helpers
# ======================================
ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"} #defines which uploaded file types are allowed for the brief upload feature, ensuring that only supported formats are processed.
MAX_BRIEF_CHARS = 12000 # limits how much text can be exracted from uploaded briefs to prevent excessively long inputs that could cause performance issues or overwhelm the AI model.

#checks if the uploaded file has an allowed extension, ensuring that only supported file types are processed for brief uploads.
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS #"." in filename checks if there is an extension in the filename, while filename.rsplit(".", 1)[1].lower() extracts the extension and converts it to lowercase for comparison against the allowed extensions set.

# opens the docx file and extracts text from all paragraphs, joining them into a single string. 
# This allows the application to process uploaded briefs in Word format and use the extracted text for the AI to generate study tips .
def extract_text_from_docx(path):
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

# reads the content of a text file, allowing the application to process uploaded briefs in plain text format and use the extracted text for the AI to generate study tips.
def extract_text_from_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

# opens pdf file and extracts text from all pages, joining them into a single string. 
# This allows the application to process uploaded briefs in PDF format and use the extracted text for the AI to generate study tips. 
# The function uses PyPDF2's PdfReader to read the PDF and extract text from each page, handling cases where text extraction might fail by returning an empty string for those pages.
def extract_text_from_pdf(path):
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)

# This function takes the extracted brief text and trims it to a maximum character limit defined by MAX_BRIEF_CHARS. 
# This ensures that the input to the AI model is concise and manageable, preventing performance issues 
def trim_brief_text(text):
    text = (text or "").strip()
    if len(text) > MAX_BRIEF_CHARS:
        return text[:MAX_BRIEF_CHARS]
    return text

# ======================================
# Request validation helpers
# ======================================


# checks if a given string is a valid date in the format YYYY-MM-DD,
#  which is used to validate the deadline field in the incoming task data.
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# main back end validation function for the incoming data from the frontend. 
# It checks that the modules and availability are properly structured, that required fields are present and correctly formatted, 
# and that values like importance, deadlines, and estimated hours meet the expected criteria.
def validate_payload(data):
    modules = data.get("modules")
    availability = data.get("availability")
    ai_strictness = data.get("ai_strictness", "medium")

    if not isinstance(modules, list) or not modules: # rejects if modules is not a list or is empty, ensuring that the application receives a valid structure for the study modules.
        return "Modules must be a non-empty list."

    if not isinstance(availability, list) or not availability: # rejects if availability is not a list or is empty, ensuring that the application receives a valid structure for the user's available time slots.
        return "Availability must be a non-empty list."

    if ai_strictness not in {"low", "medium", "high"}: # rejects if the AI strictness value is not one of the expected options, ensuring that the application receives a valid configuration for how strictly the AI should generate study tips.
        return "Invalid AI strictness value."

    for module in modules: # loops through each module to check if each module contains a name
        if not module.get("name", "").strip():
            return "Each module must have a name."

        if str(module.get("importance", "")) not in {"1", "2", "3"} and module.get("importance") not in {1, 2, 3}: # checks if the importance field for each module is either 1, 2, or 3 (as a string or integer), 
            return f"Module '{module.get('name', 'Unknown')}' has invalid importance."                             # ensuring that the application receives valid priority levels for the modules.

# ensures each module has at least one task 
        tasks = module.get("tasks", []) 
        if not isinstance(tasks, list) or not tasks:
            return f"Module '{module.get('name', 'Unknown')}' must contain at least one task."
# ensures each task has a non empty title
        for task in tasks:
            if not task.get("title", "").strip():
                return f"All tasks in module '{module.get('name', 'Unknown')}' must have a title."
# checks if deadline is a valid date 
            if not is_valid_date(task.get("deadline", "")):
                return f"Task '{task.get('title', 'Unknown')}' has an invalid deadline."
# checks if estimated hours is a positive number, ensuring that the application receives valid time estimates for each task.
            try:
                hours = float(task.get("estimated_hours", 0))
                if hours <= 0:
                    return f"Task '{task.get('title', 'Unknown')}' must have positive estimated hours."
            except (TypeError, ValueError):
                return f"Task '{task.get('title', 'Unknown')}' has invalid estimated hours."

# loops through each availabiltity slot and pulls the expected fields (day, start, end). 
    for slot in availability:
        day = slot.get("day", "").strip()
        start = slot.get("start", "")
        end = slot.get("end", "")
# ensure that no availability slot is missing any of the required fields (day, start, end) 
        if not day or not start or not end:
            return "All availability slots must include day, start, and end."
# rejects if the start time is not before the end time, ensuring that the application receives valid time slots for the user's availability.
        if start >= end:
            return "Availability start time must be before end time."

    return None # if all checks pass, the function returns None, indicating that the payload is valid.

# =========================
# Research Event logging
# =========================

# creates the /log_event endpoint and reads the JSON from the frontend
@app.route("/log_event", methods=["POST"])
def log_event():
    data = request.get_json()

# rejects missing or empty JSON payloads 
    if not data:
        return jsonify({"error": "No log data provided"}), 400

# defines a set of allowed event types to ensure that only recognized events are logged, 
# preventing invalid or unexpected data from being recorded in the logs to be ethically sound and maintain data integrity.
    allowed_event_types = {
        "app_opened",
        "consent_given",
        "schedule_generated",
        "schedule_generation_failed",
        "brief_uploaded",
        "brief_upload_failed",
        "ai_toggled"
    }

# validates that the event_type field is present and is one of the allowed event types, ensuring that only valid events are logged.
    event_type = data.get("event_type")
    if event_type not in allowed_event_types:
        return jsonify({"error": "Invalid event type"}), 400
# validates that the participant_id field is present and non-empty, 
# ensuring that each logged event can be associated with a specific participant for research purposes while maintaining ethical standards.
    participant_id = str(data.get("participant_id", "")).strip()
    if not participant_id:
        return jsonify({"error": "Missing participant_id"}), 400

# creates a log record with the server timestamp, participant ID, event type, and client timestamp.
# server and client timestamps allow researchers to understand when events occurred from both the user's perspective and the server's perspective, 
# which can be important for analyzing user behavior and troubleshooting issues.
    log_record = {
        "timestamp_server": datetime.utcnow().isoformat(),
        "participant_id": participant_id,
        "event_type": event_type,
        "timestamp_client": data.get("timestamp"),
    }

# only stores ai_enabled if its a boolean, ensuring that the log data remains consistent and that only valid values are recorded for this field.
    if isinstance(data.get("ai_enabled"), bool):
        log_record["ai_enabled"] = data["ai_enabled"]
# only stores ai_strictness if its value is one of the expected options, ensuring that the log data remains consistent and that only valid values are recorded for this field.
    if data.get("ai_strictness") in {"low", "medium", "high"}:
        log_record["ai_strictness"] = data["ai_strictness"]
# loops over the keys module_count, task_count, and availability_count, and only stores them in the log record if they are integers. 
# This ensures that the log data remains consistent and that only valid values are recorded for these fields, which
    for key in ["module_count", "task_count", "availability_count"]:
        value = data.get(key)
        if isinstance(value, int):
            log_record[key] = value
#stores status if its a string to capture any additional information about the event, while ensuring that only valid string values are recorded for this field.
    if isinstance(data.get("status"), str):
        log_record["status"] = data["status"]
#builds a logs folder path, creates folder if it doesn't exist and creates the final path to events.jsonl where the log records will be stored. This ensures that the application can log events persistently and that the logs are organized in a dedicated directory for easy access and management.
    logs_dir = os.path.join(os.path.dirname(__file__), "logs")
    os.makedirs(logs_dir, exist_ok=True)

    log_path = os.path.join(logs_dir, "events.jsonl")
# writes the log record to the JSONL file, appending it as a new line. This allows the application to maintain a persistent record of events that can be analyzed later for research purposes, while ensuring that the log data is stored in a structured format that is easy to parse and analyze.
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_record) + "\n")
# returns a success response to the client, indicating that the event was logged successfully. This allows the frontend to provide feedback to the user or take further actions based on the successful logging of the event.
    return jsonify({"status": "logged"}), 200


# =================================
# Brief upload route
# =================================

# create the upload endpoint 
@app.route("/upload_brief", methods=["POST"])
def upload_brief():

# rejects if no file is included when user tries to upload a brief, ensuring that the application receives the necessary data to process the brief and generate study tips.
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

# gets the uploaded file from the request, and rejects empty filename cases
    file = request.files["file"]

    if not file or file.filename == "":
        return jsonify({"error": "No file selected"}), 400

# checks which file type using the allowed_file function, 
# and rejects unsupported file types to ensure that the application only processes files that it can handle for brief uploads, 
# maintaining security and functionality.
    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF, TXT, and DOCX files are supported"}), 400

# sanitises the filename to prevent security issues, and extracts the file extension to determine how to process the file.
    filename = secure_filename(file.filename)
    suffix = "." + filename.rsplit(".", 1)[1].lower()
# initialises temp_path to None, which will be used to store the path of the temporary file created for processing the uploaded brief later on.
    temp_path = None

# creates a temporary file and closes the OS file descriptor 
    try:
        fd, temp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)

        file.save(temp_path) # writes the uploaded file to the temp path

# chooses the right extraction method based on the file type, and processes the file to extract text.
        if suffix == ".txt":
            extracted = extract_text_from_txt(temp_path)
        elif suffix == ".pdf":
            extracted = extract_text_from_pdf(temp_path)
        elif suffix == ".docx":
            extracted = extract_text_from_docx(temp_path)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

#trims the extracted text to your maximum allowed size
        extracted = trim_brief_text(extracted)

# rejects cases where no readable text could be extracted from the file, ensuring that the application only processes briefs that contain meaningful content for generating study tips.
        if not extracted.strip():
            return jsonify({"error": "Could not extract readable text from the file"}), 400

# returns the clean filename and extracted text to the frontend  
        return jsonify({
            "filename": filename,
            "brief_text": extracted
        }), 200

# catches unexpected errors during the file processing and returns a generic error message to the client, 
# while also ensuring that any temporary files created during the process are cleaned up to prevent resource leaks and maintain security.
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

# always tries to remove the temporary file if it was created, ensuring that the application does not leave behind temporary files that could consume disk space or pose security risks.
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
#=================================
#Serves the main StudyAI interface 
#=================================
@app.route("/")
def home():
    return render_template("index.html")

 

# ==================================
#Schedule Generation route
# ==================================

# creates the main schedule generation endpoint and reads JSON from the frontend 
@app.route('/generate_schedule', methods=['POST'])
def generate():
    data = request.get_json()

# rejects empty or missing JSON payloads to ensure that the application receives the necessary data to generate a study schedule.
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

# runs the backend validation function on the incoming data, and if it returns an error message, the endpoint responds with that error and a 400 status code. 
# This ensures that the application only processes valid data for schedule generation, 
# maintaining robustness and preventing errors during the generation process.
    error = validate_payload(data)
    if error:
        return jsonify({"error": error}), 400

# extracts the fields needed by the scheduler 
    modules = data.get('modules', [])
    availability = data.get('availability', [])
    ai_enabled = data.get('ai_enabled', False)
    ai_strictness = data.get("ai_strictness", "medium")
    participant_id = str(data.get("participant_id", "")).strip()

# checks again that modules and availability are present and non-empty,
#  providing a final safeguard before attempting to generate the schedule,
#  and ensuring that the application has the necessary data to proceed with schedule generation.
    if not modules or not availability:
        return jsonify({'error': 'Modules and availability are required'}), 400
    
# checks to see if participant has reached AI usage limit
    ai_limit_reached = False 
    if ai_enabled and participant_id:
        current_usage = get_ai_usage_count(participant_id)
        if current_usage >= AI_USAGE_LIMIT:
            ai_enabled = False
            ai_limit_reached = True
        else:
            increment_ai_usage(participant_id)


# hanedles the validated data and calls the generated schedule function in scheduler.py, passing in the modules, availability, and AI configuration.
    schedule = generate_schedule(modules, availability, ai_enabled, ai_strictness)
    schedule["ai_limit_reached"] = ai_limit_reached

# writes  a simple backend log message showing how many sessions were generated in the schedule. 
    logger.info(f"Generated schedule with {len(schedule.get('sessions', []))} sessions")
 
# returns the schedule JSON to the frontend 
    return jsonify(schedule)

#==========================
# Log Download Route
#==========================

# creates a protected downlaod endpoint for the event logging in render that requires a secret key to access, 
# ensuring that only authorized users can download the logs, 
# which is important for maintaining the privacy and security of the logged data.
@app.route("/download_logs", methods=["GET"])
def download_logs():
    key = request.args.get("key")
    secret_key = os.getenv("LOG_DOWNLOAD_KEY")

# rejects access if the provided key is missing or does not match the expected secret key, returning a 403 Unauthorized error.
    if not secret_key or key != secret_key:
        return jsonify({"error": "Unauthorized"}), 403

# builds a file path and returns a 404 if the file does not exist 
    log_path = os.path.join(os.path.dirname(__file__), "logs", "events.jsonl")

    if not os.path.exists(log_path):
        return jsonify({"error": "No logs found"}), 404
# downloads the file rather than displaying it in the browser, 
# ensuring that the logs can be securely accessed and stored by authorized users for analysis 
# while preventing unauthorized access to sensitive data.
    return send_file(log_path, as_attachment=True)


# =======================
# Server Runner
# =======================

# runs the Flask application when the script is executed directly,
# starting the server and allowing it to handle incoming requests.
if __name__ == "__main__":
    app.run(debug=False)