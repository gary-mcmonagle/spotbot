import json
import requests
import jwt

class SkypeClient:
    def __init__(self, message_data, client_id, client_secret):
        self.auth_token =self.__get_auth_token(client_id, client_secret)

    def __get_auth_token(self, client_id, client_secret):
        print("Fetching Skype Token")
        r = requests.post(url="https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token",
                          data={
                              "grant_type": "client_credentials",
                              "client_id": client_id,
                              "client_secret": client_secret,
                              "scope":"https://api.botframework.com/.default"
                          },
                          headers={
                              "Content-Type": "application/x-www-form-urlencoded",
                              "Host": "login.microsoftonline.com"
                          })
        if (not r.ok):
            raise Exception("{}: {}".format(r.status_code, r.text))
        if r.text == "" or r.text == None:
            return None
        self.__validate_access_token(json.loads(r.text)["access_token"], client_id)
        #print(json.loads(r.text))
        return json.loads(r.text)


    def __validate_access_token(self, token, client_id):
        token_key = jwt.get_unverified_header(token)['kid']
        print(token_key)
        r = requests.get("https://login.botframework.com/v1/.well-known/openidconfiguration")
        if (not r.ok):
            raise Exception("{}: {}".format(r.status_code, r.text))
        r = requests.get(json.loads(r.text)["jwks_uri"])
        if (not r.ok):
            raise Exception("{}: {}".format(r.status_code, r.text))
        keys = json.loads(r.text)["keys"]
        print(keys)
