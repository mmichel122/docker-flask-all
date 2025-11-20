import os
from flask import Flask, jsonify

app = Flask(__name__)

# Root endpoint
@app.route('/')
def hello():
    target = os.environ.get('TARGET', 'LIVE DEMO 101')
    return f"Hello {target}!"

# Liveness probe (is the container alive?)
@app.route('/healthz')
def health():
    return jsonify(status="ok", message="alive"), 200

# Readiness probe (is the app ready to serve traffic?)
@app.route('/ready')
def readiness():
    return jsonify(status="ok", message="ready"), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)
