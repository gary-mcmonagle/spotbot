from flask import Flask
import json
import logging
from Routes import Routes
from Bots import Bots

with open('secrets.json') as f:
    secrets = json.load(f)
with open('config.json') as f:
    app_config = json.load(f)

logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('app.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
if (app_config['debug']):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

bots = Bots()
application = Flask(__name__)
routes = Routes(application, bots, secrets['callback_uri'], secrets['client_id'], secrets['client_secret'])

if __name__ == "__main__":
    application.debug = app_config['debug']
    logger.info("INFO: Starting app")
    application.run()