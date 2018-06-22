from flask import Flask
import json
from Routes import Routes

with open('secrets.json') as f:
    secrets = json.load(f)
with open('config.json') as f:
    app_config = json.load(f)


application = Flask(__name__)
#routes = Routes(application, secrets['bot_url'], secrets['client_id'], secrets['client_secret'], secrets["skype_client_id"],
#                secrets["skype_client_secret"])

#could just pass in hash of all secrets and configs ??
routes = Routes(application, app_config)

if __name__ == "__main__":
    application.debug = app_config['debug']
    application.run()