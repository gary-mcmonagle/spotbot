class Track:
    def __init__(self, track_name, artist, album, uri, image_url):
        self.track_name = track_name
        self.artist = artist
        self.album = album
        self.uri = uri
        self.image_url = image_url

    def get(self):
        return {
            "title":self.track_name,
            "artist":self.artist,
            "album":self.album,
            "uri":self.uri,
            "image_url":self.image_url
        }