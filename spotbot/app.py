from flask import Flask
import json
from Routes import Routes
import logging
from applicationinsights.flask.ext import AppInsights

logging.basicConfig(filename='myapp.log', level=logging.INFO)

with open('config.json') as f:
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
    application.run()