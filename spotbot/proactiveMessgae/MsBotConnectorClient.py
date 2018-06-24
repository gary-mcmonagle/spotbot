import json
import requests
from Decorators import setInterval


class MsBotConnectorClient:
    def __init__(self, client_id, client_secret):
        self.__get_auth_token(client_id, client_secret)

    def send_message(self, message, **kwargs):
        conversation_id = kwargs.get("converation_id")
        service_url = kwargs.get("service_url")
        url = "{}v3/conversations/{}/activities".format(service_url, conversation_id)

        print(url)
        print(self.auth_token)
        r = requests.post(url=url,
                          data= message,
                          headers={
                              'Content-Type': 'application/json',
                              'Authorization': 'Bearer {}'.format(self.auth_token),
                               "charset":"utf-8"
                          },
                          )
        if (not r.ok):
            raise Exception("{}: {}".format(r.status_code, r.text))
        if r.text == "" or r.text == None:
            return None
        return json.loads(r.text)

    #@setInterval(15)
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
        self.auth_token =  json.loads(r.text)["access_token"]
        print("AT: {}".format(self.auth_token))
