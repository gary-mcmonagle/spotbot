from flask import request,Response,send_from_directory,render_template
from functools import wraps
import logging
import json
from src.RequestManager import RequestManager
from flask_cors import CORS, cross_origin
from src.services.Spotify import Spotify
from src.Bot import Bot

class Routes:
    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.create_routes()
        self.bot = None
        self.request_manager = RequestManager(self.bot, config)
        print("Routes Created!")

    def create_routes(self):
        @self.app.route('/hello', methods=["GET"])
        @self.requires_auth
        def hello():
            return "Hi"

        @self.app.route('/get_info')
        @cross_origin()
        def get_info():
            if self.bot is None:
                return json.dumps({
                    "message": "Bot Not Initialised"
                })
            else:
                return self.bot.get_info()

        @self.app.route('/live')
        def admin():
            return render_template("index.html")

        @self.app.route('/callback', methods=["GET"])
        def callback():
            # self.bot = Spotbot(request.args.get('code'), self.config["client_id"], self.config["client_secret"],
            #                    self.config["bot_url"]+"/callback", self.config['playback_refresh_poll'])
            spotify = Spotify(self.config["client_id"], self.config["client_secret"],
                              self.config["bot_url"]+"/callback", request.args.get('code'))
            self.bot = Bot(spotify)
            self.request_manager.set_bot(self.bot)
            self.request_manager.login_recieved(request.args.get("state"))
            return send_from_directory(".","callback.html")
        @self.app.route('/webhook', methods=["POST"])
        @self.requires_auth
        def webhook():
            js = self.request_manager.analyse_request(request.data.decode('utf-8'))
            resp = Response(js, status=200, mimetype='application/json')
            return resp

    def requires_auth(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            if not auth or not (self.config["df_user"] == auth.username and self.config["df_pass"] == auth.password):
                return Response(
                    'Could not verify your access level for that URL.\n'
                    'You have to login with proper credentials', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'}
                )
            return f(*args, **kwargs)
        return decorated