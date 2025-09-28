from flask import Flask, jsonify, request, make_response
from flask_socketio import SocketIO, send, emit
import os

import threading
from parser.parser import parse_response, code_please, GUIClient

import gevent

from stt import Transcriber

from io import BytesIO

stop_query = threading.Event()

transcriber = Transcriber()

def create_app() -> Flask:
    """Create and configure the Flask app."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '0000'
    return app

app = create_app()
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5173"])

# SocketIO setup
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('response', {'data': 'Connected to server'})

def handle_message(message: str):
    if 'email' in message:
        os.system('cd ../../../mastra')
        os.system(f'npx tsx ./manualEmail.ts "{message}"')
        return
    
    actions = parse_response(code_please(message))

    t = GUIClient(socketio, actions, message)

    while not stop_query.is_set() and t.step() == 0:
        pass

    socketio.emit('query_response', { 'status': 'complete' })
    gevent.sleep(0)

@socketio.on('query')
def handle_query(message):
    socketio.start_background_task(handle_message, message)

@socketio.on('abort')
def handle_abort():
    stop_query.set()
    pass

@socketio.on('begin-recording')
def handle_begin_recording():
    transcriber.begin_recording()

@socketio.on('end-recording')
def handle_end_recording():
    transcriber.end_recording()

    prompt = transcriber.transcribe()

    socketio.emit('transcribed_prompt', { 'prompt' : prompt })

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
