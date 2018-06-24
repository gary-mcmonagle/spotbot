import Constant
import json
def generate_message(**kwargs):
    message = {}
    type = kwargs.get('type')
    buttons = kwargs.get('buttons')
    text = kwargs.get('text')
    type = __set_message_type(type)
    if text is not None:
        message = __get_text(message, text, type)
    print(message)
    return json.dumps(message)

def __set_message_type(type):
    if(type is None):
        return Constant.DIALOGFLOW_MESSAGE
    else:
        return type

def __get_text(message, text, type):
    if type == Constant.DIALOGFLOW_MESSAGE:
        message['fulfillmentText'] = text
    return message

