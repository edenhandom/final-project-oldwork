import os
import json
import openai
import requests
from openai import OpenAI

import re
from markupsafe import Markup
from user_form import UserForm  # Adjust import path if needed
from flask import Flask, request, redirect, session, url_for, render_template, flash


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

#scope = "playlist-read-private,playlist-read-collaborative,user-top-read"

# FOR OPEN AI API
USER_KEY = 'sk-proj-YpstCq5l1SV5TtdFfr2lT3BlbkFJdnP8dkoexI8MXp3Mxb01'

# Create an OpenAPI client
client = OpenAI(api_key=USER_KEY)
    
#cache_handler = FlaskSessionCacheHandler(session)

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


# Call back enpoint
@app.route('/callback')
def callback():
  
  # login was unsuccessful
  if 'error' in request.args:
    return jsonify({"error": request.args['error']})
  
  # login was successful
  if 'code' in request.args:

    # build a request body to get access token
    req_body = {
      'code': request.args['code'],
      'grant_type': 'authorization_code',
      'redirect_uri': REDIRECT_URI,
      'client_id': CLIENT_ID,
      'client_secret': CLIENT_SECRET
    }

    response = requests.post(TOKEN_URL, data=req_body)
    token_info = response.json()

    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

    return redirect('/home')


@app.route('/insights')
def insights():
  # error logging in
  if 'access_token' not in session:
    return redirect('/login')
  
  # check if token has expired
  if datetime.now().timestamp() > session['expires_at']:
    return redirect('/refresh-token')
  
  # we're good to go atp
  headers = {
    'Authorization': f"Bearer {session['access_token']}"
  }

  response = requests.get(API_BASE_URL + 'me/playlists', headers=headers)
  playlists = response.json()

  print(f"\n\n\n Reached! \n\n PLaylists: {str(playlists)}, type: {type(playlists)}")


  return render_template('insights.html', text = str(playlists))


if __name__ == '__main__': 
  app.run(debug=True, host="0.0.0.0")

