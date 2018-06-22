from flask import request,Response,send_from_directory
import json
from Spotbot import Spotbot
from RequestManager import RequestManager

class Routes:
    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.create_routes()
        self.bot = None
        self.request_manager = RequestManager(self.bot, config)

    def create_routes(self):
        @self.app.route('/callback', methods=["GET"])
        def callback():
            self.bot = Spotbot(request.args.get('code'), self.config["client_id"], self.config["client_secret"],
                               self.config["bot_url"]+"/callback")
            self.request_manager.set_bot(self.bot)
            return send_from_directory(".","callback.html")
        @self.app.route('/webhook', methods=["POST"])
        def webhook():
            js = self.request_manager.analyse_request(request.data.decode('utf-8'))
            print(js)
            resp = Response(js, status=200, mimetype='application/json')
            return resp