# importing the requests library
import hashlib
import hmac
import json
import urllib
import uuid
from urllib import parse

import requests

u = 'chelsea.naspnetworks'
p = 'Hivaithai2'

m = hashlib.md5()
m.update(u.encode('utf-8') + p.encode('utf-8'))

# your API key here
IG_SIG_KEY = "55e91155636eaa89ba5ed619eb4645a4daf1103f2161dbfe6fd94d5ea7716095"


def generateDeviceId(seed):
    volatile_seed = "12345"
    m = hashlib.md5()
    m.update(seed.encode('utf-8') + volatile_seed.encode('utf-8'))
    return 'android-' + m.hexdigest()[:16]


def generateUUID(type):
    generated_uuid = str(uuid.uuid4())
    if (type):
        return generated_uuid
    else:
        return generated_uuid.replace('-', '')


def generateSignature(data, skip_quote=False):
    if not skip_quote:
        try:
            parsedData = urllib.parse.quote(data)
        except AttributeError:
            parsedData = urllib.quote(data)
    else:
        parsedData = data
    return 'ig_sig_key_version=4&signed_body=' + hmac.new(IG_SIG_KEY.encode('utf-8'), data.encode('utf-8'),
                                                          hashlib.sha256).hexdigest() + '.' + parsedData


headers = {
    'User-Agent': 'Instagram 8.2.0 Android (18/4.3; 320dpi; 720x1280; Xiaomi; HM 1SW; armani; qcom; en_US)',
           'Connection': 'Keep-Alive', 'Accept': '*/*', 'Accept-Language': 'en-US',
           'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}
GUID = str(uuid.uuid4())
url = "https://i.instagram.com/api/v1/si/fetch_headers/?challenge_type=signup&guid=" + generateUUID(False)
r = requests.get(url, headers=headers)

csrftoken = r.cookies['csrftoken']

headers = {'User-Agent': 'Instagram 8.2.0 Android (18/4.3; 320dpi; 720x1280; Xiaomi; HM 1SW; armani; qcom; en_US)',
           'Connection': 'keep-Alive', 'Accept': '*/*', 'Accept-Language': 'en-US',
           'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'}

# data to be sent to api
data = {'phone_id': generateUUID(True),
        '_csrftoken': csrftoken,
        'username': 'chelsea.naspnetworks',
        'password': 'Hivaithai2',
        'guid': generateUUID(True),
        'device_id': generateDeviceId(m.hexdigest()),
        'login_attempt_count': "0"}

json_data = json.dumps(data)

API_ENDPOINT = "https://i.instagram.com/api/v1/accounts/login/"

session = requests.Session()

r = session.post(url=API_ENDPOINT, data=generateSignature(json_data), headers=headers)

response = r.text
# print("The response is:%s" % response)
# print(r.status_code)

API_ENDPOINT = "https://i.instagram.com/api/v1/users/shadiservat/usernameinfo/"
# API_ENDPOINT = "https://i.instagram.com/api/v1/users/_kurdistannn/usernameinfo/"

s = session.get(url=API_ENDPOINT, data=generateSignature(json_data), headers=headers)

response = s.text
# print("The response is:%s" % response)
# print(r.status_code)
# print(r.cookies)

# if __name__ == '__main__':
    # insta = Instagram('chelsea.naspnetworks', 'Hivaithai2')
    # insta.login('chelsea.naspnetworks', 'Hivaithai2')
    # print(insta.view('1561651'))

    # for mediaid in insta.media_ids:
    #     cms = insta.get_all_comments(media_id=mediaid)
    #     print('\n')
    #     print('media id {} comments'.format(mediaid))
    #     for cm in cms['preview_comments']:
    #         print('{}: '.format(cm['user_id']), cm['text'])

    # print('\n')
    # for mediaid in insta.media_ids:
    #     likes = insta.get_media_likers(media_id=mediaid)
    #     print(likes)

    # print(to_json(insta.profile('2248414940')))
