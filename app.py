import os

from flask import Flask, request, redirect, session, url_for
import spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID") # 'ad91a46157df4ba080456f92c7a74ef8'
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET") # '9d4140d511c64467a582b075b990cbfe'
redirect_uri = 'http://localhost:5000/callback'
scope = 'playlist-read-private'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
  client_id=CLIENT_ID,
  client_secret=CLIENT_SECRET,
  redirect_uri=redirect_uri,
  scope=scope
  show_dialog=True
)

sp = Spotify(auth_manager=sp_oauth)


@app.route('/')
@app.route('/home')
def home():

  # Check if user is logged in
  '''
  if not sp_oauth.validate_token(cache_handler.get_cached_token()):
    auth_url = sp_oauth.get_authorize_url() #not logged in, take them to log in
    return redirect(auth_url)
  '''
  
  
  #return redirect(url_for)


@app.route('/callback')
def callback():
  sp_oauth.get_access_token(request.args['code'])
  return redirect(url_for('get_playlists'))


@app.route('/get_playlists')
def get_playlists():
  # Check if user is logged in
  if not sp_oauth.validate_token(cache_handler.get_cached_token()):
    auth_url = sp_oauth.get_authorize_url() #not logged in, take them to log in
    return redirect(auth_url)
  
  playlists = sp.current_user_playlists()
  playlists_info  = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
  playlists_html = '<br>'.join([f'{name}: {url}' for name, url in playlists_info])

  return playlists_display

@app.rount('/logout')
def logout():
  session.clear()
  return redirect(url_for('home'))

if __name__ == '__main__': 
  app.run(debug=True, host="0.0.0.0")

