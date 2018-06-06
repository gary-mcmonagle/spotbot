from Auth_Manager import AuthManager
from Decorators import setInterval
from SpotApi import *
import logging
class Spotbot:
    def __init__(self, auth_token, client_id, client_secret, callback_uri):
        self.am = AuthManager(client_id, client_secret, callback_uri)
        tokens = self.am.get_access_and_refresh_token(auth_token)
        self.access_token = tokens[0]
        self.refresh_token = tokens[1]
        self.fetch_refresh_token()
        self.api_user_id = get_user_id(self.access_token)['id']
        self.set_up_bot_playlist()


    def set_up_bot_playlist(self):
        playlist_name = "Spot Bot Lad"
        if(get_playlist_by_name(self.access_token, playlist_name, self.api_user_id) == None):
            create_playlist(self.access_token, self.api_user_id, playlist_name, playlist_name)
        pl = get_playlist_by_name(self.access_token, playlist_name, self.api_user_id)
        clean_playlist(self.access_token, self.api_user_id, pl['id'])
        set_playlist_image(self.access_token, self.api_user_id, pl['id'], 'bot.jpeg')


    def get_current_playing_song(self):
        return get_current_playing(self.access_token)["item"]["name"]


    @setInterval(60)
    def fetch_refresh_token(self):
        print("refreshing token")
        self.access_token = self.am.refresh_token(self.refresh_token)
