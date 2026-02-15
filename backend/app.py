from flask import Flask, jsonify, request
from scheduler import generate_schedule

app = Flask(__name__)
@app.route('/generate_schedule', methods=['POST'])
def generate():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    
    modules = data.get('modules', [])
    availability = data.get('availability', [])
    ai_enabled = data.get('ai_enabled', False)

    if not modules or not availability:
        return jsonify({'error': 'Modules and availability are required'}), 400
    
    schedule = generate_schedule(modules, availability, ai_enabled)

    return jsonify(schedule)

if __name__ == '__main__':
    app.run(debug=True)