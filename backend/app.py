from dotenv import load_dotenv
load_dotenv()

import os 
import json 
from datetime import datetime

from flask import Flask, jsonify, request
from scheduler import generate_schedule
from flask_cors import CORS





app = Flask(__name__)   
CORS(app)

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

#ping to test if it works
@app.route("/ping", methods=["GET"])
def ping():
    print("PING HIT")
    return jsonify({"status": "ok"})

#Sends data to generate schedule from index
@app.route('/generate_schedule', methods=['POST'])
def generate():
    data = request.get_json()
    print("Incoming payload:", data)  # Debugging statement to check the incoming data
    
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    
    modules = data.get('modules', [])
    availability = data.get('availability', [])
    ai_enabled = data.get('ai_enabled', False)
    ai_strictness = data.get("ai_strictness", "medium")

    if not modules or not availability:
        return jsonify({'error': 'Modules and availability are required'}), 400
    
    schedule = generate_schedule(modules, availability, ai_enabled, ai_strictness)

    print("Returned keys:", schedule.keys())
    print("Returned sessions:", len(schedule.get("sessions", [])))
    print("Returned warnings:", schedule.get("warnings", []))

    return jsonify(schedule)



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)