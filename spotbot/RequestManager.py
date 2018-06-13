import json
import urllib.parse
def analyse_request(request, bot, client_id, callback_uri):
    js = json.loads(request)
    intent = js['queryResult']['intent']['displayName']
    if(intent == 'spotify-login-request'):
        message = __get_login(client_id, callback_uri)

    data = {
        'fulfillmentText': message
    }
    return data

def __get_login(client_id, callback_uri):
    scope = "user-top-read user-read-recently-played user-library-modify user-library-read playlist-modify-public "
    scope += "playlist-modify-private playlist-read-collaborative playlist-read-private user-read-private "
    scope += "user-read-email user-read-birthdate user-follow-modify user-follow-read "
    scope += "user-read-currently-playing user-read-playback-state user-modify-playback-state ugc-image-upload"
    uri = 'https://accounts.spotify.com/authorize'
    uri += '?response_type=code'
    uri += '&client_id=' + client_id
    uri += '&scope=' + urllib.parse.quote(scope)
    uri += '&redirect_uri=' + urllib.parse.quote(callback_uri)
    return uri