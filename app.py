import os

from flask import Flask, request, redirect, session, url_for
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

# CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID") # 'ad91a46157df4ba080456f92c7a74ef8'
# CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET") # '9d4140d511c64467a582b075b990cbfe'

CLIENT_ID = 'ad91a46157df4ba080456f92c7a74ef8'
CLIENT_SECRET = '9d4140d511c64467a582b075b990cbfe'

redirect_uri = 'http://localhost:5000/callback'
scope = 'playlist-read-private'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
  client_id=CLIENT_ID,
  client_secret=CLIENT_SECRET,
  redirect_uri=redirect_uri,
  scope=scope,
  show_dialog=True
)

sp = Spotify(auth_manager=sp_oauth)


@app.route('/')
@app.route('/home')
def home():
  #return redirect(url_for('home'))
  playlists_html = '<h1>Hello</h1>'

  return playlists_html

  # Check if user is logged in
  
  
  #return redirect(url_for)

# Not a physical page, just a redirect
@app.route('/login')
def login():

  # Check if user is logged in
  if not sp_oauth.validate_token(cache_handler.get_cached_token()):
    auth_url = sp_oauth.get_authorize_url() #not logged in, take them to log in
    return redirect(auth_url)

  return redirect(url_for('home'))

@app.route('/history_form')
def history_form():
    pass

@app.route('/horoscope_form')
def horoscope_form():
    pass


@app.route('/callback')
def callback():
  sp_oauth.get_access_token(request.args['code'])
  return redirect(url_for('insights'))


@app.route('/insights')
def insights():
  # Check if user is logged in
  if not sp_oauth.validate_token(cache_handler.get_cached_token()):
    auth_url = sp_oauth.get_authorize_url() #not logged in, take them to log in
    return redirect(auth_url)
  
  playlists = sp.current_user_playlists()
  playlists_info  = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
  playlists_html = '<br>'.join([f'{name}: {url}' for name, url in playlists_info])

  return playlists_html

@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('home'))

@app.route('/results')
def results():
    pass

if __name__ == '__main__': 
  app.run(debug=True, host="0.0.0.0", port=5001)

