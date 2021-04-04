from flask import Flask, request, redirect, make_response
from spotipy.oauth2 import SpotifyOAuth
import pickle
import pandas as pd
import numpy as np
import spotipy
from flask_cors import CORS, cross_origin
from spotipy import util
from sklearn import preprocessing

CLIENT_ID='2fc5e1e917ec463780f918e02b3175ee'
CLIENT_SECRET='7ec294bdd9514c2393367218461a612c'

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


auth = SpotifyOAuth(CLIENT_ID,
                    CLIENT_SECRET, 
                    redirect_uri ="http://termina-api-1.estaudere.repl.co/callback/q", 
                    scope="user-library-read user-read-recently-played")


def predict(songs_features):
  classifier = pickle.load(open("model.pkl", 'rb'))
  labels = classifier.predict(songs_features)
  (unique, counts) = np.unique(labels, return_counts=True)
  freq = {}
  for A, B in zip(unique, counts):
      freq[A] = B

  return max(freq, key=freq.get)

@app.route("/")
def show_status():
    cached_token = auth.get_cached_token()
    if (cached_token):
        return cached_token
    else:
        return "not logged in"


# Routes
@app.route("/auth")
def authenticate():

    url = auth.get_authorize_url()
    return redirect(url)
    #     if code:
    #         print("Found Spotify auth code in Request URL! Trying to get valid access token...")
    #         token_info = auth.get_access_token(code)
    #         access_token = token_info['access_token']

    # if access_token:
    #     print("Access token available! Trying to get user information...")
    #     sp = spotipy.Spotify(access_token)
    #     results = sp.current_user()
    #     return results

    # else:
    #     return f"logged in with token {access_token}"



    # At this point you can now create a Spotify instance with
    # sp = spotipy.client.Spotify(auth=token)

    # songs = sp.current_user_recently_played(limit=100)
    # return songs


@app.route("/callback/q")
def callback():
    code = auth.parse_response_code(request.url)
    token_query = auth.get_access_token(code=code, check_cache=False)
    
    access_token = token_query['access_token']
    refresh_token = token_query['refresh_token']
    
    # return access_token
    
    # token = auth.get_access_token(code)
    # Once the get_access_token function is called, a cache will be created making it possible to go through the route "/" without having to login anymore
    return redirect("https://cai.edwinrheindt.repl.co/analyze")

@app.route("/getsongs")
def get_songs():
  token_info = auth.get_cached_token()
  
  token = token_info['access_token']

  sp = spotipy.client.Spotify(auth=token)

  songs = sp.current_user_saved_tracks(limit=10)
  items = songs['items']
  collection = {'songs': []}

  for item in items:
    track_info = {}
    track_info['uri'] = item['track']['uri']
    track_info['name'] = item['track']['name']
    track_info['cover'] = item['track']['album']['images'][0]['url']
    collection['songs'].append(track_info)

  return collection



@app.route("/predict")
@cross_origin()
def run_model():



  token_info = auth.get_cached_token()
  
  token = token_info['access_token']

  sp = spotipy.client.Spotify(auth=token)

  songs = sp.current_user_saved_tracks(limit=20)

  items = songs['items']
  ids = []

  for item in items:
      ids.append(item['track']['id'])

  song_info = sp.audio_features(ids)

  def get_list(ls, ls_label):
    for song in song_info:
      ls.append(song[ls_label])


  # add features to a dictionary for easy dataframe conversion
  features_dict = {}
  danceability = []
  energy = []
  loudness = []
  speechiness = []
  acousticness = []
  liveness = []
  valence = []
  tempo = []
  instrumentalness = []

  get_list(danceability, "danceability")
  get_list(energy, "energy")
  get_list(loudness, "loudness")
  get_list(speechiness, "speechiness")
  get_list(acousticness, "acousticness")
  get_list(liveness, "liveness")
  get_list(valence, "valence")
  get_list(tempo, "tempo")
  get_list(instrumentalness, "instrumentalness")

  features_dict["danceability"] = danceability
  features_dict["energy"] = energy
  features_dict["loudness"] = loudness
  features_dict["speechiness"] = speechiness
  features_dict["acousticness"] = acousticness
  features_dict["liveness"] = liveness
  features_dict["valence"] = valence
  features_dict["tempo"] = tempo
  features_dict["instrumentalness"] = instrumentalness

  songs_features = pd.DataFrame.from_dict(features_dict)

  loudness_val = songs_features[['loudness']].values
  min_max_scaler = preprocessing.MinMaxScaler()
  loudness_scaled = min_max_scaler.fit_transform(loudness_val)
  songs_features['loudness'] = pd.DataFrame(loudness_scaled)

  tempo_val = songs_features[['tempo']].values
  min_max_scaler = preprocessing.MinMaxScaler()
  tempo_scaled = min_max_scaler.fit_transform(tempo_val)
  songs_features['tempo'] = pd.DataFrame(tempo_scaled)


  label = predict(songs_features)
  return {
    "STATUS": 202,
    "message": label
  }


if __name__ == '__main__':
    app.run(port=8080, host="0.0.0.0", debug=True)