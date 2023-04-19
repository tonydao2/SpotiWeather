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


#Log in
@app.route("/login")
def SpotifyLogin():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

#logs out
@app.route("/logout")
def SpotifyLogout():
      session.clear()
      if os.path.exists(".cache"):
            os.remove(".cache")
      return render_template('home.html', message="You have been logged out.")


#creates spotify oauth object
def create_spotify_oauth():
    return SpotifyOAuth(
            client_id=secrets["client_id"],
            client_secret=secrets["client_secret"],
        redirect_uri="http://127.0.0.1:5000/redirect/",
         scope=["user-read-private", "user-read-email", 'playlist-modify-public', 
                'playlist-modify-private', 'playlist-read-private', 'user-library-modify', 
                'user-library-read', 'user-top-read'])

#API call to get the curent weather at name which is the name of the suers current location
def weatherSearch(name):
    URL = "https://api.openweathermap.org/data/2.5/weather?q="+name+"&APPID=" + weatherApi+"&units=imperial"
    response = requests.get(URL)
    return response.json()

#API call to get users current location
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

    #call apis to get users location and the weather at the location and store results in session variables
    cityName = getLocation()
    result = weatherSearch(cityName)
    weatherCondition = result.get("weather")[0].get("description")

    session['weather']=weatherCondition
    session['result'] = result

    #if access token did not work, redirect back to main page to log in again
    try: 
        token_info=get_access_token()
    except:
         #user not logged in
         return redirect("/")
    
    #header to be passed to spotify api requests
    headers = {'Authorization': 'Bearer {token}'.format(token=token_info['access_token'])}
    session['headers']=headers

    #generate the users top artists, genres, and tracks 
    trackList = userTopTracksSeeds(headers)
    genreList =userTopGenreSeeds(headers)
    artistList = userTopArtistSeeds(headers)

    #get winter recommendations
    winterTracks = ','.join(random.choices(["0bYg9bo50gSsH3LtXe2SQn", "0lizgQ7Qw35od7CYaoMBZb", "2uFaJJtFpPDc5Pa95XzTvg", "7uoFMmxln0GPXQ0AcCBXRq", "2L9QLAhrvtP4EYg1lY0Tnw", "5PuKlCjfEVIXl0ZBp5ZW9g", "65irrLqfCMRiO3p87P4C0D", "5Q2P43CJra0uRAogjHyJDK", "0qcr5FMsEO85NAQjrlDRKo", "1jhljxXlHw8K9rezXKrnow", "2QjOHCTQ1Jl3zawyYOpxh6"], k=2))
    winterGenres = "Christmas"

    #lists of weather conditions
    clearList = ['clear', 'clear sky']
    rainList = ['rain', 'light rain', 'moderate rain', 'very heavy rain', 'extreme rain', 'freezing rain', 'light intensity shower rain', 'shower rain', 'heavy intensity shower rain', 'ragged shower rain']
    drizzleList = ['light intensity drizzle', 'drizzle', 'heavy intensity drizzle', 'light intensity drizzle rain', 'drizzle rain', 'heavy intensity drizzle rain', 'shower rain and drizzle', 'heavy shower rain and drizzle', 'shower drizzle']
    thunderList = ['thunderstorm with light rain', 'thunderstorm with heavy rain', 'thunderstorm with rain', 'thunderstorm', 'light thunderstorm', 'heavy thunderstorm', 'ragged thunderstorm', 'thunderstorm with light drizzle', 'thunderstorm with heavy drizzle',  'thunderstorm with drizzle']
    cloudList = ['few clouds', 'scattered clouds' , 'broken clouds', 'overcast clouds']
    atmosphereList = ['mist', 'smoke', 'haze', 'sand whirls', 'dust whirls', 'dust', 'sand', 'volcanic ash', 'fog', 'squalls', 'tornado']
    snowList = ['light snow', 'snow', 'heavy snow', 'sleet', 'light shower sleet', 'shower sleet', 'light rain and snow', 'rain and snow', 'light shower snow', 'shower snow', 'heavy shower snow']
    
    print(trackList)
    print(genreList)
    print(artistList)
    print(weatherCondition)

    #compare weather conditions to what is in list to know which rec function to call
    if weatherCondition in clearList:
        recs = getRecsClear(trackList, genreList, artistList, headers)
    elif weatherCondition in rainList:
         recs = getRecsRain(trackList, genreList, artistList, headers)
    elif weatherCondition in drizzleList:
         recs = getRecsDrizzle(trackList, genreList, artistList, headers)
    elif weatherCondition in thunderList:
         recs = getRecsThunder(trackList, genreList, artistList, headers)
    elif weatherCondition in cloudList:
         recs = getRecsClouds(trackList, genreList, artistList, headers)
    elif weatherCondition in atmosphereList:
         recs = getRecsMist(trackList, genreList, artistList, headers)
    elif weatherCondition in snowList:
         recs = getRecsSnow(winterTracks, winterGenres, artistList, headers)
    else: 
         recs = getRecsClear(trackList, genreList, artistList, headers)

    #store the rec info into session variables 
    session['recs']=recs
    recsName = getTrackName(recs,headers)
    session['recsName']=recsName
    recsArtist = getTrackArtist(recs, headers)
    session['recsArtist']=recsArtist

    username=getUserName(headers)
    session['username']=username

    return render_template('redirect.html', name=username , weatherResponse=True, 
    cityName=result.get("name"), temp=math.floor(result.get("main").get("temp")), 
    description=result.get("weather")[0].get("description"), h=result.get("main").get("humidity"), recsName = recsName, recsArtist = recsArtist, 
    recList=recs, headers=headers)


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
    #get all of the session variables needed
    username = session.get("username")
    recsName = session.get("recsName")
    recsArtist = session.get("recsArtist")
    result = session.get("result")
    headers = session.get("headers")
    weather=session.get("weather")
    songRecs = session.get("recs")

    r = requests.get(BASE_URL + 'me', headers=headers)
    r=r.json()
    userID= r['id']

    today = date.today()
    dateFormat = today.strftime("%m/%d")

    #API Call to make playlist for user
    r = f"https://api.spotify.com/v1/users/{userID}/playlists"
    request_body = json.dumps({
           "name": "SpotiWeather for " + dateFormat,
           "description": "Weather based playlist for " + dateFormat,
           "public": False
         })
    response = requests.post(url = r, data = request_body, headers=headers)
    playlist_id = response.json()['id']

    #need to add spotify:track: to all of the song ids
    songRecs = ["spotify:track:" + s for s in songRecs]
    songRecs=','.join(songRecs)

    #API call to add songs to playlist we had just created
    url=f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris=" + songRecs
    response = requests.post(url = url, headers=headers)

    return render_template('redirect.html', weatherResponse=True, 
    cityName=result.get("name"), temp=math.floor(result.get("main").get("temp")), name=username,
    description=result.get("weather")[0].get("description"), h=result.get("main").get("humidity"), recsName = recsName, recsArtist = recsArtist,
    recList=songRecs, headers=headers, message='Playlist Created!')

#gets 10 of the users short term artists to make sure that the artists are ones that the user is actively listening to
#out of the 10, chooses 2 at random to increase variety
def userTopArtistSeeds(headers):
    artistList=[]
    limit = '10'
    timeRange ="short_term"

    #API call to get users top artists
    r= requests.get(BASE_URL + "me/top/artists?limit=" +limit + "&time_range="+timeRange, headers=headers)
    r=r.json()
    for artists in r['items']:
         artistList.append(artists['id'])

    randomArtists= (random.choices(artistList, k=2))
    return ','.join(randomArtists)

#gets 10 of the users top medium term artists and compiles a list of all of their genres 
# (artists may have more than one genre) without duplicates and chooses one genre at random 
def userTopGenreSeeds(headers):
    genres=[]
    limit = '10'
    timeRange ="medium_term"

    #API call to get users medium term artists
    r= requests.get(BASE_URL + "me/top/artists?limit=" +limit + "&time_range="+timeRange, headers=headers)
    r=r.json()
    for artists in r['items']:
         genres.append((artists['genres']))
        
    flatlist=[element for sublist in genres for element in sublist]
    genreList = [*set(flatlist)]
    randomGenres= (random.choices(genreList, k=1))
    return ','.join(randomGenres)
    
#gets 10 of the users short term tracks  to make sure that the songs are ones that the user is actively listening to
#out of the 10, chooses 2 at random to increase variety
def userTopTracksSeeds(headers):
    trackList=[]
    limit = '10'
    timeRange ="short_term"

    #API call to get users top tracks
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
     return recNames

#takes in a list of the song ids and will get the artists for each song
def getTrackArtist(recList, headers):
        recList = ','.join(recList)
        recArtist=[]
        r= requests.get(BASE_URL + "tracks?ids=" + recList, headers=headers)
        r=r.json()
        for artists in r['tracks']:
            recArtist.append(artists['artists'][0]['name'])
        return recArtist

#makes a dictionary of the song name and artists
def getTrackDict(recs, headers):
    recsDict={}
    for i in range(0, len(getTrackName(recs, headers))):
        recsDict[getTrackName(recs, headers)[i]] = getTrackArtist(recs, headers)[i]
    return recsDict

     
#returns a string list of track ids for recs for a clear day by passing in the top tracks chosen, top artists chosen, and genre chosen
def getRecsClear(trackLists, genreList, artistList, headers):
    print("clear weather")
    recList=[]
    limit ='20'
    r=requests.get(BASE_URL + "recommendations/?seed_tracks=" + trackLists + "&seed_artists=" + artistList + "&seed_genres=" + genreList + "&min_danceability=" + '0.6' + "&max_danceability=" + '0.8' + "&min_energy=" + '0.6' + "&min_tempo=" + '120' + "&min_valence=" + '0.6' + "&limit=" + limit, headers=headers)
    r=r.json()
    for album in r['tracks']:
        recList.append(album['id'])
    return recList
   
#returns a string list of track ids for recs for a rainy day by passing in the top tracks chosen, top artists chosen, and genre chosen
def getRecsRain(trackLists, genreList, artistList, headers):
    print('raining')
    recList=[]
    limit ='20'
    r=requests.get(BASE_URL + "recommendations/?seed_tracks=" + trackLists + "&seed_artists=" + artistList + "&seed_genres=" + genreList + "&min_acousticness=" + '0.7' + "&max_valence=" + '0.4' + "&limit=" + limit, headers=headers)
    r=r.json()
    for album in r['tracks']:
         recList.append(album['id'])
    return recList
     
#returns a string list of track ids for recs for when drizzling conditions by passing in the top tracks chosen, top artists chosen, and genre chosen
def getRecsDrizzle(trackLists, genreList, artistList, headers):
    print("drizzling")
    recList=[]
    limit ='20'
    r=requests.get(BASE_URL + "recommendations/?seed_tracks=" + trackLists + "&seed_artists=" + artistList + "&seed_genres=" + genreList + "&min_acousticness=" + '0.7' + "&max_acousticness=" + '0.8' + "&limit=" + limit, headers=headers)
    r=r.json()
    for album in r['tracks']:
         recList.append(album['id'])
    return recList

#returns a string list of track ids for recs for when thundering by passing in the top tracks chosen, top artists chosen, and genre chosen
def getRecsThunder(trackLists, genreList, artistList, headers):
    print("thundering")
    recList=[]
    limit ='20'
    r=requests.get(BASE_URL + "recommendations/?seed_tracks=" + trackLists + "&seed_artists=" + artistList + "&seed_genres=" + genreList + "&min_danceability=" + '0.6' + "&min_energy=" + '0.7' + "&min_tempo=" + '130' + "&limit=" + limit, headers=headers)
    r=r.json()
    for album in r['tracks']:
         recList.append(album['id'])
    return recList
     
#returns a string list of track ids for recs for a snowy day by passing in winterTracks, top artists chosen, and winter genre
def getRecsSnow(winterTracks, winterGenres, artistList, headers):
    print("snowing")
    recList=[]
    limit ='20'
    r=requests.get(BASE_URL + "recommendations/?seed_tracks=" + winterTracks + "&seed_artists=" + artistList + "&seed_genres=" + winterGenres + "&limit=" + limit, headers=headers)
    r=r.json()
    for album in r['tracks']:
         recList.append(album['id'])
    return recList

#returns a string list of track ids for recs for a cloudy day by passing in the top tracks chosen, top artists chosen, and genre chosen
def getRecsClouds(trackLists, genreList, artistList, headers):
    print("cloudy")
    recList=[]
    limit ='20'
    r=requests.get(BASE_URL + "recommendations/?seed_tracks=" + trackLists + "&seed_artists=" + artistList + "&seed_genres=" + genreList + "&min_danceability=" + '0.5' + "&max_danceability=" + '0.8' + "&min_energy=" + '0.6' + "&min_tempo=" + '100' + "&limit=" + limit, headers=headers)
    r=r.json()
    for album in r['tracks']:
         recList.append(album['id'])
    return recList
     
#returns a string list of track ids for recs for a misty day by passing in the top tracks chosen, top artists chosen, and genre chosen
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
   