import urllib.parse
import webbrowser

from SpotApi import *
from Spotbot import Spotbot

class Bots:
    def __init__(self, client_id, client_secret, callback_uri):
        self.bots = []
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_uri = callback_uri

    def get_authorization_url(self):
        scope = "user-top-read user-read-recently-played user-library-modify user-library-read playlist-modify-public "
        scope += "playlist-modify-private playlist-read-collaborative playlist-read-private user-read-private "
        scope += "user-read-email user-read-birthdate user-follow-modify user-follow-read "
        scope += "user-read-currently-playing user-read-playback-state user-modify-playback-state ugc-image-upload"
        uri = 'https://accounts.spotify.com/authorize'
        uri += '?response_type=code'
        uri += '&client_id=' + self.client_id
        uri += '&scope=' + urllib.parse.quote(scope)
        uri += '&redirect_uri=' + urllib.parse.quote(self.callback_uri)
        webbrowser.open(uri, new=2)
        return uri


    def add_spotbot(self, access_token):
        tokens = get_access_and_refresh_token(self.client_id, self.client_secret, access_token, self.callback_uri)
        user_id = get_user_id(tokens['access_token'])
        self.bots.append(Spotbot(tokens['access_token'],
                                     tokens['refresh_token'],
                                    self.client_id,
                                   self.client_secret,
                                   self.callback_uri))
        return user_id

    def get_spotbot(self, user_id):
        return self.bots[user_id]


