from flask import Flask, jsonify, request, make_response
from flask_socketio import SocketIO, send, emit

from handlers import handle_message

from threading import Event

query_event = Event()
query_thread = None

def create_app() -> Flask:
    """Create and configure the Flask app."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '0000'

    # Simple CORS handling for local development. This echoes the Origin
    # header back when it matches an allowed dev origin. For production,
    # use flask-cors or configure CORS at the reverse proxy.
    ALLOWED_ORIGINS = {"http://localhost:5173", "http://127.0.0.1:5173"}

    @app.before_request
    def handle_preflight():
        if request.method == 'OPTIONS':
            origin = request.headers.get('Origin')
            resp = make_response(('', 204))
            if origin and origin in ALLOWED_ORIGINS:
                resp.headers['Access-Control-Allow-Origin'] = origin
                resp.headers['Vary'] = 'Origin'
            resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
            resp.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            return resp

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        if origin and origin in ALLOWED_ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Vary'] = 'Origin'
        response.headers.setdefault('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        return response

    @app.route("/", methods=["GET"])
    def index():
        return jsonify(message="Hello from backend"), 200

    @app.route("/ping", methods=["GET"])
    def ping():
        return jsonify(status="ok"), 200

    @app.route("/message", methods=["POST"])
    def message():
        return handle_message(request)


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
socketio = SocketIO(app, cors_allowed_origins="*")

# SocketIO setup
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('response', {'data': 'Connected to server'})

@socketio.on('query')
def handle_query(message):
    global query_thread, query_event

    if query_thread is None:
        query_event.set()
        query_thread = socketio.start_background_task(handle_message, socketio, query_event, message)

@socketio.on('abort')
def handle_abort():
    global query_thread, query_event

    if query_thread is not None:
        query_event.clear()
        query_thread = None

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
