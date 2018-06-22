import json
import urllib.parse
from Spotbot import UnfoundTrack
from proactiveMessgae.ProactiveMessage import ProactiveMessage
class RequestManager:
    def __init__(self, bot, config):
        self.bot = bot
        self.client_id = config["client_id"]
        self.callback_uri = config["bot_url"] + "/callback"
        try:
            self.bot_connector_client_id = config["bot_connector_client_id"]
            self.bot_connector_client_secret = config["bot_connector_client_secret"]
        except:
            self.bot_connector_client_id = None
            self.bot_connector_client_secret = None

    #retroactive set bot
    def set_bot(self, bot):
        self.bot = bot

    def analyse_request(self, request):
        js = json.loads(request)
        with open('data.json', 'w') as outfile:
            json.dump(js, outfile, indent=4, sort_keys=True)

        print(js)
        intent = js['queryResult']['intent']['displayName']
        if intent == 'admin.spotify.login':
            data = self.__admin_login()
        elif intent == "session_init":
            data = self.__session_init()
        elif intent == "queue-request":
            data = self.__queue_request(js)
        elif intent == "proative-message":
            data = self.__get_skype_token()
        else:
            data = {'fulfillmentText': "Intent not understood"}

        return data

    def __admin_login(self):
        scope = "user-top-read user-read-recently-played user-library-modify user-library-read playlist-modify-public "
        scope += "playlist-modify-private playlist-read-collaborative playlist-read-private user-read-private "
        scope += "user-read-email user-read-birthdate user-follow-modify user-follow-read "
        scope += "user-read-currently-playing user-read-playback-state user-modify-playback-state ugc-image-upload"
        uri = 'https://accounts.spotify.com/authorize'
        uri += '?response_type=code'
        uri += '&client_id=' + self.client_id
        uri += '&scope=' + urllib.parse.quote(scope)
        uri += '&redirect_uri=' + urllib.parse.quote(self.callback_uri)
        return json.dumps({'fulfillmentText': uri})
    def __get_playing_song(bot):
        if(bot == None):
            return json.dumps({'fulfillmentText': "Please Login"})
        else:
            return json.dumps({'fulfillmentText': bot.get_current_playing_song()})

    def __session_init(self):
        if bot == None:
            return self.__admin_login()
        else:
            return json.dumps({'fulfillmentText': "Please Login"})

    def __queue_request(self, request_json):
        try:
            self.bot.queue_request(request_json["queryResult"]["parameters"]["track-title"],
                                     request_json["queryResult"]["parameters"]["artist-name"])
            data = {'fulfillmentText': "Song added!"}
        except UnfoundTrack:
            data = {'fulfillmentText': "Sorry could'nt find that song"}

        return json.dumps(data)

    def __get_skype_token(self):
        pam = ProactiveMessage("skype", None, skype_client_secret=self.bot_connector_client_id,
                               skype_client_id=self.bot_connector_client_secret)
        return json.dumps({'fulfillmentText': "Look at console"})



#def