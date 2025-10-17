from flask import Flask, redirect, request
from dotenv import load_dotenv
import os
from urllib.parse import urlencode

load_dotenv()

app = Flask(__name__)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
BASE_URL = os.getenv("BASE_URL")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Spotify OAuth URLs
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"

# Scopes needed for your app
SCOPES = [
    "user-read-currently-playing",
    "user-read-recently-played",
]

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def login(path):
    """Redirect to Spotify authorization page"""
    
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "show_dialog": "false",  # Set to "true" to force auth dialog every time
    }
    
    auth_url = f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"
    
    return redirect(auth_url)

if __name__ == "__main__":
    app.run(debug=True, port=5001)