import json
import urllib.parse
from Spotbot import UnfoundTrack
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
    elif intent == "rich-message-test":
        data = __rich_message()
        print(data)
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
    return json.dumps({'fulfillmentText': uri})

def __get_playing_song(bot):
    if(bot == None):
        return json.dumps({'fulfillmentText': "Please Login"})
    else:
        return json.dumps({'fulfillmentText': bot.get_current_playing_song()})

def __session_init(bot, client_id, callback_uri):
    if bot == None:
        return __admin_login(client_id, callback_uri)
    else:
        return json.dumps({'fulfillmentText': "Please Login"})

def __queue_request(bot, request_json):
    try:
        bot.queue_request(request_json["queryResult"]["parameters"]["track-title"],
                                 request_json["queryResult"]["parameters"]["artist-name"])
        data = {'fulfillmentText': "Song added!"}
    except UnfoundTrack:
        data = {'fulfillmentText': "Sorry could'nt find that song"}

    return json.dumps(data)

def __rich_message():
    return json.dumps(
        {
            "fulfillmentText": "This is a text response",
            "fulfillmentMessages": [
                {
                    "card": {
                        "title": "card title",
                        "subtitle": "card text",
                        "imageUri": "https://assistant.google.com/static/images/molecule/Molecule-Formation-stop.png",
                        "buttons": [
                            {
                                "text": "button text",
                                "postback": "https://assistant.google.com/"
                            }
                        ]
                    }
                }
            ]
        })


#def