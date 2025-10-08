import importlib
import os
from flask import Flask, redirect, request, Response
import urllib.parse
from base64 import b64decode
import json
from firebase_admin import credentials, firestore
import firebase_admin
from dotenv import load_dotenv

# Load .env for local testing
load_dotenv()

# Try to load Firebase Functions config (deployed) or fallback to env vars (local)
try:
    import functions
    config = functions.config()
    SPOTIFY_CLIENT_ID = config.get('spotify', {}).get('client_id') or os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_SECRET_ID = config.get('spotify', {}).get('secret_id') or os.getenv('SPOTIFY_SECRET_ID')
    FIREBASE_CONFIG = config.get('app', {}).get('firebase_config') or os.getenv('FIREBASE')
except ImportError:
    # Local fallback
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_SECRET_ID = os.getenv('SPOTIFY_SECRET_ID')
    FIREBASE_CONFIG = os.getenv('FIREBASE')

# Initialize Firebase if config is available
if FIREBASE_CONFIG:
    firebase_dict = json.loads(b64decode(FIREBASE_CONFIG))
    cred = credentials.Certificate(firebase_dict)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
db = firestore.client() if 'firebase_admin' in globals() else None  # Only if initialized

BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:3000/api')  # Fallback for local

app = Flask(__name__)

# Import handlers (after refactoring callback.py and view.py as instructed)
from callback import callback_handler
from view import view_handler

@app.route('/')
def index():
    return redirect('/api/login')

@app.route('/api/login')
def login():
    auth_url = 'https://accounts.spotify.com/authorize'
    params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': f"{BASE_URL}/callback",
        'scope': 'user-read-currently-playing,user-read-recently-played',
        'show_dialog': False
    }
    url = auth_url + '?' + urllib.parse.urlencode(params)
    return redirect(url)

@app.route('/api/callback/<path:path>')
def callback(path):
    return callback_handler(path)  # Calls the refactored function from callback.py

@app.route('/api/view/<path:path>')
def view(path):
    return view_handler(path)  # Calls the refactored function from view.py (for now-playing widget)

# Optional: Alias for now-playing (common URL)
@app.route('/api/now-playing/<path:path>')
def now_playing(path):
    return view_handler(path)  # Same as /api/view
