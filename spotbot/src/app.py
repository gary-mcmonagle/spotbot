from flask import Flask
import json
from src.Routes import Routes
import logging
from applicationinsights.flask.ext import AppInsights

logging.basicConfig(filename='myapp.log', level=logging.INFO)

config_path = 'src/config.json'

if __name__ == "__main__":
    config_path = 'config.json'

with open(config_path) as f:
    app_config = json.load(f)


application = Flask(__name__)
try:
    application.config['APPINSIGHTS_INSTRUMENTATIONKEY'] = app_config["app_insights_ins_key"]
    AppInsights(application)
except:
    pass


routes = Routes(application, app_config)


if __name__ == "__main__":
    application.debug = app_config['debug']
    application.run(host='0.0.0.0', port=5000)