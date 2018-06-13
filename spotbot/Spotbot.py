from Decorators import setInterval
from SpotApi import *

class Spotbot:
    def __init__(self, auth_token , client_id, client_secret, callback_uri):
        tokens = get_access_and_refresh_token(client_id, client_secret, auth_token, callback_uri)
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_uri = callback_uri
        self.api_user_id = get_user_id(self.access_token)
        self.__set_up_bot_playlist()


    def __set_up_bot_playlist(self):
        playlist_name = "Spot Bot"
        if(get_playlist_by_name(self.access_token, playlist_name, self.api_user_id) == None):
            create_playlist(self.access_token, self.api_user_id, playlist_name, playlist_name)
        self.bot_playlist_id = get_playlist_by_name(self.access_token, playlist_name, self.api_user_id)['id']
        clean_playlist(self.access_token, self.api_user_id, self.bot_playlist_id)
        set_playlist_image(self.access_token, self.api_user_id, self.bot_playlist_id, 'bot.jpeg')


    def get_current_playing_song(self):
        song = get_current_playing(self.access_token)
        return "{} - {}".format(song["item"]["artists"][0]["name"], song["item"]["name"])

    def add_song(self, track_uri):
        add_song_to_playlist(self.access_token, self.api_user_id, self.bot_playlist_id, track_uri)


    @setInterval(60)
    def fetch_refresh_token(self):
        print("refreshing token")
        self.access_token = refresh_token(self.client_id, self.client_secret, self.refresh_token)