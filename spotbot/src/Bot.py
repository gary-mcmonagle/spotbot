from src.services.Spotify import Spotify
from src.spotify.Track import Track
from src.Decorators import setInterval
import json
class Bot:
    def __init__(self, spotify):
        self.spotify:Spotify = spotify
        self.bot_playlist_id = self.__set_up_bot_playlist("SPOTBOT", "assets/bot.jpeg")
        self.bot_persis_playlist_id = self.__set_up_bot_playlist("PERSISTENT", "assets/bot-persis.jpg")
        self.playlist_playing = None
        self.provisional_track = None
        self.playing_track = None
        self.__fetch_playback_info()
   #initalise bot playlists
    def __set_up_bot_playlist(self, playlist_name, image_path):
        print("INFO: Validating playlist {} exists".format(playlist_name))
        playlist = self.spotify.get_playlist_by_name(playlist_name)
        if playlist is None:
            playlist_id = self.spotify.create_playlist(playlist_name, playlist_name)["id"]
            self.spotify.set_playlist_image(playlist_id, image_path)
        else:
            playlist_id = playlist['id']
        return playlist_id

    #add a track to vot playlists
    def queue_track(self, track_uri):
        print("INFO: Adding Track to bot play;ist")
        if not self.spotify.is_track_in_playlist(self.bot_playlist_id, track_uri):
            self.spotify.add_track_to_playlist(self.bot_playlist_id, track_uri)
            if not self.spotify.is_track_in_playlist(self.bot_persis_playlist_id, track_uri):
                self.spotify.add_track_to_playlist(self.bot_persis_playlist_id, track_uri)
            return "Added!"
        else:
            return "Track Already In Queue"

    #search spotify for track - KWARGS ?
    def search_track(self, track_name, artist_name, offset):
        print("INFO Searching for track n={} a={} o={}".format(track_name, artist_name, offset))
        found_tracks = self.spotify.search_for_track(track_name, artist_name, offset)
        if len(found_tracks) == 0:
            found_tracks = self.spotify.search_for_track(track_name, None, offset)
        if len(found_tracks) == 0:
            raise UnfoundTrack
        track_json = found_tracks[0]
        return Track(track_json["name"], track_json["artists"][0]["name"], track_json["album"]["name"],
                     track_json["uri"], track_json["album"]["images"][0]["url"])

    #update instance variables for playback state
    @setInterval(10)
    def __fetch_playback_info(self):
        print("INFO: fetching playback info")
        playback_state = self.spotify.get_current_playing()
        print("DEBUG: ps = {}".format(playback_state))
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

    #validate if correct playlist is playing
    def __check_is_bot_playlist(self, playback_state):
        print("INFO Validating Bot playlist is playing")
        if playback_state["context"]["type"] == "playlist":
            split = playback_state["context"]["uri"].split(":")
            if split[len(split)-1] == self.bot_playlist_id:
                return True
        return False

    #set the next track to be played if non in queue
    def __set_provisional_track(self):
        print("INFO: Setting Provisional Track")
        persis_playlist = self.spotify.get_playlist(self.bot_persis_playlist_id)
        if persis_playlist["tracks"]["total"] == 0:
            self.provisional_track = "spotify:track:2takcwOaAZWiXQijPHIx7B"
        else:
            offset = persis_playlist["tracks"]["total"] - 5
            if(offset < 0):
                offset = 0
            persis_tracks = self.spotify.get_playlist_tracks(self.bot_persis_playlist_id, offset)
            uris = []
            for idx, track in enumerate(persis_tracks["items"]):
                uri = track["track"]["uri"].split(":")
                uris.append(uri[len(uri) - 1])
            success = False
            limit = 0
            while not success:
                limit += 10
                recs = self.provisional_track = \
                    self.spotify.get_recommendations( uris, limit)["tracks"]#]["uri"]
                #improve here!!
                for idx, tr in enumerate(recs):
                    if not success:
                        if not self.spotify.is_track_in_playlist(self.bot_persis_playlist_id, recs[idx]["uri"]):
                            self.provisional_track = recs[idx]["uri"]
                            success = True
                            print("Using Track {}".format(idx))
    #surface information in state
    def get_info(self):
        print("INFO: Getting playback state")
        base = {
            "playlist_playing": self.playlist_playing
        }
        if self.playlist_playing:
            base["track_name"] =  self.playing_track.track_name
            base["track"] = self.playing_track.get()
        return json.dumps(base)


    def __add_provisional_track_to_playlist(self):
        print("INFO: Adding provisional Track to Bot playlist")
        if self.provisional_track is None:
            self.__set_provisional_track()
        self.spotify.add_track_to_playlist(self.bot_playlist_id, self.provisional_track)
        self.__set_provisional_track()


    def __maintain_playlist_state(self, playback_state):
        playlist = self.spotify.get_playlist(self.bot_playlist_id)
        tracks = playlist["tracks"]["items"]
        if playlist["tracks"]["total"] == 0:
            self.__add_provisional_track_to_playlist()
        if playlist["tracks"]["total"] == 1:
            if (playback_state["item"]["duration_ms"] - playback_state["progress_ms"]) <= 45000:
                self.__add_provisional_track_to_playlist()
        if tracks[0]["track"]["uri"] != self.playing_track.uri:
            self.spotify.remove_track_from_playlist(self.bot_playlist_id, tracks[0]["track"]["uri"])

class UnfoundTrack(Exception):
    pass