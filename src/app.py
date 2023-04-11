from flask import Flask, request, render_template, jsonify,url_for,redirect,session
import webbrowser
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
import os, requests
import json

app = Flask(__name__)



# OAuth
app.secret_key = "super secret key"
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
secrets = json.load(open("client_secret.json", "r"))
weatherApi = secrets["openWeather"]
locationApi = secrets["location"]


#for spotify 
BASE_URL = 'https://api.spotify.com/v1/'
client_id=secrets["client_id"]
client_secret =secrets['client_secret']




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



def getUserName():
    headers = {'Authorization': 'Bearer {token}'.format(token=session.get('acess_token'))}
    r = requests.get(BASE_URL + 'me', headers=headers)
    r=r.json()
    return 'user' #r['display_name']

def getLikedSongs():
    headers = {'Authorization': 'Bearer {token}'.format(token=session.get('acess_token'))}
    r= requests.get(BASE_URL + "me/tracks" , headers=headers)
    r=r.json()
    return 'need to finish'
    #returns file containing (default 20) of the users liked songs

def userTopArtistSeeds():
    headers = {'Authorization': 'Bearer {token}'.format(token=session.get('acess_token'))}
    limit =5
    timeRange ="medium_term"
    r= requests.get(BASE_URL + "me/top/artists?limit=" +limit + "&time_range="+timeRange, headers=headers)
    r=r.json()
    return "todo"


def userTopGenreSeeds():
    return "todo"
    

def userTopTracksSeeds():
     #need to get the top genres of a user to curate recs
    return "todo"

def getRecsClear():
     headers = {'Authorization': 'Bearer {token}'.format(token=session.get('acess_token'))}
     r=requests.get(BASE_URL + "recommendations", headers=headers)
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
     
 



@app.route("/redirect/")
def redirectPage():
    sp_oauth = create_spotify_oauth()
    code = request.args.get('code')
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    cityName = getLocation()
    result = weatherSearch(cityName)
    return render_template('redirect.html', name=getUserName() , weatherResponse=True, cityName=result.get("name"), temp=result.get("main").get("temp"), description=result.get("weather")[0].get("description"), h=result.get("main").get("humidity"))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
   
