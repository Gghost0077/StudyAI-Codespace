from flask import Flask, jsonify, request
from scheduler import generate_schedule
from flask_cors import CORS

app = Flask(__name__)   
CORS(app)

@app.route("/ping", methods=["GET"])
def ping():
    print("PING HIT")
    return jsonify({"status": "ok"})

@app.route('/generate_schedule', methods=['POST'])
def generate():
    data = request.get_json()
    print("Incoming payload:", data)  # Debugging statement to check the incoming data
    
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    
    modules = data.get('modules', [])
    availability = data.get('availability', [])
    ai_enabled = data.get('ai_enabled', False)

    if not modules or not availability:
        return jsonify({'error': 'Modules and availability are required'}), 400
    
    schedule = generate_schedule(modules, availability, ai_enabled)

    print("Returned keys:", schedule.keys())
    print("Returned sessions:", len(schedule.get("sessions", [])))
    print("Returned warnings:", schedule.get("warnings", []))

    return jsonify(schedule)



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)