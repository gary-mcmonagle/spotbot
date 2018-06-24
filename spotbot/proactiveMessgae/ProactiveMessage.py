from proactiveMessgae.MsBotConnectorClient import MsBotConnectorClient
class ProactiveMessage:
    def __init__(self, config):
        try:
            self.ms_connector_client = MsBotConnectorClient(config["ms_bot_connector_client_id"],
                                                            config["ms_bot_connector_client_secret"])
        except:
            print("no config found for ms bot")

    def __get_client(self, client_type):
        if(client_type == "ms_bot_connector"):
            return self.ms_connector_client

    def send_message(self, client_type, message_object):
        client = self.__get_client(client_type)
        client = self.__get_client(client_type)
        client.send_message(message_object)
