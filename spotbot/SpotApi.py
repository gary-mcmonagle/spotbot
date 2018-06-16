import json
import requests
import base64

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
    return json.loads(r.text)

def get_access_and_refresh_token(client_id, client_secret, auth_token, callback_uri):
    encoded = base64.b64encode("{}:{}".format(client_id, client_secret).encode()).decode()
    return __make_api_call(url="https://accounts.spotify.com/api/token",
                                    header={'Content-Type': 'application/x-www-form-urlencoded',
                                            "Authorization": "Basic {}".format(encoded)},
                                    body={
                                        'grant_type': 'authorization_code',
                                        'code': auth_token,
                                        'redirect_uri':callback_uri
                                    },
                                    method="POST"
                                    )



def refresh_token(client_id, client_secret, refresh_token):
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
    with open(image_path, "rb") as image_file:
        image_64_encode = base64.b64encode(image_file.read()).decode()
    print("https://api.spotify.com/v1/users/{}/playlists/{}/images".format(user_id, playlist_id))
    header = {'Authorization': 'Bearer {}'.format(access_token),
              "Content-Type": "image/jpeg"}
    __make_api_call(url="https://api.spotify.com/v1/users/{}/playlists/{}/images".format(user_id, playlist_id),
                    method="PUT",
                    body=image_64_encode,
                    header=header)
    print(access_token)


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

def search_for_song(access_token, track_name, artist):
    q = "artist:{} {}".format(artist, track_name)
    print(q)
    call = __make_api_call(url="https://api.spotify.com/v1/search",
                    params={"q": q,
                            "type":"track",
                            #Hardoded IE fix later (maybe)
                            "market": "IE"},
                    header={'Authorization': 'Bearer {}'.format(access_token),
                            "Content-Type": "application/json",
                            "Accept":"application/json"},
                    method="GET"
                    )
    print(call)


def add_song_to_playlist(access_token, user_id, playlist_id, track_uri):
    __make_api_call(url="https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(user_id, playlist_id),
                    method="POST",
                    header={'Authorization': 'Bearer {}'.format(access_token), "Content-Type": "application/json"},
                    body=json.dumps({
                        "uris": [track_uri]
                    }))


