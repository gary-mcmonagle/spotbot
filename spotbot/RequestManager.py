import json
import urllib.parse
def analyse_request(request, bot, client_id, callback_uri):
    js = json.loads(request)
    print(js)
    intent = js['queryResult']['intent']['displayName']
    if intent == 'admin.spotify.login':
        data = __admin_login(client_id, callback_uri)
    elif intent == "session_init":
        data = __session_init(bot, client_id, callback_uri)
    elif intent == "queue-request":
        data = __queue_request(bot, js)
    else:
        data = {'fulfillmentText': "Intent not understood"}

    return data

def __admin_login(client_id, callback_uri):
    scope = "user-top-read user-read-recently-played user-library-modify user-library-read playlist-modify-public "
    scope += "playlist-modify-private playlist-read-collaborative playlist-read-private user-read-private "
    scope += "user-read-email user-read-birthdate user-follow-modify user-follow-read "
    scope += "user-read-currently-playing user-read-playback-state user-modify-playback-state ugc-image-upload"
    uri = 'https://accounts.spotify.com/authorize'
    uri += '?response_type=code'
    uri += '&client_id=' + client_id
    uri += '&scope=' + urllib.parse.quote(scope)
    uri += '&redirect_uri=' + urllib.parse.quote(callback_uri)
    return {'fulfillmentText': uri}

def __get_playing_song(bot):
    if(bot == None):
        return {'fulfillmentText': "Please Login"}
    else:
        return {'fulfillmentText': bot.get_current_playing_song()}

def __session_init(bot, client_id, callback_uri):
    if bot == None:
        return __admin_login(client_id, callback_uri)
    else:
        return {'fulfillmentText': "Please Login"}

def __queue_request(bot, request_json):
    bot.queue_request(request_json["queryResult"]["parameters"]["track-title"],
                             request_json["queryResult"]["parameters"]["artist-name"])
    return {'fulfillmentText': "Blah"}


#def