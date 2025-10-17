import os
import json
import requests
from base64 import b64encode
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET_ID = os.getenv("SPOTIFY_SECRET_ID")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")
BASE_URL = os.getenv("BASE_URL")
REDIRECT_URI = SPOTIFY_REDIRECT_URI or f"{BASE_URL}/api/callback"

# Replace the placeholder URLs with actual Spotify API URLs
SPOTIFY_URL_TOKEN = "https://accounts.spotify.com/api/token"
SPOTIFY_URL_NOW_PLAYING = "https://api.spotify.com/v1/me/player/currently-playing?additional_types=track,episode"
SPOTIFY_URL_RECENTLY_PLAY = "https://api.spotify.com/v1/me/player/recently-played?limit=10"
SPOTIFY_URL_USER_INFO = "https://api.spotify.com/v1/me"

class InvalidTokenError(Exception):
    pass

def _auth_header():
    # Helper for client credential auth
    auth_str = f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_SECRET_ID}'
    return {"Authorization": f"Basic {b64encode(auth_str.encode()).decode('ascii')}"}

def generate_token(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    res = requests.post(SPOTIFY_URL_TOKEN, data=data, headers=_auth_header())
    return res.json()

def refresh_token(refresh_token):
    data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
    res = requests.post(SPOTIFY_URL_TOKEN, data=data, headers=_auth_header())
    return res.json()

def get_user_profile(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    return requests.get(SPOTIFY_URL_USER_INFO, headers=headers).json()

def get_now_playing(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    return requests.get(SPOTIFY_URL_NOW_PLAYING, headers=headers).json()

def get_recently_play(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    return requests.get(SPOTIFY_URL_RECENTLY_PLAY, headers=headers).json()