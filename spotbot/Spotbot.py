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
        self.admin_session = None


    def __set_up_bot_playlist(self):
        playlist_name = "Spot Bot"
        if(get_playlist_by_name(self.access_token, playlist_name, self.api_user_id) == None):
            create_playlist(self.access_token, self.api_user_id, playlist_name, playlist_name)
            set_playlist_image(self.access_token, self.api_user_id, self.bot_playlist_id, 'bot.jpeg')
        self.bot_playlist_id = get_playlist_by_name(self.access_token, playlist_name, self.api_user_id)['id']
        #clean_playlist(self.access_token, self.api_user_id, self.bot_playlist_id)


    def get_current_playing_song(self):
        song = get_current_playing(self.access_token)
        return "{} - {}".format(song["item"]["artists"][0]["name"], song["item"]["name"])

    def queue_request(self, track_name, artist_name):
        found_tracks = search_for_song(self.access_token, track_name, artist_name)
        if len(found_tracks) == 0:
            raise UnfoundTrack
        else:
            add_song_to_playlist(self.access_token, self.api_user_id, self.bot_playlist_id, found_tracks[0]["uri"])
        print("Song Requested - {}-{}".format(artist_name, track_name))


    @setInterval(60)
    def fetch_refresh_token(self):
        print("refreshing token")
        self.access_token = refresh_token(self.client_id, self.client_secret, self.refresh_token)

class UnfoundTrack(Exception):
    pass
