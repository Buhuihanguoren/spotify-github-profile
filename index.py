from api.app import app as application

# Vercel looks for `application` as the entry point
# (it runs like gunicorn — no need to call app.run())