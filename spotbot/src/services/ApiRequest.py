import requests
import json
import src.services.Constants as Constants

def make_api_call(**kwargs):

    url = kwargs.get('url')
    method = kwargs.get('method')
    header = kwargs.get('header')
    body = kwargs.get('body')
    params = kwargs.get('params')

    if method == Constants.GET:
        r = requests.get(url=url, headers=header, params=params)
    if method == Constants.POST:
        r = requests.post(url=url, data=body, headers=header)
    if method == Constants.PUT:
        r = requests.put(url=url, data=body, headers=header)
    if method == Constants.DELETE:
        r = requests.delete(url=url, data=body, headers=header)

    if(not r.ok):
        raise Exception("{}: {}".format(r.status_code, r.text))
    if r.text == "" or r.text == None:
        return None
    with open('data.json', 'w') as f:
        f.write(r.text)
    return json.loads(r.text)