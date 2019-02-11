import requests


class Qhttp(object):
    def __init__(self):
            pass

    @staticmethod
    def get(url, url_query=None, **kwargs):
        reply = requests.get(url, params=url_query, **kwargs)
        return reply

    @staticmethod
    def post(url, params):
        reply = requests.post(url=url, data=params)
        return reply

    @staticmethod
    def session():
        reply = requests.Session()
        return reply
