from flask import Flask
import json
with open('secrets.json') as f:
    secrets = json.load(f)
with open('config.json') as f:
    app_config = json.load(f)

application = Flask(__name__)

if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    if(app_config['debug']):
        application.debug = True
    application.run()