import json
import urllib.parse
from Spotbot import UnfoundTrack
from proactiveMessgae.ProactiveMessage import ProactiveMessage
from MessageGenerator import generate_message
import jwt
import Constant

class RequestManager:
    def __init__(self, bot, config):
        self.bot = bot
        self.client_id = config["client_id"]
        self.callback_uri = config["bot_url"] + "/callback"
        self.jwt_key = config["jwt_key"]
        self.pam = ProactiveMessage(config)

    #retroactive set bot
    def set_bot(self, bot):
        self.bot = bot

    def analyse_request(self, request):
        js = json.loads(request)
        intent = js['queryResult']['intent']['displayName']
        if intent == 'admin.spotify.login':
            data = self.__admin_login(request)
        elif self.bot is None:
            data = generate_message(text="No Spotify account connected")
        elif intent == "queue-request" or intent == "queue-request-try-again":
            data = self.__track_search(js, intent)
        elif intent == "queue-request-success":
            data = self.__queue_track(js)
        else:
            data = generate_message(text="Cant find intent {}".format(intent))

        return data

    def login_recieved(self, jwt_token):
        print("JWT: {}".format(jwt_token))
        decoded = jwt.decode(jwt_token, self.jwt_key, algorithms='HS256')
        base_message = self.__format_by_type(decoded)
        base_message["text"] = "Logged In Successfully!"
        self.pam.send_message(base_message["type"], generate_message(**base_message), **base_message)


    def __admin_login(self, request):
        state_token = jwt.encode(json.loads(request), self.jwt_key, algorithm='HS256').decode()
        scope = "user-top-read user-read-recently-played user-library-modify user-library-read playlist-modify-public "
        scope += "playlist-modify-private playlist-read-collaborative playlist-read-private user-read-private "
        scope += "user-read-email user-read-birthdate user-follow-modify user-follow-read "
        scope += "user-read-currently-playing user-read-playback-state user-modify-playback-state ugc-image-upload"
        uri = 'https://accounts.spotify.com/authorize'
        uri += '?response_type=code'
        uri += '&client_id=' + self.client_id
        uri += '&scope=' + urllib.parse.quote(scope)
        uri += '&redirect_uri=' + urllib.parse.quote(self.callback_uri)
        uri += "&state=" + state_token
        return generate_message(text=uri)

    def __get_playing_song(bot):
        if bot is None:
            return json.dumps({'fulfillmentText': "Please Login"})
        else:
            return json.dumps({'fulfillmentText': bot.get_current_playing_song()})

    def __track_search(self, request_json,intent):
        if intent == "queue-request":
            track_name = request_json["queryResult"]["parameters"]["track-title"]
            artist_name = request_json["queryResult"]["parameters"]["artist-name"]
            offset = 0
        else:
            track_name = request_json["queryResult"]["outputContexts"][0]["parameters"]["track-title"]
            artist_name = request_json["queryResult"]["outputContexts"][0]["parameters"]["artist-name"]
            offset = int(request_json["queryResult"]["outputContexts"][0]["parameters"]["offset"])

        print(json.dumps(request_json))
        try:
            track = self.bot.search_track(track_name, artist_name, offset)
            buttons = [{
                "title": "Yes",
                "value": "Yes"
            }]
            buttons.append({
                "title": "Try Again",
                "value": "Try Again"
            })
            buttons.append({
                "title": "Cancel",
                "value": "Cancel"
            })
            data = generate_message(card_title=track.track_name,
                                    card_image_url=track.image_url,
                                    card_buttons=buttons,
                                    output_contexts=
                                    [
                                        {
                                            "name":"queue-request-followup",
                                            "parameters":{
                                                "track-uri": track.uri,
                                                "offset": offset+1
                                            }
                                        }
                                    ])
        except UnfoundTrack:
            data = generate_message(text="Sorry Couldnt find that song :(")
        print(data)
        return data

    def __format_by_type(self, request_info):
        bot_type = self.__determine_type(request_info)
        base_message = {}
        if bot_type == Constant.BOT_CONNECTOR_MESSAGE:
            base_message = {
                "bot_id": request_info["originalDetectIntentRequest"]["payload"]["data"]["address"]["bot"]["id"],
                "conversation_id": urllib.parse.quote(request_info["originalDetectIntentRequest"]["payload"]["data"]["address"]["conversation"]["id"]),
                "bot_name": request_info["originalDetectIntentRequest"]["payload"]["data"]["address"]["bot"]["name"],
                "service_url": request_info["originalDetectIntentRequest"]["payload"]["data"]["address"]["serviceUrl"]
            }
        base_message["type"] = bot_type
        return base_message

    def __queue_track(self, request_info):
        return generate_message(text=self.bot.queue_track(request_info["queryResult"]["outputContexts"][0]["parameters"]["track-uri"]))

    def __determine_type(self, request_info):
        print("Source: {}".format(request_info["originalDetectIntentRequest"]["source"]))
        if request_info["originalDetectIntentRequest"]["source"] == "skype":
            return Constant.BOT_CONNECTOR_MESSAGE
