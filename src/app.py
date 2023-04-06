from flask import Flask, request, render_template, jsonify,url_for,redirect,session
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os, requests
import json

app = Flask(__name__)


# OAuth
app.secret_key = "super secret key"
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
secrets = json.load(open("client_secret.json", "r"))
weatherApi = secrets["openWeather"]
locationApi = secrets["location"]


# Default page
@app.route("/")
def hello():
	return render_template('home.html')

@app.route("/login")
def SpotifyLogin():
      sp_oauth = create_spotify_oauth()
      auth_url = sp_oauth.get_authorize_url()
      return redirect(auth_url)

@app.route("/logout", methods=['POST'])
def SpotifyLogout():
      session.clear()
      return render_template('home.html', message="You have been logged out.")


def create_spotify_oauth():
    return SpotifyOAuth(
            client_id=secrets["client_id"],
            client_secret=secrets["client_secret"],
        redirect_uri="http://127.0.0.1:5000/redirect/",
         scope="playlist-read-private")


def weatherSearch(name):
    URL = "https://api.openweathermap.org/data/2.5/weather?q="+name+"&APPID=" + weatherApi+"&units=imperial"
    response = requests.get(URL)
    return response.json()


def getLocation():
    URL = 'http://api.ipstack.com/check?access_key='+locationApi
    geo_req = requests.get(URL)
    geo_json = json.loads(geo_req.text)
    latitude = geo_json['latitude']
    longitude = geo_json['longitude']
    city = geo_json['city']
    return city

@app.route("/redirect/")
def redirectPage():
      cityName = getLocation()
      result = weatherSearch(cityName)
      return render_template('redirect.html', name='Tony') # weatherResponse=True, cityName=result.get("name"), temp=result.get("main").get("temp"), description=result.get("weather")[0].get("description"), h=result.get("main").get("humidity"))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
   
