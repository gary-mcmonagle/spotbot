import json
import requests
import time

endpoints = {
    "current_playing":["get", "https://api.spotify.com/v1/me/player"],
    "pause": ["put", "https://api.spotify.com/v1/me/player/pause"]
}

def invoke_spotify_api(func, access_token):
    endpoint = endpoints[func]
    auth_header = {'Authorization': 'Bearer {}'.format(access_token)}
    r = None
    if endpoint[0] == "get":
        r = requests.get(endpoint[1], headers=auth_header, timeout=120.0)
    if endpoint[0] == "put":
        r = requests.put(endpoint[1], headers=auth_header)
    if r.status_code != 200:
        return None
    else:
        return json.loads(r.text)