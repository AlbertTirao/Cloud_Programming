from flask import Flask, render_template, request, redirect, session, url_for
import requests
import os
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

# Load API keys from .env file
load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
WEATHERAPI_KEY = os.getenv("OPEN_WEATHER_MAP")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Spotify OAuth setup
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-library-read user-read-private playlist-read-private"
)

def get_news():
    """Fetch latest US news from NewsAPI"""
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWSAPI_KEY}"
    response = requests.get(url)
    return response.json().get("articles", [])

def get_weather(city):
    """Fetch weather from OpenWeather API"""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHERAPI_KEY}&units=metric"
    response = requests.get(url)
    return response.json()

@app.route('/')
def home():
    # Weather and news data
    city = request.args.get('city', 'Dagupan')  # Default city is London
    news_articles = get_news()
    weather_data = get_weather(city)
    
    # Spotify data (checking if the user is authenticated)
    if not session.get("token_info"):
        return redirect(url_for("login"))
    
    token_info = session.get("token_info")
    sp = Spotify(auth=token_info['access_token'])
    
    # Get playlists of the current user
    results = sp.current_user_playlists()
    playlists = results['items']
    playlist_names = [p['name'] for p in playlists]
    
    return render_template('index.html', articles=news_articles, weather=weather_data, city=city, playlists=playlist_names)

@app.route('/login')
def login():
    # Redirect the user to Spotify's authorization page
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Get the authorization code from the query parameters
    code = request.args.get('code')
    
    # Use the authorization code to get the access token
    token_info = sp_oauth.get_access_token(code)
    
    # Store the token info in the session
    session['token_info'] = token_info
    
    # Redirect back to the home page
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
    
    
