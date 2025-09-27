
from flask import jsonify, request
import threading
import uuid
import time
from typing import Dict, Any
import queue
from flask import Response



def handle_message(req):
	
	print(req)
	if not req.is_json:
		return jsonify(error="Request must be {'text': '...'}"), 400
	data = req.get_json()
	if not isinstance(data, dict):
		return jsonify(error="Request must be {'text': '...'}"), 400
	if data.get("text") is None:
		return jsonify(error="Request must be {'text': '...'}"), 400
	text = data["text"]

	
	return jsonify(message="it is working"), 202
