from Decorators import setInterval
from SpotApi import *
from spotify.Track import Track

class Spotbot:
    def __init__(self, auth_token , client_id, client_secret, callback_uri, playback_refresh_poll):
        tokens = get_access_and_refresh_token(client_id, client_secret, auth_token, callback_uri)
        self.access_token = tokens['access_token']
        self.refresh_token = tokens['refresh_token']
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback_uri = callback_uri
        self.playback_refresh_poll = playback_refresh_poll
        self.api_user_id = get_user_id(self.access_token)
        self.bot_playlist_id = self.__set_up_bot_playlist("spot-bot", "assets/bot.jpeg")
        self.bot_persis_playlist_id = self.__set_up_bot_playlist("spot-bot-persis", "assets/bot-persis.jpg")
        self.__fetch_playback_info()
        self.__fetch_refresh_token()
        self.provisional_track = None


    def __set_up_bot_playlist(self, playlist_name, image_path):
        playlist = get_playlist_by_name(self.access_token, playlist_name, self.api_user_id)
        if playlist is None:
            playlist_id = create_playlist(self.access_token, self.api_user_id, playlist_name, playlist_name)["id"]
            set_playlist_image(self.access_token, self.api_user_id, playlist_id, image_path)
        else:
            playlist_id = playlist['id']
        return playlist_id

    def get_current_playing_song(self):
        song = get_current_playing(self.access_token)
        return "{} - {}".format(song["item"]["artists"][0]["name"], song["item"]["name"])

    def queue_track(self, track_uri):
        if not is_track_in_playlist(self.access_token, self.api_user_id, self.bot_playlist_id, track_uri):
            add_song_to_playlist(self.access_token, self.api_user_id, self.bot_playlist_id, track_uri)
            return "Added!"
        else:
            return "Track Already In Queue"

    def search_track(self, track_name, artist_name, offset):
            found_tracks = search_for_track(self.access_token, track_name, artist_name, offset)
            if len(found_tracks) == 0:
                found_tracks = search_for_track(self.access_token, track_name, None, offset)
            if len(found_tracks) == 0:
                raise UnfoundTrack
            track_json = found_tracks[0]
            return Track(track_json["name"], track_json["artists"][0]["name"], track_json["album"]["name"],
                         track_json["uri"], track_json["album"]["images"][0]["url"])


    @setInterval(30)
    def __fetch_refresh_token(self):
        print("refreshing token")
        self.access_token = refresh_token(self.client_id, self.client_secret, self.refresh_token)

    @setInterval(10)
    def __fetch_playback_info(self):
        print("fetching playback info")
        playback_state = get_current_playing(self.access_token)
        #is_playing = True
        try:
            is_playing = playback_state["is_playing"]
        except:
            is_playing = False
        if is_playing:
            self.playing_track = Track(
                playback_state["item"]["name"],
                playback_state["item"]["artists"][0]["name"],
                playback_state["item"]["album"]["name"],
                playback_state["item"]["uri"],
                playback_state["item"]["album"]["images"][0]["url"]
            )
            self.playlist_playing = self.__check_is_bot_playlist(playback_state)
            if self.playlist_playing:
                self.__maintain_playlist_state(playback_state)
        else:
            print("Spotify not playing")
            self.playing_track = None
            self.playlist_playing = False

    def __check_is_bot_playlist(self, playback_state):
        if playback_state["context"]["type"] == "playlist":
            split = playback_state["context"]["uri"].split(":")
            if split[len(split)-1] == self.bot_playlist_id:
                return True
        return False

    def __add_provisional_track_to_playlist(self):
        print("Adding Provisional Track")
        persis_playlist = get_playlist(self.access_token, self.bot_persis_playlist_id, self.api_user_id)
        tracks = persis_playlist["tracks"]["items"]
        if persis_playlist["tracks"]["total"] == 0:
            add_song_to_playlist(self.access_token, self.api_user_id, self.bot_playlist_id,
                                 "spotify:track:2takcwOaAZWiXQijPHIx7B")
        else:
            uris = []
            for idx, track in enumerate(tracks):
                uri = track["track"]["uri"].split(":")
                uris.append(uri[len(uri)-1])
            add_song_to_playlist(self.access_token, self.api_user_id, self.bot_playlist_id, get_recommendations(self.access_token, uris)["tracks"][0]["uri"])


    def __maintain_playlist_state(self, playback_state):
        playlist = get_playlist(self.access_token, self.bot_playlist_id, self.api_user_id)
        tracks = playlist["tracks"]["items"]
        if playlist["tracks"]["total"] == 0:
            self.__add_provisional_track_to_playlist()
        if playlist["tracks"]["total"] == 1:
            if (playback_state["item"]["duration_ms"] - playback_state["progress_ms"]) <= 45000:
                self.__add_provisional_track_to_playlist()
        if tracks[0]["track"]["uri"] != self.playing_track.uri:
            self.__recycle_playlist_track(tracks[0]["track"]["uri"])

    def __recycle_playlist_track(self, track_uri):
        remove_track_from_playlist(self.access_token, self.api_user_id, self.bot_playlist_id, track_uri)
        add_song_to_playlist(self.access_token, self.api_user_id, self.bot_persis_playlist_id, track_uri)



class UnfoundTrack(Exception):
    pass
