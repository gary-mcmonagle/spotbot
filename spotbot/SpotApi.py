import json
import requests
import base64
import logging
import urllib.parse

def __make_api_call(**kwargs):

    url = kwargs.get('url')
    method = kwargs.get('method')
    header = kwargs.get('header')
    body = kwargs.get('body')
    params = kwargs.get('params')

    if method == "GET":
        r = requests.get(url=url, headers=header, params=params)
    if method == "POST":
        r = requests.post(url=url, data=body, headers=header)
    if method == "PUT":
        r = requests.put(url=url, data=body, headers=header)
    if method == "DELETE":
        r = requests.delete(url=url, data=body, headers=header)

    if(not r.ok):
        raise Exception("{}: {}".format(r.status_code, r.text))
    if r.text == "" or r.text == None:
        return None
    with open('data.json', 'w') as f:
        f.write(r.text)
    return json.loads(r.text)

def get_access_and_refresh_token(client_id, client_secret, auth_token, callback_uri):
    logging.info("Requesting Auth Token")
    encoded = base64.b64encode("{}:{}".format(client_id, client_secret).encode()).decode()
    return __make_api_call(url="https://accounts.spotify.com/api/token",
                                    header={'Content-Type': 'application/x-www-form-urlencoded',
                                            "Authorization": "Basic {}".format(encoded)},
                                    body={
                                        'grant_type': 'authorization_code',
                                        'code': auth_token,
                                        'redirect_uri': callback_uri
                                    },
                                    method="POST"
                                    )



def refresh_token(client_id, client_secret, refresh_token):
    logging.info("Getting RefreshToken")
    encoded = base64.b64encode("{}:{}".format(client_id, client_secret).encode()).decode()
    return __make_api_call(url="https://accounts.spotify.com/api/token",
                           header={'Content-Type': 'application/x-www-form-urlencoded',
                                   "Authorization": "Basic {}".format(encoded)},
                           body={
                                'grant_type': 'refresh_token',
                                'refresh_token': refresh_token
                           },
                           method="POST"
                           )['access_token']


def get_user_id(access_token):
    auth_header = {'Authorization': 'Bearer {}'.format(access_token)}
    return __make_api_call(url="https://api.spotify.com/v1/me",
                           method="GET",
                           header=auth_header)['id']

def get_current_playing(access_token):
    auth_header = {'Authorization': 'Bearer {}'.format(access_token)}
    return __make_api_call(url="https://api.spotify.com/v1/me/player",
                            method="GET",
                            header=auth_header)

def create_playlist(access_token, user_id, playlist_name, desc):
    header = {'Authorization': 'Bearer {}'.format(access_token), "Content-Type": "application/json"}
    body = {"name": playlist_name,
            "public": False,
            "description": desc
            }
    return __make_api_call(url="https://api.spotify.com/v1/users/{}/playlists".format(user_id),
                           method="POST",
                           header=header,
                           body=json.dumps(body))

def set_playlist_image(access_token, user_id, playlist_id, image_path):
    logging.info("Setting PLaylist Image")
    with open(image_path, "rb") as image_file:
        image_64_encode = base64.b64encode(image_file.read()).decode()
    header = {'Authorization': 'Bearer {}'.format(access_token),
              "Content-Type": "image/jpeg"}
    __make_api_call(url="https://api.spotify.com/v1/users/{}/playlists/{}/images".format(user_id, playlist_id),
                    method="PUT",
                    body=image_64_encode,
                    header=header)


def clean_playlist(access_token, user_id, playlist_id):
    has_tracks = True
    while(has_tracks):
        tracks = __make_api_call(
            url="https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(user_id, playlist_id),
            header={'Authorization': 'Bearer {}'.format(access_token)},
            method="GET"
        )
        if len(tracks["items"]) == 0:
            has_tracks = False
        else:
            tracks_to_delete = []
            for track in enumerate(tracks["items"]):
                tracks_to_delete.append({"uri":track[1]["track"]["uri"]})
            __make_api_call(
                url="https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(user_id, playlist_id),
                method="DELETE",
                header={'Authorization': 'Bearer {}'.format(access_token), "Content-Type": "application/json"},
                body=json.dumps({"tracks": tracks_to_delete})
            )
#could use kwargs here ?
def get_playlist(access_token, playlist_id, user_id):
    return __make_api_call(
        url="https://api.spotify.com/v1/users/{}/playlists/{}".format(user_id, playlist_id),
        method="GET",
        header={'Authorization': 'Bearer {}'.format(access_token), "Content-Type": "application/json"}

    )


def get_playlist_by_name(access_token, playlist_name, user_id):
    allchecked = False
    url = "https://api.spotify.com/v1/me/playlists"
    while(not allchecked):
        request = __make_api_call(url=url,
                                  header={'Authorization': 'Bearer {}'.format(access_token)},
                                  method="GET",
                                  )
        for idx, playlist in enumerate(request["items"]):
            if(playlist["name"] == playlist_name):
                return __make_api_call(url="https://api.spotify.com/v1/users/{}/playlists/{}".format(user_id, playlist['id']),
                                       method="GET",
                                       header={'Authorization': 'Bearer {}'.format(access_token)})
        if request["next"] == None:
            allchecked = True
        else:
            url = request["next"]
    return None

def search_for_track(access_token, track_name, artist, offset):
    print(offset)
    if artist is not None:
        q = "artist:{} {}".format(artist, track_name)
    else:
        q = track_name
    return __make_api_call(url="https://api.spotify.com/v1/search",
                    params={"q": q,
                            "type":"track",
                            #Hardoded IE fix later (maybe)
                            "market": "IE",
                            "limit":1,
                            "offset": offset
                            },
                    header={'Authorization': 'Bearer {}'.format(access_token),
                            "Content-Type": "application/json",
                            "Accept":"application/json"},
                    method="GET"
                    )["tracks"]["items"]


def add_song_to_playlist(access_token, user_id, playlist_id, track_uri):
    __make_api_call(url="https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(user_id, playlist_id),
                    method="POST",
                    header={'Authorization': 'Bearer {}'.format(access_token), "Content-Type": "application/json"},
                    body=json.dumps({
                        "uris": [track_uri]
                    }))

def remove_track_from_playlist(access_token, user_id, playlist_id, track_uri):
    body = {
        "tracks": [
            {
                "uri": track_uri
            }
        ]
    }
    __make_api_call(url="https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(user_id, playlist_id),
                    method="DELETE",
                    header={'Authorization': 'Bearer {}'.format(access_token), "Content-Type": "application/json"},
                    body=json.dumps(body)
                    )


def is_track_in_playlist(access_token, user_id, playlist_id, track_uri):
    all_got = False
    current_max = 100
    while not all_got:
        tracks =__make_api_call(url="https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(user_id, playlist_id),
                        method="GET",
                        header={'Authorization': 'Bearer {}'.format(access_token), "Content-Type": "application/json"})
        print("URIS")
        for track in enumerate(tracks["items"]):
            if track[1]["track"]["uri"] == track_uri:
                return True
        if(tracks["total"] <= current_max):
            all_got = True
        else:
            current_max += 100
    return False

def get_recommendations(access_token, tracks):
    track_string = ""
    for idx, track in enumerate(tracks):
        track_string += track
        if idx != len(tracks)-1:
            track_string += ","
    print("TS = {}".format( urllib.parse.quote(track_string)))
    return __make_api_call(url="https://api.spotify.com/v1/recommendations",
                           method="GET",
                           header={'Authorization': 'Bearer {}'.format(access_token),
                                   "Content-Type": "application/json"
                                   },
                           params={
                               "limit": 1,
                               "seed_tracks": track_string
                           }
                           )




