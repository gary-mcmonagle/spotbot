from Auth_Manager import AuthManager
from Decorators import setInterval
import requests
import logging
import spotipy
class Spotbot:
    def __init__(self, auth_token, client_id, client_secret, callback_uri):
        self.am = AuthManager(client_id, client_secret, callback_uri)
        tokens = self.am.get_access_and_refresh_token(auth_token)
        self.access_token = tokens[0]
        self.refresh_token = tokens[1]
        self.spotipy_client = spotipy.Spotify(self.access_token)
        self.bot_id = self.spotipy_client.current_user()['id']
        self.fetch_refresh_token()

    def next_song(self):
        r = requests.post('https://api.spotify.com/v1/me/player/next', data={
        },headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        print("text: {}".format(r.text))
        print("content:{}".format(r.content))

    @setInterval(60)
    def fetch_refresh_token(self):
        print("refreshing token for {}".format(self.bot_id))
        logging.info("refreshing token for {}".format(self.bot_id))
        self.access_token = self.am.refresh_token(self.refresh_token)
        self.spotipy_client = spotipy.Spotify(self.access_token)#