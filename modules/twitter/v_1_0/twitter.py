import hashlib
import json
import os
import time

import oauth2 as oauth
from PIL import Image

from components.Qhttp import Qhttp
from vendor.custom_exception import NetworkError, ResultNotFoundError, InvalidInputError, TwitterApiConstraint


class Twitter:
    def __init__(self, consumer_key, consumer_secret, access_key, access_secret, parent=None):

        self.consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
        self.access_token = oauth.Token(key=access_key, secret=access_secret)
        self.client = oauth.Client(self.consumer, self.access_token)
        self.default_number = 4
        self.check_number = 0
        self.parent = parent
        proccess_id = parent.task_model.process_id
        self.storage = [
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
            '/modules/storage/' + proccess_id]

    def update_progressbar(self, message, percent):
        if self.parent:
            self.parent.progress = {'state': message, 'percent': percent}

    def search(self, query, count):
        """
        :param query: string, use as a query search
        :param count: string, use as a number of search result
        :return: search result
        """
        self.update_progressbar('request submitted successfully, request to twitter: search query', 20)

        if count is not None:
            if count > 200:
                count = 200
            timeline_endpoint = "https://api.twitter.com/1.1/users/search.json?q=%s&count=%s" % (query, str(count))

        else:
            timeline_endpoint = "https://api.twitter.com/1.1/users/search.json?q=%s&count=%s" % \
                                (query, str(self.default_number))

        try:  # set request to twitter api, using different link if use id or screen_name
            if self.parent:
                self.parent.check_point()
            response, data = self.client.request(timeline_endpoint)
        except Exception as e:  # can not access twitter
            raise NetworkError(e)
        self.update_progressbar('received data from api', 40)
        if self.parent:
            self.parent.check_point()
        if 'status' not in response:  # some thing goes wrong
            raise InvalidInputError("status not found")
        if response['status'] != '200':  # something goes wrong
            data_loads = json.loads(str(bytes.decode(data)))

            if data_loads['errors'][-1]['message'] == 'Rate limit exceeded':
                raise TwitterApiConstraint('Twitter rejected 3 consecutive attempts to access its API under your '
                                           'Twitter account ')
            else:
                raise InvalidInputError(data_loads['errors'][-1]['message'])
        data_loads = json.loads(str(bytes.decode(data)))

        self.update_progressbar('parse_result', 75)
        # parse results
        return_result = Twitter.__parse_search(self, data_loads)[0]
        return_result['has_mdia'] = True
        return return_result
    def show_user(self, user_id):
        """
        :param user_id: string, use as a user_id or screen_name search
        :return: search result
        """
        return_result = {'results': [], 'has_media': True}
        self.update_progressbar('request submitted successfully, request to twitter: show user', 20)
        try:  # set request to twitter api, using different link if use id or screen_name
            int(user_id)
            timeline_endpoint = "https://api.twitter.com/1.1/users/show.json?user_id=%s" % (str(user_id))
        except ValueError:
            timeline_endpoint = "https://api.twitter.com/1.1/users/show.json?screen_name=%s" % (str(user_id))

        try:
            if self.parent:
                self.parent.check_point()
            response, data = self.client.request(timeline_endpoint)
        except Exception:
            raise NetworkError('can not connect to twitter')
        self.update_progressbar('received data from api', 40)
        if self.parent:
            self.parent.check_point()
        if 'status' not in response:  # something goes wrong
            raise InvalidInputError("status not found")
        if response['status'] != '200':  # something goes wrong
            data_loads = json.loads(str(bytes.decode(data)))
            if data_loads['errors'][-1]['message'] == 'Rate limit exceeded':
                raise TwitterApiConstraint('Twitter rejected 3 consecutive attempts to access its API under your '
                                           'Twitter account ')
            else:
                raise InvalidInputError(data_loads['errors'][-1]['message'])
        data_loads = json.loads(str(bytes.decode(data)))
        info = [data_loads]
        # extract json demand format from parse result
        self.update_progressbar('parse_result', 75)
        return_value = Twitter.__parse_search(self, info)
        result = return_value[0]
        entity_list = return_value[1]
        return_result['special_properties'] = result['results'][-1]['special_properties']
        return_result['properties'] = result['results'][-1]['properties']

        for item in entity_list:
            data = {'data':'', 'type':''}
            ref = {'ref': {'task': 'twitter_profile', 'twitter_account': user_id, 'section': ''}}
            if 'name' in item.keys():
                data['data'] = item['name']
                data['type'] = 11
                ref['ref']['section'] = 'name'

            if 'location' in item.keys():
                ref['ref']['section'] = 'location'
                data['data'] = item['location']
                data['type'] = 8

            if 'screen_name' in item.keys():
                ref['ref']['section'] = 'screen_name'
                data['data'] = item['screen_name']
                data['type'] = 5

            data.update(ref)
            return_result['results'].append(data)
        return return_result

    def friends_list(self, user_id, count=None):
        """
        :param user_id: string, use as a user_id or screen_name search
        :param count: number of result
        :return: search result
        """
        self.update_progressbar('request submitted successfully, request to twitter: friends_list', 20)
        try:  # set request to twitter api, using different link if use id or screen_name and use count or not
            int(user_id)
            if count is not None:
                if count > 200:
                    count = 200
                timeline_endpoint = "https://api.twitter.com/1.1/friends/list.json?user_id=%s&count=%s" % (
                    str(user_id), str(count))
            else:
                timeline_endpoint = "https://api.twitter.com/1.1/friends/list.json?user_id=%s&count=%s" % (
                    str(user_id), str(self.default_number))
        except ValueError:
            if count is not None:
                if count > 200:
                    count = 200
                timeline_endpoint = "https://api.twitter.com/1.1/friends/list.json?screen_name=%s&count=%s" % (
                    str(user_id), str(count))
            else:
                timeline_endpoint = "https://api.twitter.com/1.1/friends/list.json?screen_name=%s&count=%s" % (
                    str(user_id), str(self.default_number))

        try:  # set request to twitter api
            if self.parent:
                self.parent.check_point()
            response, data = self.client.request(timeline_endpoint)
        except Exception:
            raise NetworkError('can not connect to twitter')
        self.update_progressbar('received data from api', 40)
        if self.parent:
            self.parent.check_point()
        if 'status' not in response:  # somethings goes wrong
            raise InvalidInputError("status not found")
        if response['status'] != '200':  # something goes wrong
            data_loads = json.loads(str(bytes.decode(data)))
            if data_loads['errors'][-1]['message'] == 'Rate limit exceeded':
                raise TwitterApiConstraint('Twitter rejected 3 consecutive attempts to access its API under your '
                                           'Twitter account ')
            else:
                raise InvalidInputError(data_loads['errors'][-1]['message'])
        # parse result
        data_loads = json.loads(str(bytes.decode(data)))
        self.update_progressbar('parse_result', 75)
        return_result = Twitter.__parse_search(self, data_loads['users'])[0]
        return_result['has_media'] = True
        return return_result

    def follower_list(self, user_id, count=None):
        """
        :param user_id: string, use as a user_id or screen_name search
        :param count: number of result
        :return: search result
        """
        self.update_progressbar('request submitted successfully, request to twitter: follower_list', 20)

        try:  # set request to twitter api, using different link if use id or screen_name and use count or not
            int(user_id)
            if count is not None:
                if count > 200:
                    count = 200
                timeline_endpoint = "https://api.twitter.com/1.1/followers/list.json?user_id=%s&count=%s" % (str(
                    user_id), str(count))
            else:
                timeline_endpoint = "https://api.twitter.com/1.1/followers/list.json?user_id=%s&count=%s" % (str(
                    user_id), str(self.default_number))
        except ValueError:
            if count is not None:
                if count > 200:
                    count = 200
                timeline_endpoint = "https://api.twitter.com/1.1/followers/list.json?screen_name=%s&count=%s" % (str(
                    user_id), str(count))
            else:
                timeline_endpoint = "https://api.twitter.com/1.1/followers/list.json?screen_name=%s&count=%s" % (str(
                    user_id), str(self.default_number))
        try:
            if self.parent:
                self.parent.check_point()
            response, data = self.client.request(timeline_endpoint)
        except Exception:
            raise NetworkError('can not connect to twitter')
        self.update_progressbar('received data from api', 40)
        if self.parent:
            self.parent.check_point()
        if 'status' not in response:  # something goes wrong
            raise InvalidInputError("status not found")
        if response['status'] != '200':  # something goes wrong
            data_loads = json.loads(str(bytes.decode(data)))
            if data_loads['errors'][-1]['message'] == 'Rate limit exceeded':
                raise TwitterApiConstraint('Twitter rejected 3 consecutive attempts to access its API under your '
                                           'Twitter account ')
            else:
                raise InvalidInputError(data_loads['errors'][-1]['message'])
        data_loads = json.loads(str(bytes.decode(data)))
        self.update_progressbar('parse_result', 75)
        return_result = Twitter.__parse_search(self, data_loads['users'])[0]
        return_result['has_media'] = True
        return return_result

    def __parse_search(self, searchs):
        result = {'results': ''}
        result_list = []
        entity_list = []
        for search in searchs:

            # define necessary dict for each result
            if self.parent:
                self.parent.check_point()
            alias = ''
            temp_result = {'data': '', 'type': 5, 'properties': [], 'special_properties': [{'sub_type': 2, 'type': 0}]}
            name = {'name': '', 'type': 11}
            description = {'description': '', 'type': 0}
            url = {'url': [], 'type': 1}
            url_unexpand = {'title': ''}
            url_expand = {'title': ''}
            screen_name = {'screen_name': '', 'type': 5}
            location = {'location': '', 'type': 8}
            protected = {'protected': '', 'type': 0}
            verified = {'verified': '', 'type': 0}
            followers_count = {'followers_count': '', 'type': 0}
            friends_count = {'friends_count': '', 'type': 0}
            listed_count = {'listed_count': '', 'type': 0}
            favourites_count = {'favourites_count': '', 'type': 0}
            statuses_count = {'statuses_count': '', 'type': 0}
            created_at = {'created_at': '', 'type': 0}
            geo_enabled = {'geo_enabled': '', 'type': 0}
            lang = {'lang': '', 'type': 11}
            contributors_enabled = {'contributors_enabled': '', 'type': 0}
            profile_background_image_url_https = {'profile_background_image_url': '', 'type': 13,
                                                  'more': {'ref': '', 'url': ''}}
            profile_background_image_url_https_thumbnail = {'profile_background_image_url_thumbnail': '', 'type': 13,
                                                            'more': {'ref': '', 'url': ''}}
            profile_banner_url = {'profile_banner_url': '', 'type': 13, 'more': {'ref': '', 'url': ''}}
            profile_banner_url_thumbnail = {'profile_banner_url_thumbnail': '', 'type': 13,
                                            'more': {'ref': '', 'url': ''}}
            profile_image_url_https = {'profile_image_url': '', 'type': 13, 'more': {'ref': '', 'url': ''}}
            profile_image_url_https_thumbnail = {'profile_image_url_thumbnail': '', 'type': 13,
                                                 'more': {'ref': '', 'url': ''}}

            if 'screen_name' in search:
                temp_result['data'] = search['screen_name']
                screen_name['screen_name'] = search['screen_name']
                alias = search['screen_name']
            if 'description' in search:
                description['description'] = search['description']
            if 'name' in search:
                name['name'] = search['name']
            if 'url' in search:
                url_expand['title'] = search['url']
            if 'screen_name' in search:
                temp_result['data'] = search['screen_name']
                screen_name['screen_name'] = search['screen_name']
            if 'location' in search:
                location['location'] = search['location']
            if 'protected' in search:
                protected['protected'] = search['protected']
            if 'verified' in search:
                verified['verified'] = search['verified']
            if 'followers_count' in search:
                followers_count['followers_count'] = search['followers_count']
            if 'friends_count' in search:
                friends_count['friends_count'] = search['friends_count']
            if 'listed_count' in search:
                listed_count['listed_count'] = search['listed_count']
            if 'favourites_count' in search:
                favourites_count['favourites_count'] = search['favourites_count']
            if 'statuses_count' in search:
                statuses_count['statuses_count'] = search['statuses_count']
            if 'created_at' in search:
                created_at['created_at'] = search['created_at']
            if 'geo_enabled' in search:
                geo_enabled['geo_enabled'] = search['geo_enabled']
            if 'lang' in search:
                lang['lang'] = search['lang']
            if 'contributors_enabled' in search:
                contributors_enabled['contributors_enabled'] = search['contributors_enabled']
            try:
                if 'profile_background_image_url_https' in search:
                    profile_background_image_url_https_list = self.__save_image(
                        search['profile_background_image_url_https'],
                        alias)
                    profile_background_image_url_https['profile_background_image_url'] = \
                        profile_background_image_url_https_list[0]
                    profile_background_image_url_https['more']['ref'] = 'https://twitter.com/' + alias
                    profile_background_image_url_https['more']['url'] = search[
                        'profile_background_image_url_https']
                    profile_background_image_url_https['more']['file_name'] = profile_background_image_url_https_list[2]

                    profile_background_image_url_https_thumbnail['profile_background_image_url_thumbnail'] = \
                        profile_background_image_url_https_list[1]
                    profile_background_image_url_https_thumbnail['more']['ref'] = 'https://twitter.com/' + alias
                    profile_background_image_url_https_thumbnail['more']['url'] = search[
                        'profile_background_image_url_https']
                    profile_background_image_url_https_thumbnail['more']['file_name'] = \
                        profile_background_image_url_https_list[2]
            except Exception:
                profile_background_image_url_https = {'profile_background_image_url': '', 'type': 13,
                                                      'more': {'ref': '', 'url': ''}}
                profile_background_image_url_https_thumbnail = {'profile_background_image_url_thumbnail': '',
                                                                'type': 13,
                                                                'more': {'ref': '', 'url': ''}}
            try:
                if 'profile_banner_url' in search:
                    profile_banner_url_list = self.__save_image(search['profile_banner_url'], alias)
                    profile_banner_url['profile_banner_url'] = profile_banner_url_list[0]
                    profile_banner_url['more']['ref'] = 'https://twitter.com/' + alias
                    profile_banner_url['more']['url'] = search[
                        'profile_banner_url']
                    profile_banner_url['more']['file_name'] = profile_banner_url_list[2]

                    profile_banner_url_thumbnail['profile_banner_url_thumbnail'] = profile_banner_url_list[1]
                    profile_banner_url_thumbnail['more']['ref'] = 'https://twitter.com/' + alias
                    profile_banner_url_thumbnail['more']['url'] = search[
                        'profile_banner_url']
                    profile_banner_url_thumbnail['more']['file_name'] = profile_banner_url_list[2]
            except Exception:
                profile_banner_url = {'profile_banner_url': '', 'type': 13, 'more': {'ref': '', 'url': ''}}
                profile_banner_url_thumbnail = {'profile_banner_url_thumbnail': '', 'type': 13,
                                                'more': {'ref': '', 'url': ''}}
            try:
                if 'profile_image_url_https' in search:
                    profile_image_url_https_list = self.__save_image(search['profile_image_url_https'], alias)
                    profile_image_url_https['profile_image_url'] = profile_image_url_https_list[0]
                    profile_image_url_https['more']['ref'] = 'https://twitter.com/' + alias
                    profile_image_url_https['more']['file_name'] = profile_image_url_https_list[2]
                    profile_image_url_https['more']['url'] = search[
                        'profile_image_url_https']

                    profile_image_url_https_thumbnail['profile_image_url_thumbnail'] = profile_image_url_https_list[1]
                    profile_image_url_https_thumbnail['more']['ref'] = 'https://twitter.com/' + alias
                    profile_image_url_https_thumbnail['more']['file_name'] = profile_image_url_https_list[2]
                    profile_image_url_https_thumbnail['more']['url'] = search[
                        'profile_image_url_https']
            except Exception:
                profile_image_url_https = {'profile_image_url': '', 'type': 13, 'more': {'ref': '', 'url': ''}}
                profile_image_url_https_thumbnail = {'profile_image_url_thumbnail': '', 'type': 13,
                                                     'more': {'ref': '', 'url': ''}}

            # create structure of final result
            temp_result['properties'].append(name)
            temp_result['properties'].append(description)
            url['url'].append(url_unexpand)
            url['url'].append(url_expand)
            temp_result['properties'].append(url)
            temp_result['special_properties'].append(screen_name)
            temp_result['special_properties'].append(location)
            temp_result['special_properties'].append(protected)
            temp_result['special_properties'].append(verified)
            temp_result['special_properties'].append(followers_count)
            temp_result['special_properties'].append(friends_count)
            temp_result['special_properties'].append(listed_count)
            temp_result['special_properties'].append(favourites_count)
            temp_result['special_properties'].append(statuses_count)
            temp_result['special_properties'].append(created_at)
            temp_result['special_properties'].append(geo_enabled)
            temp_result['special_properties'].append(lang)
            temp_result['special_properties'].append(contributors_enabled)
            temp_result['special_properties'].append(profile_background_image_url_https)
            temp_result['special_properties'].append(profile_background_image_url_https_thumbnail)
            temp_result['special_properties'].append(profile_banner_url)
            temp_result['special_properties'].append(profile_banner_url_thumbnail)
            temp_result['special_properties'].append(profile_image_url_https)
            temp_result['special_properties'].append(profile_image_url_https_thumbnail)
            result_list.append(temp_result)
            entity_list.append(screen_name)
            entity_list.append(location)
            entity_list.append(name)
        if len(result_list) == 0:
            raise ResultNotFoundError('not found any result')
        result['results'] = result_list
        return result, entity_list

    def __save_image(self, url, username):
        """
         :param url:  download content of this url
         :param username:  use for naming files
         :return: the path that can download photos
         """

        if username is None:
            return ''
        base_path = self.storage[0]
        relative_path = self.storage[1]
        img_full_path = base_path + '/' + relative_path + '/'
        thumbnail_full_path = base_path + '/' + relative_path + '/' + 'thumbnail' + '/'
        thumbnail_save_path = ''
        file = str(hashlib.md5(username.encode('utf-8')).hexdigest()) + str(
            hashlib.md5(str(int(round(time.time() * 1000))).encode('utf-8')).hexdigest())
        os.makedirs(img_full_path, exist_ok=True)
        os.makedirs(thumbnail_full_path, exist_ok=True)
        try:  # using Qhttps get request to download
            img_data = Qhttp.get(url, timeout=10).content
            img_save_path = img_full_path + file + '.jpg'
            image = open(img_save_path, 'wb')
            image.write(img_data)
            image.close()
        except Exception:
            return ''
        try:
            size = 72, 72
            thumbnail_save_path = thumbnail_full_path + file + '.jpg'
            image = Image.open(img_save_path)
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(thumbnail_save_path, quality=40, optimize=True)
        except Exception:
            pass
        return [img_save_path, thumbnail_save_path, file]
