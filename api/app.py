from flask import Flask, request, redirect, jsonify, Response, render_template
from util import spotify, firestore
import os, time, base64, random, json

app = Flask(__name__)
db = firestore.get_firestore_db()
CACHE_TOKEN_INFO = {}

# === AUTH ===
@app.route("/api/login")
def login():
    login_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={spotify.SPOTIFY_CLIENT_ID}"
        f"&response_type=code"
        f"&scope=user-read-currently-playing,user-read-recently-played"
        f"&redirect_uri={spotify.REDIRECT_URI}"
    )
    return redirect(login_url)

@app.route("/api/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Missing authorization code", 400

    token_info = spotify.generate_token(code)
    if "error" in token_info:
        return jsonify(token_info)

    access_token = token_info.get("access_token")
    user = spotify.get_user_profile(access_token)
    uid = user.get("id")

    expired_ts = int(time.time()) + token_info["expires_in"]
    doc_ref = db.collection("users").document(uid)
    doc_ref.set({
        "access_token": token_info["access_token"],
        "refresh_token": token_info.get("refresh_token"),
        "expired_ts": expired_ts,
    })

    return f"""
        <html>
            <head>
                <title>Success!</title>
            </head>
            <body style="background-color: #282c34; color: white; font-family: monospace; padding: 20px;">
                <h1>✅ Success!</h1>
                <p>You are logged in as **{user.get('display_name')}**.</p>
                <p>Your unique Spotify ID (UID) is: <code>{uid}</code></p>
                <p>Use the following code in your GitHub README:</p>
                <pre style="background-color: #1e1e1e; padding: 15px; border-radius: 5px; overflow-x: auto;">
<a href="https://open.spotify.com/user/{uid}" target="_blank">
  <img src="{spotify.BASE_URL.replace('/api', '')}/?uid={uid}&theme=default" />
</a>
                </pre>
                <p>Remember to **star** the <a href="https://github.com/kittinan/spotify-github-profile" target="_blank" style="color: #61afef;">repository</a>!</p>
            </body>
        </html>
    """