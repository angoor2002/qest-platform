from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from agentic_workflow import agentic_workflow

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], methods=["POST"], supports_credentials=True)

@app.route('/chat', methods=['POST'])
def chat_handler():
    data = request.get_json()
    session_id = data.get('session_id')
    message = data.get('message')

    if not session_id or not message:
        return jsonify({"error": "Missing 'session_id' or 'message'"}), 400

    result = agentic_workflow(message, session_id)
    if asyncio.iscoroutine(result):
        result = asyncio.run(result)

    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True)
