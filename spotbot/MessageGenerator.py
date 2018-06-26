import Constant
import json
def generate_message(**kwargs):
    message = {}
    type = kwargs.get('type')
    buttons = kwargs.get('buttons')
    text = kwargs.get('text')
    type = __set_message_type(type)
    message = __message_base_set_up(message, type, kwargs)
    if text is not None:
        message = __get_text(message, text, type)
    if buttons is not None:
        message = __set_card(message,type, kwargs)
    print("Message: {}".format(message))
    return json.dumps(message)

def __set_message_type(type):
    if(type is None):
        return Constant.DIALOGFLOW_MESSAGE
    else:
        return type

def __message_base_set_up(message, type , kwargs):
    if type == Constant.BOT_CONNECTOR_MESSAGE:
        message["type"] = "message"
        message["from"] = {
            "id": kwargs.get("bot_id"),
            "name": kwargs.get("bot_name")
        }
    print("Message: {}".format(message))
    return message

def __get_text(message, text, type):
    if type == Constant.DIALOGFLOW_MESSAGE:
        message['fulfillmentText'] = text
    if type == Constant.BOT_CONNECTOR_MESSAGE:
        message["text"] = text
    return message

def __set_card_text(message, type,kwargs):
    if(type == Constant.BOT_CONNECTOR_MESSAGE):
        message["title"] = kwargs.get("card_title")
        message["subtitle"] = kwargs.get("card_subtitle")
        message["text"] = kwargs.get("card_text")
    return message

def __set_card_image(message, type, kwargs):
    if kwargs.get("card_image_url") is not None:
        if type == Constant.BOT_CONNECTOR_MESSAGE:
            message["images"] = [
                {
                    "url": kwargs.get("card_image_url"),
                    "alt": "picture of a duck"
                }
            ]

    return message


def __set_card(message, type, kwargs):
    if type == Constant.DIALOGFLOW_MESSAGE:
        message = {
                "fulfillmentMessages":[
                    {
                        "payload":{
                            "skype": __set_card(message, Constant.BOT_CONNECTOR_MESSAGE, kwargs)
                        }
                    }
            ]
        }
        return message
    if type == Constant.BOT_CONNECTOR_MESSAGE:
        base = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.hero",
                    "content": {
                    #     "buttons": [
                    #         {
                    #             "type": "playAudio",
                    #             "title": "Duck Call",
                    #             "value": "url to an audio track of a duck call goes here"
                    #         },
                    #         {
                    #             "type": "openUrl",
                    #             "title": "Watch Video",
                    #             "image": "http://aka.ms/Fo983c",
                    #             "value": "url goes here of the duck in flight"
                    #         }
                    #     ]
                    }
                }
            ]
        }
        base["attachments"][0]["content"] = __set_card_text(base["attachments"][0]["content"], type, kwargs)
        base["attachments"][0]["content"] = __set_card_image(base["attachments"][0]["content"], type, kwargs)

        return base