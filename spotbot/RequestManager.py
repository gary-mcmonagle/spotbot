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
        elif intent == "session_init":
            data = self.__session_init()
        elif intent == "queue-request":
            data = self.__track_search(js)
        elif intent == "proative-message":
            data = self.__get_skype_token()
        elif intent == "queue-request-success":
            data = self.__queue_song(js)
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

    #def __track_search(self, request_json):


    def __track_search(self, request_json):
        try:
            track = self.bot.search_track(request_json["queryResult"]["parameters"]["track-title"],
                                     request_json["queryResult"]["parameters"]["artist-name"], 0)
            buttons = [{
                "title": "Yes",
                "value": "Yes"
            }]
            if track.search_index != track.total_search_results:
                buttons.append({
                    "title": "Try Again",
                    "value": "Try Again"
                })
            buttons.append({
                "title": "Cancel",
                "value": "Cancel"
            })
            data = generate_message(card_title=track.track_name,
                                    card_image_url=track.image_url[0],
                                    card_buttons=buttons,
                                    output_contexts=
                                    [
                                        {
                                            "name":"queue-request-followup",
                                            "parameters":{
                                                "track-uri": track.uri,
                                                "page": track.search_index
                                            }
                                        }
                                    ])
        except UnfoundTrack:
            data = generate_message(text="Sorry Couldnt find that song :(")
        print(data)
        return data

    def __get_skype_token(self):
        pam = ProactiveMessage("skype", None, skype_client_secret=self.bot_connector_client_id,
                               skype_client_id=self.bot_connector_client_secret)
        return json.dumps({'fulfillmentText': "Look at console"})

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

    def __queue_song(self, request_info):
        self.bot.queue_track(request_info["queryResult"]["outputContexts"][0]["parameters"]["track-uri"])
        return generate_message(text="adding")

    def __determine_type(self, request_info):
        print("Source: {}".format(request_info["originalDetectIntentRequest"]["source"]))
        if request_info["originalDetectIntentRequest"]["source"] == "skype":
            return Constant.BOT_CONNECTOR_MESSAGE
