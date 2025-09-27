
from flask import jsonify, request
import threading
import uuid
import time
from typing import Dict, Any
import queue
from flask import Response

from parser.parser import GUIClient, code_please, parse_response

from threading import Event

def handle_message(socketio, query_event: Event, message: str):
    print(f"Handling message {message}")

    actions = parse_response(code_please(message))

    t = GUIClient(socketio, actions, message)

    while(t.step() == 0):
        if not query_event.is_set():
            socketio.emit('query_response', { 'status': 'aborted'})
            return

        pass

    socketio.emit('query_response', { 'status': 'complete' })
