from flask import Flask, request, render_template, jsonify,url_for,redirect, session, url_for
import webbrowser
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
import os, requests
import json, time
import requests

app = Flask(__name__)



# OAuth
app.secret_key = "super secret key"
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
secrets = json.load(open("client_secret.json", "r"))
weatherApi = secrets["openWeather"]
locationApi = secrets["location"]


#for spotify 
BASE_URL = 'https://api.spotify.com/v1/'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
redirect_uri = "http://127.0.0.1:5000/redirect/"
scope = ["user-read-private", "user-read-email", 'playlist-modify-public', 
                'playlist-modify-private', 'playlist-read-private', 'user-library-modify', 
                'user-library-read', 'user-top-read']
client_id=secrets["client_id"]
client_secret=secrets["client_secret"]
TOKEN_INFO='token_info'







# Default page
@app.route("/")
def hello():
	return render_template('home.html')



@app.route("/login")
def SpotifyLogin():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route("/logout")
def SpotifyLogout():
      session.clear()
      return render_template('home.html', message="You have been logged out.")



def create_spotify_oauth():
    return SpotifyOAuth(
            client_id=secrets["client_id"],
            client_secret=secrets["client_secret"],
        redirect_uri="http://127.0.0.1:5000/redirect/",
         scope=["user-read-private", "user-read-email", 'playlist-modify-public', 
                'playlist-modify-private', 'playlist-read-private', 'user-library-modify', 
                'user-library-read', 'user-top-read'])


def weatherSearch(name):
    URL = "https://api.openweathermap.org/data/2.5/weather?q="+name+"&APPID=" + weatherApi+"&units=imperial"
    response = requests.get(URL)
    return response.json()


def getLocation():
    URL = "https://api.ipdata.co?api-key="+locationApi
    response = requests.get(URL)
    geo=response.json()
    return geo['city'] 


     
 #gets the access code from oauth to exchange for the access token
@app.route("/redirect/")
def redirectPage():
    sp_oauth=create_spotify_oauth()
    session.clear()
    code=request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO]=token_info
    return redirect(url_for('getPlaylist', _external=True))


@app.route("/getPlaylist")
def getPlaylist():
    cityName = getLocation()
    result = weatherSearch(cityName)
    weatherCondition = result.get("weather")[0].get("description")

    try: 
        token_info=get_access_token()
    except:
         #user not logged in
         return redirect("/")
    
    #header to be passed to spotify api requests
    headers = {'Authorization': 'Bearer {token}'.format(token=token_info['access_token'])}

    username=getUserName(headers)
    return render_template('redirect.html', name=username , weatherResponse=True, cityName=result.get("name"), temp=result.get("main").get("temp"), description=result.get("weather")[0].get("description"), h=result.get("main").get("humidity"))


#function to get the access token which is needed to be passed into api requests
#will refresh the token if it is about to expire
def get_access_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
         raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
         sp_oauth = create_spotify_oauth()
         token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info 
 
#function to get username, if user is not registered in dashboard it will say user
def getUserName(headers):
    try:
        r = requests.get(BASE_URL + 'me', headers=headers)
        r.raise_for_status()
        r=r.json()
        return r['display_name']
    except:
         return "User!"
    

def getLikedSongs():

    #r= requests.get(BASE_URL + "me/tracks" , headers=headers)
    #r=r.json()
    return 'need to finish'
    #returns file containing (default 20) of the users liked songs

def userTopArtistSeeds():
   
    limit =5
    timeRange ="short_term"
    #r= requests.get(BASE_URL + "me/top/artists?limit=" +limit + "&time_range="+timeRange, headers=headers)
   # r=r.json()
    return "todo"

def userTopGenreSeeds():
    return "todo"
    

def userTopTracksSeeds():
     #need to get the top genres of a user to curate recs
    return "todo"

def getRecsClear():
     r=requests.get(BASE_URL + "recommendations")
     return "need to finish"


def getRecsRain():
     return 'TODO'
     
def getRecsDrizzle():
     #shower rain
     return 'TODO'

def getRecsThunder():
     return 'TODO'
     
def getRecsSnow():
     return 'TODO'

def getRecsClouds():
     #grouped together few clouds, scattered clouds, broken clouds
     return 'TODO'

def getRecsMist():
     return 'TODO'


if __name__ == "__main__":
    app.run(port=5000, debug=True)
   
