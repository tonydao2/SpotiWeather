from flask import Flask, request, render_template, jsonify,url_for,redirect,session
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)


# OAuth
app.secret_key = "super secret key"
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'


# Default page
@app.route("/")
def hello():
	return render_template('home.html')

@app.route("/login")
def login():
      sp_oauth = create_spotify_oauth()
      auth_url = sp_oauth.get_authorize_url()
      return redirect(auth_url)

@app.route("/redirect")
def redirectPage():
      return 'redirected'

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = "a6fa6ca9891241a78bafe9fcea216bf0",
        client_secret = "535a6e79540f405e9530b56ebcb2953a",
        redirect_uri=url_for('redirectPage', _external=True),
         scope="playlist-read-private")




if __name__ == "__main__":
    app.run(port=5000, debug=True)