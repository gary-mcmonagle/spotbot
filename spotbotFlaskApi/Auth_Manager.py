import requests
import urllib.parse
import webbrowser
class AuthManager:

    def __init__(self, client_id, client_secret, callback_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_uri = callback_uri

    def get_access_and_refresh_token(self, auth_token):
        r = requests.post('https://accounts.spotify.com/api/token', data={
            'grant_type': 'authorization_code',
            'code': auth_token,
            'redirect_uri': self.callback_uri
        },headers={'Content-Type': 'application/x-www-form-urlencoded'}, auth=(self.client_id, self.client_secret))
        return [r.json()['access_token'], r.json()['refresh_token']]

    def refresh_token(self, refresh_token):
        r = requests.post('https://accounts.spotify.com/api/token', data={
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        },headers={'Content-Type': 'application/x-www-form-urlencoded'}, auth=(self.client_id, self.client_secret))
        return r.json()['access_token']

    @staticmethod
    def get_authorization_url(callback_url, client_id):
        scope = "user-top-read user-read-recently-played user-library-modify user-library-read playlist-modify-public "
        scope += "playlist-modify-private playlist-read-collaborative playlist-read-private user-read-private "
        scope += "user-read-email user-read-birthdate user-follow-modify user-follow-read "
        scope += "user-read-currently-playing user-read-playback-state user-modify-playback-state ugc-image-upload"
        uri = 'https://accounts.spotify.com/authorize'
        uri += '?response_type=code'
        uri += '&client_id=' + client_id
        uri += '&scope=' + urllib.parse.quote(scope)
        uri += '&redirect_uri=' + urllib.parse.quote(callback_url)
        webbrowser.open(uri, new=2)
        return uri