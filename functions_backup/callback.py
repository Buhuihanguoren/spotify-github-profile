from flask import Response, render_template
from base64 import b64decode
import os
import json
from util import spotify  # Assuming this is in util/spotify.py—add if missing

# Firebase init (using global config from app.py, but local for callback)
from firebase_admin import credentials, firestore
import firebase_admin

print("Starting Server")

firebase_config = os.getenv("FIREBASE")  # Fallback for local; use global in production
if firebase_config:
    firebase_dict = json.loads(b64decode(firebase_config))
    cred = credentials.Certificate(firebase_dict)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

db = firestore.client()

def catch_all(path):
    code = request.args.get("code")

    if code is None:
        # TODO: no code
        return Response("not ok")

    token_info = spotify.generate_token(code)
    access_token = token_info["access_token"]

    spotify_user = spotify.get_user_profile(access_token)
    user_id = spotify_user["id"]

    doc_ref = db.collection("users").document(user_id)
    doc_ref.set(token_info)

    rendered_data = {
        "uid": user_id,
        "BASE_URL": spotify.BASE_URL,  # Assuming BASE_URL is in util/spotify.py
    }

    return render_template("callback.html.j2", **rendered_data)

# Export the handler for import in app.py
callback_handler = catch_all