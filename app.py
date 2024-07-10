import os
import json
import openai
import requests
from openai import OpenAI

import re
from markupsafe import Markup
from user_form import UserForm  # Adjust import path if needed
from flask import Flask, request, redirect, session, url_for, render_template, flash


from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler


# new !
import requests
import urllib.parse
from datetime import datetime
from flask import Flask, redirect, request, jsonify, session


app = Flask(__name__)
#app.config['SECRET_KEY'] = os.urandom(64)
app.secret_key = '53d355f8-571a-4590-a310-1f95579440851'

# FOR SPOTIFY API
CLIENT_ID='8d7ad77d655b4509a54d8f842b409e2e'
CLIENT_SECRET='fe0c23212bfe46858fc51a15c1fa6606'
REDIRECT_URI='http://localhost:5000/callback'

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

''''

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

# CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID") # 'ad91a46157df4ba080456f92c7a74ef8'
# CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET") # '9d4140d511c64467a582b075b990cbfe'

# FOR SPOTIFY API
CLIENT_ID = 'ad91a46157df4ba080456f92c7a74ef8'
CLIENT_SECRET = '9d4140d511c64467a582b075b990cbfe'


Something wrong with our callback? I changed it to 3000 but idk what that did
Maybe it has to match our port?

redirect_uri = 'http://localhost:3000/callback'
scope = "playlist-read-private,playlist-read-collaborative,user-top-read"
'''

# FOR OPEN AI API
USER_KEY = 'sk-proj-YpstCq5l1SV5TtdFfr2lT3BlbkFJdnP8dkoexI8MXp3Mxb01'
# Create an OpenAPI client
client = OpenAI(api_key=USER_KEY)



@app.route('/')
def hello_world():
  return render_template('home.html')

# User clicked login button vvv
@app.route('/login')
def login():
  scope = 'user-read-private user-read-email'

  params = {
    'client_id': CLIENT_ID,
    'response_type': 'code',
    'scope': scope,
    'redirect_uri': REDIRECT_URI,
    'show_dialog': True # usually false -> for testing purposes
  }

  auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

  return redirect(auth_url)

@app.route('/home')
def home():
  return render_template('home.html')


@app.route('/callback')
def callback():
  token_info = sp_oauth.get_access_token(request.args['code'])
  print(f' HERE' , token_info)
  return redirect(url_for('home'))

@app.route('/history_form')
def history_form():
  """
    - I must first check if the user is logged in
    - If they are logged in then I want to return their top items
    - if not, I want to give a message that theyre not logged in, log in here then retry.
      then have a button that will lead to the login page
      then once they log in, they will be redirected to the home page to try again
    • Endpoint for followed artists
    • Endpoint for most played artists/songs (get top artists/tracks)
    ◦Grab Spotify data (JSON), clean up, & store in DB
    ◦ Allow for user input and store into database as well

    Functions:

      Are they logged in?
        if they are, run Retrieve
        if not, print error message, have two buttons: home and login
      Retrieve User's top songs/artists
  """
  error_message = ""
  followed = ""

  token_info = cache_handler.get_cached_token()
  if not sp_oauth.validate_token(token_info):
    error_message = "You are not logged in, so we cannot access your Spotify information! Please log in."
    # return redirect(url_for(''))
  
  try:
    followed = sp.current_user_followed_artists(limit=20, after=None)
  except SpotifyException as e:
    error_message += f" \n An error occurred: {e}"
  finally:
    return render_template('history_form.html', followed = followed, error_message = error_message)


  # print()
  # top_artists = sp.current_user_top_artists(limit=20, offset=0, time_range='medium_term')
  # top_tracks = sp.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')
  # print(top_artists)
  # print(top_tracks)


  # return render_template('history_form.html')



# Adding User Form page to website
@app.route('/user_form', methods=['GET', 'POST'])
def user_form():
    form = UserForm()
    if form.validate_on_submit():
        # Store form data in session
        session['user_data'] = {
            'star_sign': form.star_sign.data,
            'personality_traits': form.personality_traits.data,
            'fav_genre1': form.fav_genre1.data,
            'fav_genre2': form.fav_genre2.data,
            'fav_genre3': form.fav_genre3.data}
        
        flash(f'Details submitted successfully!', 'success')
        
        # Redirects to a new page, "submit_page"
        return redirect(url_for('submit_page'))
   
    return render_template('user_form.html', title='Info', form=form)

# Get response from Chat GPT
def get_chat_response(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": 
            ("You are a musical genius that's good at reading people.")},
            {"role": "user", "content": prompt}
            ]
    )
    message = response.choices[0].message.content
    return message


# For submission page, brings user here after they submit form
@app.route('/submit_page')
def submit_page():
    # Retrieve user data from session
    user_data = session.get('user_data', None)
    
    if user_data:
        
        star_sign = user_data.get('star_sign', 'Unknown')
        personality_traits = user_data.get('personality_traits', 'Unknown')
        fav_genre1 = user_data.get('fav_genre1', 'Unknown')
        fav_genre2 = user_data.get('fav_genre2', 'Unknown')
        fav_genre3 = user_data.get('fav_genre3', 'Unknown')
        
        prompt = (
            f"Give me a playlist of recommended songs based on my "
            f"star sign: {star_sign}, personality traits: {personality_traits}, "
            f"and my preference of these genres: {fav_genre1}, {fav_genre2}, {fav_genre3}. "
            f"Please list each song on a new line, song title only in quotes. "
            f"Format like: 'Song1'\n 'Song2'\n...'"
            )
        
        recommendations = get_chat_response(prompt)
        #print(recommendations)
        #rec_links = make_urls_clickable(recommendations)
        song_list = extract_song_titles(recommendations)
        
        # This code doesn't work right now but may function if we can login
        song_ids = []
        for song in song_list:
            track_id = get_track_id(song)
            print(f"Track ID for {song}:", track_id)  # Debugging print

            if track_id:
               song_ids.append(track_id)
        
        # Broken
        #song_links = [get_song_link(id) for id in song_ids if id]        
        
        return render_template('submit_page.html', 
                               title='Submitted Data', 
                               user_data=user_data, 
                               recommendations=song_list
                               )
        
        
    else:
        flash('No data submitted!', 'error')
        return redirect(url_for('user_form'))


# Extract a song title from Chat GPT response
def extract_song_titles(input_string):
    
    # Regular expression pattern to match the song titles
    pattern = r'"([^"]+)"'
    
    # Using re.findall to extract all occurrences of the pattern
    matches = re.findall(pattern, input_string)

    # Return the list of song titles
    return matches


'''
This works now!!!!! ha ha ha
'''
# Get track ID from a track name
def get_track_id(track_name):
    
    base_url = 'https://api.spotify.com/v1/search'
    searchResults = sp.search(q="track:" + track_name, type="track", limit=1)
    tracks = searchResults.get('tracks', {}).get('items', [])
    if tracks:
        return tracks[0]['id']
    else:
        return None


'''
Try to make this work
'''
# Get a song link from a track ID
def get_song_link(track_id):
    # Base URL for Spotify track links
    base_url = 'https://open.spotify.com/track/'
    
    # Construct the full Spotify track link
    track_link = base_url + track_id
    
    return track_link


# Make a link clickable
def make_urls_clickable(text):
    url_pattern = re.compile(r'(https://\S+)')
    return url_pattern.sub(r'<a href="\1" target="_blank">\1</a>', text)


@app.route('/insights')
def insights():
  
  # Check if user is logged in
  token_info = sp_oauth.get_access_token() 
  print(f'INSIGHTS', token_info)
  validate_info = sp_oauth.validate_token(token_info)
  print(f'INSIGHTS 2', validate_info)
  if not validate_info:
    auth_url = sp_oauth.get_authorize_url() #not logged in, take them to log in
    return redirect(auth_url)
  
  
  # Get all of user's playlists
  playlists = sp.current_user_playlists()
  playlists_info = [(pl['id'], pl['name']) for pl in playlists['items']]
  playlists_html = '<br>'.join([f'{name}: {url}' for name, url in playlists_info])

  # choice by user to pick playlists or use all
  if request.method == 'POST':
    selected_playlist_ids = request.form.getlist('playlist_ids')
    selected_playlists = {}
    if 'all_playlists' in selected_playlist_ids:
      selected_playlist_ids = [pl['id'] for pl in playlists ['items']]
    for playlist_id in selected_playlist_ids:
      playlist = sp.playlist(playlist_id)
      tracks_info = [(track['track']['name'], track['track']['artists'][0]['name']) for track in playlist['tracks']['items']]
      selected_playlists[playlist_id] = tracks_info
    return redirect(url_for('personality')) #for insights page, but this would take these insights to the results page 

  # Make render_dropdown_menu
  return render_template('insights.html', text = playlists_html)
  
  # I copied something from chat (doesnt work) (i think we can use this)
'''
    token_info = sp_oauth.get_cached_token()
    if not token_info or not sp_oauth.validate_token(token_info):
      auth_url = sp_oauth.get_authorize_url()
      return redirect(auth_url)

    sp = Spotify(auth=token_info['access_token'])
    try:
      playlists = sp.current_user_playlists(limit=50)
      playlists_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
      playlists_html = '<br>'.join([f'{name}: {url}' for name, url in playlists_info])
      return render_template('insights.html', text=playlists_html)
    except Exception as e:
      flash(f"Error: {str(e)}", 'danger')
      return redirect(url_for('home'))
'''

@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('home'))

@app.route('/results')
def results():
    pass


'''
Changed the port here to 3000
'''
if __name__ == '__main__': 
  app.run(debug=True, host="0.0.0.0", port=3000)

