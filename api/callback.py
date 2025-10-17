from flask import Flask, Response, render_template, request
from dotenv import load_dotenv, find_dotenv
from util.firestore import get_firestore_db
from util import spotify
from time import time

load_dotenv(find_dotenv())

print("Starting Callback Server")

db = get_firestore_db()
app = Flask(__name__)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    code = request.args.get("code")
    error = request.args.get("error")

    # Handle user denying access
    if error:
        return Response(f"Authorization failed: {error}", status=400)

    if code is None:
        return Response("Missing authorization code", status=400)

    try:
        # Exchange code for token
        token_info = spotify.generate_token(code)
        
        if "error" in token_info:
            return Response(f"Spotify error: {token_info.get('error_description', 'Unknown error')}", status=400)
        
        access_token = token_info["access_token"]
        
        # Get user profile
        spotify_user = spotify.get_user_profile(access_token)
        
        if "error" in spotify_user:
            return Response("Failed to get user profile", status=400)
        
        user_id = spotify_user["id"]
        
        # Add expiration timestamp
        expired_ts = int(time()) + token_info.get("expires_in", 3600)
        token_info["expired_ts"] = expired_ts

        # Save to Firestore
        doc_ref = db.collection("users").document(user_id)
        doc_ref.set(token_info)

        rendered_data = {
            "uid": user_id,
            "BASE_URL": spotify.BASE_URL,
        }

        return render_template("callback.html.j2", **rendered_data)
    
    except Exception as e:
        print(f"Callback error: {e}")
        return Response(f"Server error: {str(e)}", status=500)


if __name__ == "__main__":
    app.run(debug=True)