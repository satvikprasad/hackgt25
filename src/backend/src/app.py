from flask import Flask, jsonify, request

app = Flask(__name__)

def create_app() -> Flask:
	"""Create and configure the Flask app."""
	app = Flask(__name__)

	@app.route("/", methods=["GET"])
	def index():
		return jsonify(message="Hello from backend"), 200

	@app.route("/ping", methods=["GET"])
	def ping():
		return jsonify(status="ok"), 200

	@app.route("/echo", methods=["POST"])
	def echo():
		# Expect JSON body like: { "text": "..." }
		if not request.is_json:
			return jsonify(error="Request must be JSON"), 400
		data = request.get_json()
		text = data.get("text") if isinstance(data, dict) else None
		if text is None:
			return jsonify(error="Missing 'text' field"), 400
		return jsonify(text=text), 200

	return app

app = create_app()

if __name__ == "__main__":
	# For local development only. In production use a WSGI server.
	app.run(host="127.0.0.1", port=5000, debug=True)

from flask import Flask

app = Flask(__name__)
