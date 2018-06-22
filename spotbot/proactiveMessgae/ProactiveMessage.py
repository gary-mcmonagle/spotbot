from proactiveMessgae.SkypeClient import SkypeClient
class ProactiveMessage:
    def __init__(self, client_type, message_data, **kwargs):
        if(client_type == "skype"):
            self.client = SkypeClient(message_data, kwargs.get('skype_client_id'), kwargs.get('skype_client_secret'))