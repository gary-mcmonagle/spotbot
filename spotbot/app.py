from flask import Flask
import json
from Routes import Routes

with open('secrets.json') as f:
    secrets = json.load(f)
with open('config.json') as f:
    app_config = json.load(f)


application = Flask(__name__)
routes = Routes(application, secrets['callback_uri'], secrets['client_id'], secrets['client_secret'])

if __name__ == "__main__":
    application.debug = app_config['debug']
    application.run()