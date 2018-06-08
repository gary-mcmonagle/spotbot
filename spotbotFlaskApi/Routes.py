from flask import request

class Routes:
    def __init__(self, app, bots, callback_uri, client_id, client_secret):
        self.app = app
        self.bots = bots
        self.callback_uri = callback_uri
        self.client_id = client_id
        self.client_secret = client_secret
        self.create_routes()

    def create_routes(self):
        @self.app.route('/login')
        def login():
            return self.bots.get_authorization_url()
        @self.app.route('/callback')
        def callback():
            return self.bots.add_spotbot(request.args.get('code'))
        @self.app.route('/countBots')
        def countBots():
            return str(self.bots.count_bots())
        @self.app.route('/next')
        def get_info():
            self.bots.bots[0].next_song()
            return "Skipping"
        @self.app.route('/getplaying')
        def get_playing():
            return self.bots.bots[0].get_current_playing_song()
        @self.app.route('/addtrack')
        def addsong():
            self.bots.bots[0].add_song(request.args.get('trackuri'))