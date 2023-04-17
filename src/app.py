from flask import Flask, request, render_template, jsonify,url_for,redirect, session, url_for
import webbrowser, spotipy, math
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
import os, requests, random
import json, time
from datetime import date
import requests

app = Flask(__name__)



# OAuth
app.secret_key = "super secret key"
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
secrets = json.load(open("client_secret.json", "r"))
if os.path.exists(".cache"):
  os.remove(".cache")
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
    session['headers']=headers
    trackList = userTopTracksSeeds(headers)
    genreList =userTopGenreSeeds(headers)
    artistList = userTopArtistSeeds(headers)
    winterTracks = ','.join(random.choices(["0bYg9bo50gSsH3LtXe2SQn", "0lizgQ7Qw35od7CYaoMBZb", "2uFaJJtFpPDc5Pa95XzTvg", "7uoFMmxln0GPXQ0AcCBXRq", "2L9QLAhrvtP4EYg1lY0Tnw", "5PuKlCjfEVIXl0ZBp5ZW9g", "65irrLqfCMRiO3p87P4C0D", "5Q2P43CJra0uRAogjHyJDK", "0qcr5FMsEO85NAQjrlDRKo", "1jhljxXlHw8K9rezXKrnow", "2QjOHCTQ1Jl3zawyYOpxh6"], k=2))
    winterGenres = "Christmas"

    print(trackList)
    print(genreList)
    print(artistList)
    print(weatherCondition)
    if weatherCondition=="clear":
        recs = getRecsClear(trackList, genreList, artistList, headers)
    elif weatherCondition =="rain":
         recs = getRecsRain(trackList, genreList, artistList, headers)
    elif weatherCondition =="drizzle":
         recs = getRecsDrizzle(trackList, genreList, artistList, headers)
    elif weatherCondition == "thunder":
         recs = getRecsThunder(trackList, genreList, artistList, headers)
    elif weatherCondition =="few clouds" or weatherCondition =="scattered clouds" or weatherCondition =="broken clouds":
         recs = getRecsClouds(trackList, genreList, artistList, headers)
    elif weatherCondition == "mist":
         recs = getRecsMist(trackList, genreList, artistList, headers)
    elif weatherCondition == "snow":
         recs = getRecsSnow(winterTracks, winterGenres, artistList, headers)
    else: 
         recs = getRecsClear(trackList, genreList, artistList, headers)

    session['recs']=recs
    
    username=getUserName(headers)
    return render_template('redirect.html', name=username , weatherResponse=True, 
    cityName=result.get("name"), temp=math.floor(result.get("main").get("temp")), 
    description=result.get("weather")[0].get("description"), h=result.get("main").get("humidity"), 
    recsName = getTrackName(recs,headers), recsArtist = getTrackArtist(recs, headers), recList=recs, headers=headers)


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
    

@app.route("/makePlaylist")
def makePlaylist():
    headers = session.get("headers")
    songRecs = session.get("recs")
    r = requests.get(BASE_URL + 'me', headers=headers)
    r=r.json()
    userID= r['id']
    today = date.today()
    dateFormat = today.strftime("%m/%d")

    r = f"https://api.spotify.com/v1/users/{userID}/playlists"
    request_body = json.dumps({
           "name": "SpotiWeather for " + dateFormat,
           "description": "Weather based playlist for" + dateFormat,
           "public": False
         })
    response = requests.post(url = r, data = request_body, headers=headers)
    playlist_id = response.json()['id']
    songRecs = ["spotify:track:" + s for s in songRecs]
    songRecs=','.join(songRecs)
    url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris=" + songRecs

    response = requests.post(url = url, headers=headers)
    return render_template("final.html")


    

     

def getLikedSongs():

    #r= requests.get(BASE_URL + "me/tracks" , headers=headers)
    #r=r.json()
    return 'need to finish'
    #returns file containing (default 20) of the users liked songs

def userTopArtistSeeds(headers):
    artistList=[]
    limit = '10'
    timeRange ="long_term"
    r= requests.get(BASE_URL + "me/top/artists?limit=" +limit + "&time_range="+timeRange, headers=headers)
    r=r.json()
    for artists in r['items']:
         artistList.append(artists['id'])

    randomArtists= (random.choices(artistList, k=2))
    return ','.join(randomArtists)

def userTopGenreSeeds(headers):
    genres=[]
    limit = '10'
    timeRange ="medium_term"
    r= requests.get(BASE_URL + "me/top/artists?limit=" +limit + "&time_range="+timeRange, headers=headers)
    r=r.json()
    for artists in r['items']:
         genres.append((artists['genres']))
        
    flatlist=[element for sublist in genres for element in sublist]
    genreList = [*set(flatlist)]
    randomGenres= (random.choices(genreList, k=1))
    return ','.join(randomGenres)
    

def userTopTracksSeeds(headers):
    trackList=[]
    limit = '10'
    timeRange ="short_term"
    r= requests.get(BASE_URL + "me/top/tracks?limit=" +limit + "&time_range="+timeRange, headers=headers)
    r=r.json()
    for album in r['items']:
         trackList.append(album['id'])

    randomTracks= (random.choices(trackList, k=2))
    return ','.join(randomTracks)

#takes in the list of song ids and will return an array of their names
def getTrackName(recList, headers):
     recList = ','.join(recList)
     recNames=[]
     r= requests.get(BASE_URL + "tracks?ids=" + recList, headers=headers)
     r=r.json()
     for album in r['tracks']:
        recNames.append(album['name'])
     print(recNames)
     return recNames

def getTrackArtist(recList, headers):
        recList = ','.join(recList)
        recArtist=[]
        r= requests.get(BASE_URL + "tracks?ids=" + recList, headers=headers)
        r=r.json()
        for artists in r['tracks']:
            recArtist.append(artists['artists'][0]['name'])
        return recArtist

def getTrackDict(recs, headers):
    recsDict={}
    for i in range(0, len(getTrackName(recs, headers))):
        recsDict[getTrackName(recs, headers)[i]] = getTrackArtist(recs, headers)[i]
    return recsDict

     
#returns a string list of track ids for recs
def getRecsClear(trackLists, genreList, artistList, headers):
    print("clear weather")
    recList=[]
    limit ='20'
    r=requests.get(BASE_URL + "recommendations/?seed_tracks=" + trackLists + "&seed_artists=" + artistList + "&seed_genres=" + genreList + "&min_danceability=" + '0.6' + "&max_danceability=" + '0.8' + "&min_energy=" + '0.6' + "&min_tempo=" + '120' + "&min_valence=" + '0.6' + "&limit=" + limit, headers=headers)
    r=r.json()
    for album in r['tracks']:
        recList.append(album['id'])
    return recList
   

def getRecsRain(trackLists, genreList, artistList, headers):
    print('raining')
    recList=[]
    limit ='20'
    r=requests.get(BASE_URL + "recommendations/?seed_tracks=" + trackLists + "&seed_artists=" + artistList + "&seed_genres=" + genreList + "&min_acousticness=" + '0.7' + "&max_valence=" + '0.4' + "&limit=" + limit, headers=headers)
    r=r.json()
    for album in r['tracks']:
         recList.append(album['id'])
    return recList
     
def getRecsDrizzle(trackLists, genreList, artistList, headers):
    print("drizzling")
    #shower rain
    recList=[]
    limit ='20'
    r=requests.get(BASE_URL + "recommendations/?seed_tracks=" + trackLists + "&seed_artists=" + artistList + "&seed_genres=" + genreList + "&min_acousticness=" + '0.7' + "&max_acousticness=" + '0.8' + "&limit=" + limit, headers=headers)
    r=r.json()
    for album in r['tracks']:
         recList.append(album['id'])
    return recList

def getRecsThunder(trackLists, genreList, artistList, headers):
    print("thundering")
    recList=[]
    limit ='20'
    r=requests.get(BASE_URL + "recommendations/?seed_tracks=" + trackLists + "&seed_artists=" + artistList + "&seed_genres=" + genreList + "&min_danceability=" + '0.6' + "&min_energy=" + '0.7' + "&min_tempo=" + '130' + "&limit=" + limit, headers=headers)
    r=r.json()
    for album in r['tracks']:
         recList.append(album['id'])
    return recList
     
def getRecsSnow(winterTracks, winterGenres, artistList, headers):
    print("snowing")
    recList=[]
    limit ='20'
    r=requests.get(BASE_URL + "recommendations/?seed_tracks=" + winterTracks + "&seed_artists=" + artistList + "&seed_genres=" + winterGenres + "&limit=" + limit, headers=headers)
    r=r.json()
    for album in r['tracks']:
         recList.append(album['id'])
    return recList

def getRecsClouds(trackLists, genreList, artistList, headers):
    #grouped together few clouds, scattered clouds, broken clouds
    print("cloudy")
    recList=[]
    limit ='20'
    r=requests.get(BASE_URL + "recommendations/?seed_tracks=" + trackLists + "&seed_artists=" + artistList + "&seed_genres=" + genreList + "&min_danceability=" + '0.5' + "&max_danceability=" + '0.8' + "&min_energy=" + '0.6' + "&min_tempo=" + '100' + "&limit=" + limit, headers=headers)
    r=r.json()
    for album in r['tracks']:
         recList.append(album['id'])
    return recList
     

def getRecsMist(trackLists, genreList, artistList, headers):
    print("misty")
    recList=[]
    limit ='20'
    r=requests.get(BASE_URL + "recommendations/?seed_tracks=" + trackLists + "&seed_artists=" + artistList + "&seed_genres=" + genreList + "&min_acousticness=" + '0.7' + "&max_acousticness=" + '0.8' + "&min_danceability=" + '0.5' + "&max_danceability=" + '0.8' + "&limit=" + limit, headers=headers)
    r=r.json()
    for album in r['tracks']:
         recList.append(album['id'])
    return recList


if __name__ == "__main__":
    app.run(port=5000, debug=True)
   