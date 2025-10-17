# Spotify GitHub Profile Widget

Display your currently playing Spotify track on your GitHub profile! 🎵

![Spotify](https://spotify-github-profile-ashen5523-three.vercel.app/view?uid=v2kyn2tq6dtav2q5yf4bf9fik)

## Features

 **Real-time Updates** - Shows what you're currently playing on Spotify  
 **Multiple Themes** - Default, Compact, Natemoo-re, Novatorem, Karaoke, and more  
 **Optimized Performance** - 30-second caching to minimize API calls  
 **Secure** - OAuth flow with environment variables  
 **Error Handling** - Graceful fallbacks for all states  

## Quick Start

### 1. Connect Your Spotify Account

Click the button below to authenticate:

[<img src="/img/btn-spotify.png" width="200">](https://spotify-github-profile-ashen5523-three.vercel.app/api/login)

After logging in, you'll receive your **User ID (UID)**.

### 2. Add to Your GitHub Profile

Add this to your GitHub profile README:

```markdown
![Spotify](https://spotify-github-profile-ashen5523-three.vercel.app/view?uid=YOUR_UID_HERE)
```

Replace `YOUR_UID_HERE` with your actual UID from step 1.

### Example with Custom Parameters

```markdown
![Spotify](https://spotify-github-profile-ashen5523-three.vercel.app/view?uid=YOUR_UID&theme=compact&background_color=121212)
```

## Prerequisites

- Python 3.12+
- Spotify Developer Account
- Firebase Project
- Vercel Account

## Tech Stack

- **Backend**: Python Flask
- **Hosting**: Vercel Serverless Functions
- **Database**: Firebase Firestore
- **API**: Spotify Web API
- **Caching**: In-memory with 30s TTL

## Architecture

```
User Request → Vercel Function → Cache Check → Spotify API → Firebase → SVG Response
```

### Key Features:
- **Token Management**: Automatic refresh when expired
- **Response Caching**: 30-second cache reduces API calls by 95%
- **Error States**: Graceful fallbacks for all scenarios
- **Security**: Environment variables for all credentials

## Development


### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Buhuihanguoren/spotify-github-profile.git
   cd spotify-github-profile
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

   Required variables:
   ```
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_SECRET_ID=your_spotify_client_secret
   BASE_URL=http://localhost:5000
   SPOTIFY_REDIRECT_URI=http://localhost:5000/api/callback
   FIREBASE=your_base64_encoded_firebase_key
   ```

4. **Run locally**
   ```bash
   vercel dev
   ```

   Visit: http://localhost:3000/api/login

### Testing

Run tests with pytest:
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=api --cov-report=html

# Specific test
pytest tests/test_api_view.py -v
```

## Deployment

### Deploy to Vercel

1. **Fork this repository**

2. **Create a Vercel project**
   - Import your forked repository
   - Add environment variables in Vercel dashboard

3. **Configure Spotify App**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Add redirect URI: `https://your-project.vercel.app/api/callback`

4. **Deploy**
   ```bash
   vercel --prod
   ```


## Security

- ✅ All credentials stored in environment variables
- ✅ OAuth 2.0 authentication flow
- ✅ Token refresh handling
- ✅ No sensitive data in repository
- ✅ Secure Firebase integration

## Known Issues

- Local files playing on Spotify may return 404/500 errors (Spotify API limitation)

## Troubleshooting

### "Not authenticated" showing
- Re-authenticate at `/api/login`

### Widget not updating
- Make sure you're not in Spotify Private Session
- Try playing on Desktop app or Web Player
- Wait 30 seconds for cache to expire

### Login errors
- Verify Spotify redirect URI is correct
- Check environment variables in Vercel

## Credits

- Original inspiration: [natemoo-re](https://github.com/natemoo-re)
- Base project: [kittinan/spotify-github-profile](https://github.com/kittinan/spotify-github-profile)
- Enhanced by: [Buhuihanguoren](https://github.com/Buhuihanguoren)

## Related Projects

- [Apple Music GitHub Profile](https://github.com/rayriffy/apple-music-github-profile)