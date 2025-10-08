import functions_framework
from flask import request
from app import app  # Import your Flask instance from app.py

@functions_framework.http
def spotify_api(request):
    """Entrypoint for all API routes."""
    with app.test_request_context(path=request.path, method=request.method, headers=dict(request.headers), body=request.get_data()):
        return app.full_dispatch_request()