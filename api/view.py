from flask import Flask, Response, render_template, request
from base64 import b64encode
from dotenv import load_dotenv, find_dotenv
from util.firestore import get_firestore_db
from util.profanity import profanity_check
from PIL import Image, ImageFile
from time import time
import io
from util import spotify
import random
import requests
import functools
import colorgram
import html

load_dotenv(find_dotenv())

ImageFile.LOAD_TRUNCATED_IMAGES = True

print("Starting Server")

db = get_firestore_db()
CACHE_TOKEN_INFO = {}
# Add response cache with timestamp
CACHE_SVG_RESPONSE = {}

app = Flask(__name__, template_folder='templates')

# === UTILS ===

def isLightOrDark(rgb, threshold=128):
    return "dark" if (rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114) < threshold else "light"

@functools.lru_cache(maxsize=128)
def generate_css_bar(num_bar=75):
    css_bar = ""
    left = 1
    for i in range(1, num_bar + 1):
        anim = random.randint(350, 500)
        css_bar += (
            ".bar:nth-child({})  {{ left: {}px; animation-duration: {}ms; }}".format(
                i, left, anim
            )
        )
        left += 4
    return css_bar

@functools.lru_cache(maxsize=128)
def load_image(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error loading image from {url}: {e}")
        return None

def make_svg(
    artist_name,
    song_name,
    img_b64,
    is_now_playing,
    cover_image,
    theme,
    bar_color,
    show_offline,
    background_color,
    mode,
    progress_ms,
    duration_ms,
):
    height = 525 if cover_image else 145

    if is_now_playing:
        title_text = "Now playing"
        content_bar = "".join(["<div class='bar'></div>" for _ in range(75)])
    elif show_offline:
        title_text = "Not playing"
        content_bar = ""
    else:
        title_text = "Recently played"
        content_bar = "".join(["<div class='bar'></div>" for _ in range(75)])

    css_bar = generate_css_bar(75)

    rendered_data = {
        "height": height,
        "artist_name": html.escape(artist_name),
        "song_name": html.escape(song_name),
        "img": img_b64,
        "cover_image": bool(cover_image),
        "is_now_playing": is_now_playing,
        "bar_color": bar_color,
        "background_color": background_color,
        "content_bar": content_bar,
        "css_bar": css_bar,
        "title_text": title_text,
    }

    svg_output = render_template(f"spotify.{theme}.html.j2", **rendered_data)
    return svg_output

# === API LOGIC ===

def get_access_token(uid):
    # 1. Check in-memory cache
    if uid in CACHE_TOKEN_INFO and CACHE_TOKEN_INFO[uid]["expired_ts"] > time():
        return CACHE_TOKEN_INFO[uid]["access_token"]
    
    # 2. Check Firestore
    doc_ref = db.collection("users").document(uid)
    doc = doc_ref.get()
    if not doc.exists:
        return None

    token_info = doc.to_dict()
    
    # 3. Check if current token is valid
    if token_info["expired_ts"] > time():
        CACHE_TOKEN_INFO[uid] = token_info
        return token_info["access_token"]
        
    # 4. Refresh token
    refresh_token = token_info.get("refresh_token")
    if not refresh_token:
        raise spotify.InvalidTokenError
        
    new_token_info = spotify.refresh_token(refresh_token)
    
    if "error" in new_token_info:
        if new_token_info["error"] == "invalid_grant":
            doc_ref.delete()
        raise spotify.InvalidTokenError

    # Update token in Firestore and cache
    expired_ts = int(time()) + new_token_info["expires_in"]
    token_info["access_token"] = new_token_info["access_token"]
    token_info["expired_ts"] = expired_ts
    
    doc_ref.set(token_info)
    CACHE_TOKEN_INFO[uid] = token_info
    
    return token_info["access_token"]

def get_song_info(uid, show_offline=False):
    # 1. Get Access Token
    try:
        access_token = get_access_token(uid)
    except spotify.InvalidTokenError:
        return {
            "error": "invalid_token",
            "is_playing": False,
            "item": {"name": "Please reconnect", "type": "offline", "album": {"images": []}},
            "currently_playing_type": "track",
            "progress_ms": 0,
            "duration_ms": 1,
            "is_now_playing": False
        }
    
    if not access_token:
        return {
            "error": "no_token",
            "is_playing": False,
            "item": {"name": "Not authenticated", "type": "offline", "album": {"images": []}},
            "currently_playing_type": "track",
            "progress_ms": 0,
            "duration_ms": 1,
            "is_now_playing": False
        }

    # 2. Get Currently Playing Track
    is_now_playing = True
    song_info = spotify.get_now_playing(access_token)
    
    if song_info.get("is_playing") is False or "item" not in song_info:
        # 3. If not playing, get the most recent track
        song_info = spotify.get_recently_play(access_token)
        is_now_playing = False
        
        if not song_info.get("items"):
            return {
                "is_playing": False,
                "item": {"name": "No recent tracks", "type": "offline", "album": {"images": []}},
                "currently_playing_type": "track",
                "progress_ms": 0,
                "duration_ms": 1,
                "is_now_playing": False
            }
        
        song_info = song_info["items"][0]
        song_info["is_playing"] = False
        song_info["currently_playing_type"] = song_info["track"]["type"]
        song_info["item"] = song_info["track"]
        song_info["progress_ms"] = 0
        song_info["duration_ms"] = song_info["item"]["duration_ms"]

    item = song_info["item"]
    currently_playing_type = song_info["currently_playing_type"]
    is_playing = song_info.get("is_playing", False)
    progress_ms = song_info.get("progress_ms", 0)
    duration_ms = item.get("duration_ms", 1)

    return {
        "is_playing": is_playing,
        "item": item,
        "currently_playing_type": currently_playing_type,
        "progress_ms": progress_ms,
        "duration_ms": duration_ms,
        "is_now_playing": is_now_playing
    }

# === MAIN ROUTE ===

@app.route("/")
@app.route("/api/view.py")
@app.route("/<path:path>")
def catch_all(path=None):
    # Get parameters
    uid = request.args.get("uid")
    theme = request.args.get("theme", "default")
    show_offline = request.args.get("show_offline", "false").lower() == "true"
    interchange = request.args.get("interchange", "false").lower() == "true"
    background_color = request.args.get("background_color", "0d1117").lower()
    is_skip_dark = request.args.get("is_skip_dark", "true").lower() == "true"
    is_enable_profanity = request.args.get("is_enable_profanity", "true").lower() == "true"
    mode = request.args.get("mode", "light").lower()
    
    # Create cache key
    cache_key = f"{uid}:{theme}:{show_offline}:{interchange}:{background_color}:{is_skip_dark}:{is_enable_profanity}:{mode}"
    
    # Check response cache (30 second TTL)
    current_time = time()
    if cache_key in CACHE_SVG_RESPONSE:
        cached_data = CACHE_SVG_RESPONSE[cache_key]
        if current_time - cached_data["timestamp"] < 30:
            return Response(
                cached_data["svg"],
                mimetype="image/svg+xml",
                headers={
                    "Cache-Control": "s-maxage=30, stale-while-revalidate",
                }
            )
    
    # Set default values for offline state
    artist_name = "Spotify"
    song_name = "Not Playing"
    img_b64 = b64encode(b"").decode("ascii")
    is_now_playing = False
    cover_image = b""
    bar_color = "53b14f"
    progress_ms = 0
    duration_ms = 1

    if not uid:
        pass  # Will render offline card
    else:
        try:
            song_info = get_song_info(uid, show_offline)
            
            # Handle errors gracefully
            if "error" in song_info:
                error_type = song_info["error"]
                if error_type == "invalid_token":
                    artist_name = "Spotify"
                    song_name = "Please reconnect"
                elif error_type == "no_token":
                    artist_name = "Spotify"
                    song_name = "Not authenticated"
                is_now_playing = False
            else:
                item = song_info["item"]
                currently_playing_type = song_info["currently_playing_type"]
                is_now_playing = song_info["is_now_playing"]
                progress_ms = song_info["progress_ms"]
                duration_ms = song_info["duration_ms"]
                
                # Extract cover image URL and load it
                image_url = item.get("album", {}).get("images", [{}])[0].get("url")
                if image_url:
                    cover_image = load_image(image_url)
                
                if cover_image:
                    # Resize and convert to Base64
                    img = Image.open(io.BytesIO(cover_image))
                    img = img.resize((300, 300), Image.LANCZOS)
                    
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG", optimize=True)
                    img_b64 = b64encode(buffered.getvalue()).decode("ascii")
                    
                    # Extract color for bar
                    try:
                        colors = colorgram.extract(io.BytesIO(cover_image), 10)
                    except Exception as e:
                        print(f"Error extracting colors from image: {e}")
                        colors = []

                    for color in colors:
                        rgb = color.rgb
                        light_or_dark = isLightOrDark([rgb.r, rgb.g, rgb.b], threshold=80)

                        if light_or_dark == "dark" and is_skip_dark:
                            continue

                        bar_color = "%02x%02x%02x" % (rgb.r, rgb.g, rgb.b)
                        break

                # Find artist_name and song_name
                if currently_playing_type == "track":
                    artist_name = item["artists"][0]["name"]
                    song_name = item["name"]
                elif currently_playing_type == "episode":
                    artist_name = item["show"]["publisher"]
                    song_name = item["name"]

                # Handle profanity filtering
                if is_enable_profanity:
                    artist_name = profanity_check(artist_name)
                    song_name = profanity_check(song_name)

                if interchange:
                    artist_name, song_name = song_name, artist_name

        except Exception as e:
            print(f"Unhandled error: {e}")
            artist_name = "Spotify"
            song_name = "Temporarily unavailable"
            is_now_playing = False

    # Generate SVG
    svg = make_svg(
        artist_name,
        song_name,
        img_b64,
        is_now_playing,
        cover_image,
        theme,
        bar_color,
        show_offline,
        background_color,
        mode,
        progress_ms,
        duration_ms,
    )
    
    # Cache the response
    CACHE_SVG_RESPONSE[cache_key] = {
        "svg": svg,
        "timestamp": current_time
    }
    
    # Clean old cache entries (keep cache size reasonable)
    if len(CACHE_SVG_RESPONSE) > 100:
        oldest_keys = sorted(CACHE_SVG_RESPONSE.keys(), 
                           key=lambda k: CACHE_SVG_RESPONSE[k]["timestamp"])[:20]
        for key in oldest_keys:
            del CACHE_SVG_RESPONSE[key]

    resp = Response(
        svg,
        mimetype="image/svg+xml",
        headers={
            "Cache-Control": "s-maxage=30, stale-while-revalidate",
        },
    )
    return resp