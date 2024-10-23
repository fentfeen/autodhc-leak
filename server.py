import logging
from flask import Flask, jsonify

# Disabling request prints
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Sends orders
app = Flask(__name__)

@app.route('/', methods=['GET'])
def send_message():
    return jsonify({"reply": "setting things up"}), 240

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
