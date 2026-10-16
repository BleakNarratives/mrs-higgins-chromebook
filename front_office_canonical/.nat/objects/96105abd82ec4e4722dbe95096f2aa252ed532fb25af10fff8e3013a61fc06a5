import os
import json
import subprocess
import threading
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Data paths
LEDGER_PATH = "the_ledger.json"
INCOME_SUMMARY = "income_summary.json"
ROUTING_LOG = "front_desk_routing_log.json"
REPORT_PATH = "the_ledger_report.txt"
LOGS_DIR = "logs"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/briefing')
def get_briefing():
    # Simulate briefing.py logic or read its output
    # For now, let's just return a placeholder or try to read briefing output if it was saved
    # In a real scenario, we might run briefing.py and capture output
    try:
        result = subprocess.run(['python3', 'briefing.py'], capture_output=True, text=True)
        return jsonify({"output": result.stdout})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ledger')
def get_ledger():
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({"entries": []})

@app.route('/api/ship', methods=['POST'])
def ship_it():
    def run_pipeline():
        subprocess.run(['bash', 'mrs_higgins.sh'])

    thread = threading.Thread(target=run_pipeline)
    thread.start()
    return jsonify({"status": "Pipeline started"})

@app.route('/api/logs')
def get_latest_logs():
    if not os.path.exists(LOGS_DIR):
        return jsonify({"logs": "No logs found"})

    logs = sorted(os.listdir(LOGS_DIR), reverse=True)
    if not logs:
        return jsonify({"logs": "No logs found"})

    with open(os.path.join(LOGS_DIR, logs[0]), 'r') as f:
        return jsonify({"logs": f.read()})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=False)
