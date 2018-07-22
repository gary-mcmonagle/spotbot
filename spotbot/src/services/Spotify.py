from src.services.ApiRequest import make_api_call
from src.Decorators import setInterval
import src.services.Constants as Constants
import base64
import json
import urllib.parse

class Spotify:
    def __init__(self, client_id, client_secret, callback_uri, auth_token):
        print("INFO:  START -> Instantiating Spotify")
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_uri = callback_uri
        tokens = self.get_access_and_refresh_token(auth_token)
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens["refresh_token"]
        self.user_id = self.get_user_id()
        print("INFO:  END -> Instantiating Spotify")

    #get tokens used to access based on token returned from callback
    def get_access_and_refresh_token(self, auth_token):
        print("INFO: Getting access and refresh tokens")
        encoded = base64.b64encode("{}:{}".format(self.client_id, self.client_secret).encode()).decode()
        return make_api_call(url="https://accounts.spotify.com/api/token",
                               header={'Content-Type': 'application/x-www-form-urlencoded',
                                       "Authorization": "Basic {}".format(encoded)},
                               body={
                                   'grant_type': 'authorization_code',
                                   'code': auth_token,
                                   'redirect_uri': self.callback_uri
                               },
                               method=Constants.POST
                               )

    #use refresh token to update access token
    @setInterval(150)
    def refresh_token(self):
        print("INFO: Refreshing access token")
        encoded = base64.b64encode("{}:{}".format(self.client_id, self.client_secret).encode()).decode()
        self.access_token =  make_api_call(url="https://accounts.spotify.com/api/token",
                               header={'Content-Type': 'application/x-www-form-urlencoded',
                                       "Authorization": "Basic {}".format(encoded)},
                               body={
                                   'grant_type': 'refresh_token',
                                   'refresh_token': self.refresh_token
                               },
                               method=Constants.POST
                               )['access_token']

    #fetch user id
    def get_user_id(self):
        print("INFO: Getting user id")
        auth_header = {'Authorization': 'Bearer {}'.format(self.access_token)}
        return make_api_call(url="https://api.spotify.com/v1/me",
                               method=Constants.GET,
                               header=auth_header)['id']

    #me/player
    def get_current_playing(self):
        auth_header = {'Authorization': 'Bearer {}'.format(self.access_token)}
        return make_api_call(url="https://api.spotify.com/v1/me/player",
                                method=Constants.GET,
                                header=auth_header)

    #create a private playlist
    def create_playlist(self, playlist_name, desc):
        print("INFO: Creating Playlist {}".format(playlist_name))
        header = {'Authorization': 'Bearer {}'.format(self.access_token), "Content-Type": "application/json"}
        body = {"name": playlist_name,
                "public": False,
                "description": desc
                }
        return make_api_call(url="https://api.spotify.com/v1/users/{}/playlists".format(self.user_id),
                               method=Constants.POST,
                               header=header,
                               body=json.dumps(body))

    #set image of playlist from local file (checked in)
    def set_playlist_image(self, playlist_id, image_path):
        print("INFO: Setting Image for {}".format(playlist_id))
        with open(image_path, "rb") as image_file:
            image_64_encode = base64.b64encode(image_file.read()).decode()
        header = {'Authorization': 'Bearer {}'.format(self.access_token),
                  "Content-Type": "image/jpeg"}
        make_api_call(url="https://api.spotify.com/v1/users/{}/playlists/{}/images".format(self.user_id, playlist_id),
                        method=Constants.PUT,
                        body=image_64_encode,
                        header=header)

    #return json for playlist - REFACTOR KWARGS
    def get_playlist(self, playlist_id):
        print("INFO: Getting playlist {}".format(playlist_id))
        return make_api_call(
            url="https://api.spotify.com/v1/users/{}/playlists/{}".format(self.user_id, playlist_id),
            method="GET",
            header={'Authorization': 'Bearer {}'.format(self.access_token), "Content-Type": "application/json"}
        )

    #return json for playlist - Refactor KWARGS
    def get_playlist_by_name(self, playlist_name):
        print("INFO Searching for playlist {}".format(playlist_name))
        allchecked = False
        url = "https://api.spotify.com/v1/me/playlists"
        while(not allchecked):
            request = make_api_call(url=url,
                                      header={'Authorization': 'Bearer {}'.format(self.access_token)},
                                      method=Constants.GET,
                                      )
            for idx, playlist in enumerate(request["items"]):
                if(playlist["name"] == playlist_name):
                    return make_api_call(url="https://api.spotify.com/v1/users/{}/playlists/{}".format(self.user_id, playlist['id']),
                                           method=Constants.GET,
                                           header={'Authorization': 'Bearer {}'.format(self.access_token)})
            if request["next"] == None:
                allchecked = True
            else:
                url = request["next"]
        return None

    #search for track - returns JSON Should return Track ?
    def search_for_track(self, track_name, artist, offset):
        print("INFO: Searching for track n={} a={} o={}".format(track_name, artist, offset))
        if artist is not None:
            q = "artist:{} {}".format(artist, track_name)
        else:
            q = track_name
        return make_api_call(url="https://api.spotify.com/v1/search",
                        params={"q": q,
                                "type":"track",
                                #Hardoded IE fix later (maybe)
                                "market": "IE",
                                "limit":1,
                                "offset": offset
                                },
                        header={'Authorization': 'Bearer {}'.format(self.access_token),
                                "Content-Type": "application/json",
                                "Accept":"application/json"},
                        method=Constants.GET
                        )["tracks"]["items"]

    #add track to playlist based on track uri. Could be by Track?
    def add_track_to_playlist(self, playlist_id, track_uri):
        print("INFO adding track {} to playlist {}".format(track_uri, playlist_id))
        make_api_call(url="https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(self.user_id, playlist_id),
                        method=Constants.POST,
                        header={'Authorization': 'Bearer {}'.format(self.access_token), "Content-Type": "application/json"},
                        body=json.dumps({
                            "uris": [track_uri]
                    }))

    #remove track based on URI, Could be by Track?
    def remove_track_from_playlist(self, playlist_id, track_uri):
        print("INFO: Removing track {} from playlist {}".format(track_uri, playlist_id))
        body = {
            "tracks": [
                {
                    "uri": track_uri
                }
            ]
        }
        make_api_call(url="https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(self.user_id, playlist_id),
                        method=Constants.DELETE,
                        header={'Authorization': 'Bearer {}'.format(self.access_token), "Content-Type": "application/json"},
                        body=json.dumps(body)
                        )

    #true/false is track in playlist
    def is_track_in_playlist(self, playlist_id, track_uri):
        print("INFO: Checking is Track {} in Playlist {}".format(track_uri, playlist_id))
        all_got = False
        current_max = 100
        while not all_got:
            tracks = make_api_call(
                            url="https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(self.user_id, playlist_id),
                            method=Constants.GET,
                            header={'Authorization': 'Bearer {}'.format(self.access_token), "Content-Type": "application/json"})
            for track in enumerate(tracks["items"]):
                if track[1]["track"]["uri"] == track_uri:
                    return True
            if(tracks["total"] <= current_max):
                all_got = True
            else:
                current_max += 100
        return False

    #return list of tracks
    def get_playlist_tracks(self, playlist_id, offset):
        print("INFO: Getting Tracks for {}".format(playlist_id))
        return make_api_call(url="https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(self.user_id, playlist_id),
                               method=Constants.GET,
                               header={'Authorization': 'Bearer {}'.format(self.access_token), "Content-Type": "application/json"},
                               params={"offset": offset})

    #return reccomentions based on passed in tracks
    def get_recommendations(self, tracks, limit):
        print("INFO: Getting recommendations based on {}".format(tracks))
        track_string = ""
        for idx, track in enumerate(tracks):
            track_string += track
            if idx != len(tracks)-1:
                track_string += ","
        print("TS = {}".format(urllib.parse.quote(track_string)))
        return make_api_call(url="https://api.spotify.com/v1/recommendations",
                               method=Constants.GET,
                               header={'Authorization': 'Bearer {}'.format(self.access_token),
                                       "Content-Type": "application/json"
                                       },
                               params={
                                   "limit": limit ,
                                   "seed_tracks": track_string,
                                   "market": "IE"
                               }
                               )
