from flask import Flask
import json
from Routes import Routes
import logging

logging.basicConfig(filename='myapp.log', level=logging.INFO)

with open('secrets.json') as f:
    secrets = json.load(f)
with open('config.json') as f:
    app_config = json.load(f)


application = Flask(__name__)
routes = Routes(application, app_config)

if __name__ == "__main__":
    application.debug = app_config['debug']
    application.run()