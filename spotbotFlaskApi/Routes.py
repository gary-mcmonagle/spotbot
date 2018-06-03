from Auth_Manager import AuthManager
from flask import request
from Spotbot import Spotbot

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
            return AuthManager.get_authorization_url(self.callback_uri, self.client_id)
        @self.app.route('/callback')
        def callback():
            self.bots.add_spotbot(Spotbot(request.args.get('code'), self.client_id, self.client_secret, self.callback_uri))
            return "Success"
        @self.app.route('/countBots')
        def countBots():
            return str(self.bots.count_bots())
        @self.app.route('/next')
        def get_info():
            self.bots.bots[0].next_song()
            return "Skipping"