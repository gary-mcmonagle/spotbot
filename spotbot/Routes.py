from flask import request,Response,send_from_directory
import json
from Spotbot import Spotbot
from RequestManager import analyse_request

class Routes:
    def __init__(self, app, callback_uri, client_id, client_secret):
        self.app = app
        self.callback_uri = callback_uri
        self.client_id = client_id
        self.client_secret = client_secret
        self.create_routes()
        self.bot = None

    def create_routes(self):
        @self.app.route('/callback', methods=["GET"])
        def callback():
            self.bot = Spotbot(request.args.get('code'), self.client_id, self.client_secret, self.callback_uri)
            return send_from_directory(".","callback.html")
        @self.app.route('/webhook', methods=["POST"])
        def webhook():
            js = json.dumps(analyse_request(request.data.decode('utf-8'), self.bot, self.client_id, self.callback_uri))
            resp = Response(js, status=200, mimetype='application/json')
            return resp