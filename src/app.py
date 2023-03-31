from flask import Flask, request, render_template, jsonify,url_for,redirect,session
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import json

app = Flask(__name__)


# OAuth
app.secret_key = "super secret key"
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
secrets = json.load(open("client_secret.json", "r"))
    


# Default page
@app.route("/")
def hello():
	return render_template('home.html')

@app.route("/login")
def login():
      sp_oauth = create_spotify_oauth()
      auth_url = sp_oauth.get_authorize_url()
      return redirect(auth_url)

@app.route("/redirect/")
def redirectPage():
      return render_template('home.html')

def create_spotify_oauth():
    return SpotifyOAuth(
            client_id=secrets["client_id"],
            client_secret=secrets["client_secret"],
        redirect_uri="http://127.0.0.1:5000/redirect/",
         scope="playlist-read-private")




if __name__ == "__main__":
    app.run(port=5000, debug=True)
   
