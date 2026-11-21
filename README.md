# Spotify GitHub Profile Widget

A small serverless app that shows the track you're playing on Spotify as an SVG card, for a GitHub profile README.

This is my extended version of [kittinan/spotify-github-profile](https://github.com/kittinan/spotify-github-profile). My deployment only serves my own card, so to use it, deploy your own copy (see below).

My card, live:

![Spotify](https://spotify-github-profile-ashen5523-three.vercel.app/view?uid=v2kyn2tq6dtav2q5yf4bf9fik)

## Features

- The current track, or the last one played, as an SVG card
- Themes: default, compact, natemoo-re, novatorem, karaoke, apple, spotify-embed
- 30-second response cache, so the card doesn't hit the Spotify API on every view
- OAuth 2.0 login with automatic token refresh
- All credentials in environment variables, none in the repository
- A fallback card for every error state

## How it works

```
Request -> Vercel function -> cache check -> Spotify API (token from Firebase) -> SVG card
```

Built with Python and Flask on Vercel serverless functions, Firebase Firestore for the tokens, and the Spotify Web API.

## Run your own copy

1. Fork this repository and import it into [Vercel](https://vercel.com).
2. Create an app in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) and add the redirect URI `https://<your-project>.vercel.app/api/callback`.
3. In Vercel, set these environment variables: `SPOTIFY_CLIENT_ID`, `SPOTIFY_SECRET_ID`, `SPOTIFY_REDIRECT_URI`, `BASE_URL` and `FIREBASE` (your Firebase service-account JSON, base64-encoded).
4. Deploy, open `https://<your-project>.vercel.app/api/login` once, and copy the UID it shows.
5. Add the card to your profile README:

```markdown
![Spotify](https://<your-project>.vercel.app/view?uid=YOUR_UID)
```

Leave the Spotify app in development mode and add only your own account as a user in the dashboard. Then nobody else can log in through your deployment and have their tokens stored in your Firebase.

Optional parameters: `theme=compact`, `background_color=121212` and the others in `api/view.py`.

## Local development

```bash
pip install -r requirements.txt
cp .env.example .env    # fill in your own credentials
vercel dev              # then open http://localhost:3000/api/login
```

## Tests

```bash
pytest tests/ -v
pytest tests/ --cov=api --cov-report=html
```

## Known issues

- Local files playing on Spotify can return a 404 or 500 (a Spotify API limitation).
- Nothing shows during a Spotify private session.

## Credits

Based on [kittinan/spotify-github-profile](https://github.com/kittinan/spotify-github-profile), which was inspired by [natemoo-re](https://github.com/natemoo-re).
