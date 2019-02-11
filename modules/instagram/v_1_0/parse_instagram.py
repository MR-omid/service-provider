import hashlib
import os
import time
from PIL import Image
from components.Qhttp import Qhttp
from vendor.custom_exception import ResultNotFoundError


def parse_profile(profile, user_id, process_id):
    """
     :param profile:  download content of  url
     :param user_id:  duse for instagram account key
     :param process_id:  process_id use for saving img
     :return: parsed data of profile request
     """
    result = {'results': ''}
    result_list = []
    return_result = {'special_properties': '', 'properties': '', 'results': '', 'has_media': True}
    item = profile['user']
    # define necessary dict for each result
    temp_result = {'results': [], 'type': 5, 'properties': [], 'special_properties': [{'sub_type': 3, 'type': 0}]}
    is_business = {'is_business': '', 'type': 0}
    profile_pic_id = {'profile_pic_id': '', 'type': 0}

    # defining dict
    has_placed_url = {'has_placed_url': '', 'type': 1}
    has_highlight_reels = {'has_highlight_reels': '', 'type': 0}
    include_direct_blacklist_status = {'include_direct_blacklist_status': '', 'type': 0}
    has_unseen_besties_media = {'has_unseen_besties_media': '', 'type': 0}
    auto_expand_chaining = {'auto_expand_chaining': '', 'type': 0}
    profile_pic_url = {'profile_pic_url': '', 'type': 13, 'more': {'url': '', 'ref': ''}}
    profile_pic_url_thumbnail = {'profile_pic_url_thumbnail': '', 'type': 13, 'more': {'url': '', 'ref': ''}}
    longitude = {'longitude': '', 'type': 8}
    has_anonymous_profile_picture = {'has_anonymous_profile_picture': '', 'type': 0}
    external_url = {'external_url': '', 'type': 1}
    latitude = {'latitude': '', 'type': 8}
    geo_media_count = {'geo_media_count': '', 'type': 0}
    city_id = {'city_id': '', 'type': 0}
    reel_auto_archive = {'reel_auto_archive': '', 'type': 0}
    school = {'school': '', 'type': 0}
    public_email = {'public_email': '', 'type': 2}
    has_biography_translation = {'has_biography_translation': '', 'type': 0}
    contact_phone_number = {'contact_phone_number': '', 'type': 4}
    full_name = {'full_name': '', 'type': 11}
    category = {'category': '', 'type': 0}
    is_private = {'is_private': '', 'type': 0}
    has_chaining = {'has_chaining': '', 'type': 5}
    following_count = {'following_count': '', 'type': 0}
    follower_count = {'follower_count': '', 'type': 0}
    is_favorite = {'is_favorite': '', 'type': 0}
    is_verified = {'is_verified': '', 'type': 0}
    biography = {'biography': '', 'type': 0}
    media_count = {'media_count': '', 'type': 0}
    business_contact_method = {'business_contact_method': '', 'type': 0}
    address_street = {'address_street': '', 'type': 8}
    is_eligible_for_school = {'is_eligible_for_school': '', 'type': 0}
    public_phone_number = {'public_phone_number': '', 'type': 4}
    direct_messaging = {'direct_messaging': '', 'type': 0}
    has_persistent_profile_school = {'has_persistent_profile_school': '', 'type': 0}
    username = {'username': '', 'type': 5}
    zip_dict = {'zip': '', 'type': 8}
    fb_page_call_to_action_id = {'fb_page_call_to_action_id': '', 'type': 0}
    is_call_to_action_enabled = {'is_call_to_action_enabled': '', 'type': 0}
    pk = {'pk': '', 'type': 0}
    external_lynx_url = {'external_lynx_url': '', 'type': 0}
    usertags_count = {'usertags_count': '', 'type': 0}
    has_placed_orders = {'has_placed_orders': '', 'type': 0}
    city_name = {'city_name': '', 'type': 11}
    alias = ''

    # check key value of api output
    if 'is_business' in item:
        is_business['is_business'] = item['is_business']
    if 'external_lynx_url' in item:
        external_lynx_url['external_lynx_url'] = item['external_lynx_url']
    if 'has_placed_orders' in item:
        has_placed_orders['has_placed_orders'] = item['has_placed_orders']
    if 'profile_pic_id' in item:
        profile_pic_id['profile_pic_id'] = item['profile_pic_id']
    if 'has_placed_url' in item:
        has_placed_url['has_placed_url'] = item['has_placed_url']
    if 'has_highlight_reels' in item:
        has_highlight_reels['has_highlight_reels'] = item['has_highlight_reels']
    if 'include_direct_blacklist_status' in item:
        include_direct_blacklist_status['include_direct_blacklist_status'] = item['include_direct_blacklist_status']
    if 'has_unseen_besties_media' in item:
        has_unseen_besties_media['has_unseen_besties_media'] = item['has_unseen_besties_media']
    if 'auto_expand_chaining' in item:
        auto_expand_chaining['auto_expand_chaining'] = item['auto_expand_chaining']
    if 'longitude' in item:
        longitude['longitude'] = item['longitude']
    if 'has_anonymous_profile_picture' in item:
        has_anonymous_profile_picture['has_anonymous_profile_picture'] = item['has_anonymous_profile_picture']
    if 'external_url' in item:
        external_url['external_url'] = item['external_url']
    if 'latitude' in item:
        latitude['latitude'] = item['latitude']
    if 'geo_media_count' in item:
        geo_media_count['geo_media_count'] = item['geo_media_count']
    if 'city_id' in item:
        city_id['city_id'] = item['city_id']
    if 'reel_auto_archive' in item:
        reel_auto_archive['reel_auto_archive'] = item['reel_auto_archive']
    if 'school' in item:
        school['school'] = item['school']
    if 'public_email' in item:
        public_email['public_email'] = item['public_email']
        public_email_result = {'data': item['public_email'], 'special_properties': [], 'type': 2, 'properties': [],
                               'ref':
                                   {'task': 'instagram_profile', 'section': 'email', 'instagram_account': user_id}}
        temp_result['results'].append(public_email_result)

    if 'has_biography_translation' in item:
        has_biography_translation['has_biography_translation'] = item['has_biography_translation']
    if 'contact_phone_number' in item:
        contact_phone_number['contact_phone_number'] = item['contact_phone_number']
    if 'full_name' in item:
        full_name['full_name'] = item['full_name']
        full_name_result = {'special_properties': [], 'data': item['full_name'], 'type': 11, 'properties': [], 'ref':
            {'task': 'instagram_profile', 'section': 'full_name', 'instagram_account': user_id}}
        temp_result['results'].append(full_name_result)

    if 'category' in item:
        category['category'] = item['category']
    if 'is_private' in item:
        is_private['is_private'] = item['is_private']
    if 'public_phone_number' in item and 'public_phone_country_code' in item:
        public_phone_number['public_phone_number'] = str(item['public_phone_number']) \
                                                     + str(item['public_phone_country_code'])
        public_phone_number_result = {'special_properties': [], 'data': public_phone_number['public_phone_number'],
                                      'type': 4, 'properties': [], 'ref':
                                          {'task': 'instagram_profile', 'section': 'phone_number',
                                           'instagram_account': user_id}}
        temp_result['results'].append(public_phone_number_result)

    if 'has_chaining' in item:
        has_chaining['has_chaining'] = item['has_chaining']
    if 'following_count' in item:
        following_count['following_count'] = item['following_count']
    if 'follower_count' in item:
        follower_count['follower_count'] = item['follower_count']
    if 'is_favorite' in item:
        is_favorite['is_favorite'] = item['is_favorite']
    if 'is_verified' in item:
        is_verified['is_verified'] = item['is_verified']
    if 'biography' in item:
        biography['biography'] = item['biography']
    if 'media_count' in item:
        media_count['media_count'] = item['media_count']
    if 'business_contact_method' in item:
        business_contact_method['business_contact_method'] = item['business_contact_method']
    if 'address_street' in item:
        address_street['address_street'] = item['address_street']
    if 'is_eligible_for_school' in item:
        is_eligible_for_school['is_eligible_for_school'] = item['is_eligible_for_school']
    if 'direct_messaging' in item:
        direct_messaging['direct_messaging'] = item['direct_messaging']
    if 'has_persistent_profile_school' in item:
        has_persistent_profile_school['has_persistent_profile_school'] = item['has_persistent_profile_school']
    if 'username' in item:
        username['username'] = item['username']
        alias = item['username']
        user_name_result = {'data': item['username'], 'type': 5, 'properties': [],
                            'special_properties': [{'sub_type': 3, 'type': 0}], 'ref':
                                {'task': 'instagram_profile', 'section': 'username', 'instagram_account': user_id}}
        temp_result['results'].append(user_name_result)
    if 'zip' in item:
        zip_dict['zip'] = item['zip']
    if 'fb_page_call_to_action_id' in item:
        fb_page_call_to_action_id['fb_page_call_to_action_id'] = item['fb_page_call_to_action_id']
    if 'is_call_to_action_enabled' in item:
        is_call_to_action_enabled['is_call_to_action_enabled'] = item['is_call_to_action_enabled']
    if 'pk' in item:
        pk['pk'] = item['pk']
        alias = str(item['pk'])
    if 'usertags_count' in item:
        usertags_count['usertags_count'] = item['usertags_count']
    if 'city_name' in item:
        city_name['city_name'] = item['city_name']
    if 'is_eligible_for_school' in item:
        is_eligible_for_school['is_eligible_for_school'] = item['is_eligible_for_school']
    if 'address_street' in item:
        address_street['address_street'] = item['address_street']
    if 'is_eligible_for_school' in item:
        is_eligible_for_school['is_eligible_for_school'] = item['is_eligible_for_school']
    if 'hd_profile_pic_url_info' in item:
        if 'url' in item['hd_profile_pic_url_info']:
            profile_pic_list = save_image(item['hd_profile_pic_url_info']['url'], alias, process_id)
            profile_pic_url['profile_pic_url'] = profile_pic_list[0]
            profile_pic_url['more']['url'] = item['hd_profile_pic_url_info']['url']
            profile_pic_url['more']['file_name'] = profile_pic_list[2]
            profile_pic_url['more']['ref'] = 'instagram.com/' + alias

            profile_pic_url_thumbnail['profile_pic_url_thumbnail'] = profile_pic_list[1]
            profile_pic_url_thumbnail['more']['url'] = item['hd_profile_pic_url_info']['url']
            profile_pic_url_thumbnail['more']['file_name'] = profile_pic_list[2]
            profile_pic_url_thumbnail['more']['ref'] = 'instagram.com/' + alias
    elif 'hd_profile_pic_versions' in item:
        if 'url' in item['hd_profile_pic_versions']:
            profile_pic_list = save_image(item['hd_profile_pic_versions']['url'], alias, process_id)
            profile_pic_url['profile_pic_url'] = profile_pic_list[0]
            profile_pic_url['more']['url'] = item['hd_profile_pic_url_info']['url']
            profile_pic_url['more']['file_name'] = profile_pic_list[2]
            profile_pic_url['more']['ref'] = 'instagram.com/' + alias

            profile_pic_url_thumbnail['profile_pic_url_thumbnail'] = profile_pic_list[1]
            profile_pic_url_thumbnail['more']['url'] = item['hd_profile_pic_url_info']['url']
            profile_pic_url_thumbnail['more']['file_name'] = profile_pic_list[2]
            profile_pic_url_thumbnail['more']['ref'] = 'instagram.com/' + alias

    elif 'profile_pic_url' in item:
        profile_pic_list = save_image(item['profile_pic_url'], alias, process_id)
        profile_pic_url['profile_pic_url'] = profile_pic_list[0]
        profile_pic_url['more']['url'] = item['hd_profile_pic_url_info']['url']
        profile_pic_url['more']['file_name'] = profile_pic_list[2]
        profile_pic_url['more']['ref'] = 'instagram.com/' + alias

        profile_pic_url_thumbnail['profile_pic_url_thumbnail'] = profile_pic_list[1]
        profile_pic_url_thumbnail['more']['url'] = item['hd_profile_pic_url_info']['url']
        profile_pic_url_thumbnail['more']['file_name'] = profile_pic_list[2]
        profile_pic_url_thumbnail['more']['ref'] = 'instagram.com/' + alias

    # create structure of properties
    temp_result['properties'].append(profile_pic_url)
    temp_result['properties'].append(profile_pic_url_thumbnail)
    temp_result['properties'].append(full_name)
    temp_result['properties'].append(username)
    temp_result['properties'].append(city_name)
    temp_result['properties'].append(public_email)
    temp_result['properties'].append(public_phone_number)
    temp_result['properties'].append(contact_phone_number)
    temp_result['properties'].append(external_url)
    temp_result['properties'].append(zip_dict)
    temp_result['properties'].append(address_street)
    temp_result['properties'].append(latitude)
    temp_result['properties'].append(longitude)
    temp_result['properties'].append(city_id)
    temp_result['properties'].append(biography)
    # create structure of special properties
    temp_result['special_properties'].append(has_placed_url)
    temp_result['special_properties'].append(has_highlight_reels)
    temp_result['special_properties'].append(include_direct_blacklist_status)
    temp_result['special_properties'].append(has_unseen_besties_media)
    temp_result['special_properties'].append(auto_expand_chaining)
    temp_result['special_properties'].append(has_placed_orders)
    temp_result['special_properties'].append(external_lynx_url)
    temp_result['special_properties'].append(follower_count)
    temp_result['special_properties'].append(following_count)
    temp_result['special_properties'].append(is_business)
    temp_result['special_properties'].append(has_biography_translation)
    temp_result['special_properties'].append(business_contact_method)
    temp_result['special_properties'].append(category)
    temp_result['special_properties'].append(geo_media_count)
    temp_result['special_properties'].append(pk)
    temp_result['special_properties'].append(is_call_to_action_enabled)
    temp_result['special_properties'].append(media_count)
    temp_result['special_properties'].append(has_chaining)
    temp_result['special_properties'].append(has_anonymous_profile_picture)
    temp_result['special_properties'].append(fb_page_call_to_action_id)
    temp_result['special_properties'].append(school)
    temp_result['special_properties'].append(is_verified)
    temp_result['special_properties'].append(is_private)
    temp_result['special_properties'].append(is_favorite)
    temp_result['special_properties'].append(is_eligible_for_school)
    temp_result['special_properties'].append(direct_messaging)
    temp_result['special_properties'].append(reel_auto_archive)
    temp_result['special_properties'].append(usertags_count)
    temp_result['special_properties'].append(has_persistent_profile_school)
    result_list.append(temp_result)
    if len(result_list) == 0:
        raise ResultNotFoundError('not found any result')
    result['results'] = result_list
    return_result['special_properties'] = result['results'][-1]['special_properties']
    return_result['properties'] = result['results'][-1]['properties']
    return_result['results'] = result['results'][-1]['results']
    return_result['has_media'] = True
    return [return_result, pk]


def parse_follower_following(user_list, alias, process_id, request_number):
    """
     :param user_list:  download content of  url
     :param alias:  alias use for saving image
     :param process_id:  process_id use for saving img
     :param request_number:  number of expected result record
     :return: parsed data of follower_following request
     """
    return_result = {'results': [], 'has_media': True}
    for item in user_list:
        try:
            if len(return_result['results']) >= request_number:
                break
            # defining structure
            temp_result = {'data': '', 'type': 5, 'properties': [], 'special_properties': [{'sub_type': 3, 'type': 0}]}
            reel_auto_archive = {'reel_auto_archive': '', 'type': 0}
            profile_pic_id = {'profile_pic_id': '', 'type': 0}
            has_anonymous_profile_picture = {'has_anonymous_profile_picture': '', 'type': 0}
            is_verified = {'is_verified': '', 'type': 0}
            is_private = {'is_private': '', 'type': 0}

            pk = {'pk': '', 'type': 0}
            latest_reel_media = {'latest_reel_media': '', 'type': 0}
            full_name = {'full_name': '', 'type': 11}
            profile_pic_url = {'profile_pic_url': '', 'type': 13, 'more': {'url': '', 'ref': ''}}
            profile_pic_url_thumbnail = {'profile_pic_url_thumbnail': '', 'type': 13, 'more': {'url': '', 'ref': ''}}

            # assigning values
            if 'username' in item:
                temp_result['data'] = item['username']
            else:
                continue
            if 'profile_pic_url' in item:
                profile_pic_list = save_image(item['profile_pic_url'], alias, process_id)
                profile_pic_url['profile_pic_url'] = profile_pic_list[0]
                profile_pic_url['more']['url'] = item['profile_pic_url']
                profile_pic_url['more']['file_name'] = profile_pic_list[2]
                profile_pic_url['more']['ref'] = 'instagram.com/' + alias
                temp_result['properties'].append(profile_pic_url)

                profile_pic_url_thumbnail['profile_pic_url_thumbnail'] = profile_pic_list[1]
                profile_pic_url_thumbnail['more']['url'] = item['profile_pic_url']
                profile_pic_url_thumbnail['more']['file_name'] = profile_pic_list[2]
                profile_pic_url_thumbnail['more']['ref'] = 'instagram.com/' + alias
                temp_result['properties'].append(profile_pic_url_thumbnail)

            if 'full_name' in item:
                full_name['full_name'] = item['full_name']
            if 'reel_auto_archive' in item:
                reel_auto_archive['reel_auto_archive'] = item['reel_auto_archive']
            if 'profile_pic_id' in item:
                profile_pic_id['profile_pic_id'] = item['profile_pic_id']
            if 'has_anonymous_profile_picture' in item:
                has_anonymous_profile_picture['has_anonymous_profile_picture'] = item['has_anonymous_profile_picture']
            if 'is_private' in item:
                is_private['is_private'] = item['is_private']
            if 'is_verified' in item:
                is_verified['is_verified'] = item['is_verified']
            if 'pk' in item:
                pk['pk'] = item['pk']
            if 'latest_reel_media' in item:
                latest_reel_media['latest_reel_media'] = item['latest_reel_media']

            temp_result['properties'].append(pk)
            temp_result['properties'].append(full_name)
            temp_result['special_properties'].append(latest_reel_media)
            temp_result['special_properties'].append(is_verified)
            temp_result['special_properties'].append(is_private)
            temp_result['special_properties'].append(profile_pic_id)
            temp_result['special_properties'].append(reel_auto_archive)
            temp_result['special_properties'].append(has_anonymous_profile_picture)
            return_result['results'].append(temp_result)

        except Exception:
            continue
    if len(return_result['results']) == 0:
        raise ResultNotFoundError
    return return_result


def parse_search_contact(item, process_id):
    return_result = {}
    alias = ''
    result = {'data': '', 'type': 5, 'properties': [], 'special_properties': [{'sub_type': 3, 'type': 0}]}
    profile_pic_url = {'profile_pic_url': '', 'type': 13, 'more': {'url': '', 'ref': ''}}
    profile_pic_url_thumbnail = {'profile_pic_url_thumbnail': '', 'type': 13, 'more': {'url': '', 'ref': ''}}
    if 'username' in item:
        result['data'] = item['username']
        alias = item['username']
    if 'full_name' in item:
        result['properties'].append({'full_name': item['full_name'], 'type': 11})

    if 'pk' in item:
        result['special_properties'].append({'pk': item['pk'], 'type': 0})
    if 'is_verified' in item:
        result['properties'].append({'is_verified': item['is_verified'], 'type': 0})
    if 'reel_auto_archive' in item:
        result['special_properties'].append({'reel_auto_archive': item['reel_auto_archive'], 'type': 0})
    if 'profile_pic_url' in item and alias:
        profile_pic_list = save_image(item['profile_pic_url'], alias, process_id)
        profile_pic_url['profile_pic_url'] = profile_pic_list[0]
        profile_pic_url['more']['url'] = item['profile_pic_url']
        profile_pic_url['more']['file_name'] = profile_pic_list[2]
        profile_pic_url['more']['ref'] = 'instagram.com/' + alias
        result['properties'].append(profile_pic_url)

        profile_pic_url_thumbnail['profile_pic_url_thumbnail'] = profile_pic_list[1]
        profile_pic_url_thumbnail['more']['url'] = item['profile_pic_url']
        profile_pic_url_thumbnail['more']['file_name'] = profile_pic_list[2]
        profile_pic_url_thumbnail['more']['ref'] = 'instagram.com/' + alias
        result['properties'].append(profile_pic_url_thumbnail)

    return_result['results'] = result
    return_result['has_media'] = True
    return return_result


def parse_search_by_query(people_list, process_id):
    """
     :param people_list:  list of people who showed in search result
     :param process_id:  process_id for saving photo
     :return: return structured result
     """
    return_result = {'results': [], 'has_media': True}
    for item in people_list:
        try:
            temp_result = {'data': '', 'type': 5, 'properties': [], 'special_properties': [{'sub_type': 3, 'type': 0}]}
            reel_auto_archive = {'reel_auto_archive': '', 'type': 0}
            profile_pic_id = {'profile_pic_id': '', 'type': 0}
            has_anonymous_profile_picture = {'has_anonymous_profile_picture': '', 'type': 0}
            is_verified = {'is_verified': '', 'type': 0}
            is_private = {'is_private': '', 'type': 0}
            follower_count = {'follower_count': '', 'type': 0}
            mutual_followers_count = {'mutual_followers_count': '', 'type': 0}
            pk = {'pk': '', 'type': 0}
            latest_reel_media = {'latest_reel_media': '', 'type': 0}
            full_name = {'full_name': '', 'type': 11}
            profile_pic_url = {'profile_pic_url': '', 'type': 13, 'more': {'url': '', 'ref': ''}}
            profile_pic_url_thumbnail = {'profile_pic_url_thumbnail': '', 'type': 13, 'more': {'url': '', 'ref': ''}}

            # assigning values
            if 'username' in item:
                temp_result['data'] = item['username']
                alias = item['username']
            else:
                continue
            if 'profile_pic_url' in item:
                profile_pic_list = save_image(item['profile_pic_url'], alias, process_id)
                profile_pic_url['profile_pic_url'] = profile_pic_list[0]
                profile_pic_url['more']['url'] = item['profile_pic_url']
                profile_pic_url['more']['file_name'] = profile_pic_list[2]
                profile_pic_url['more']['ref'] = 'instagram.com/' + alias
                temp_result['properties'].append(profile_pic_url)

                profile_pic_url_thumbnail['profile_pic_url_thumbnail'] = profile_pic_list[1]
                profile_pic_url_thumbnail['more']['url'] = item['profile_pic_url']
                profile_pic_url_thumbnail['more']['file_name'] = profile_pic_list[2]
                profile_pic_url_thumbnail['more']['ref'] = 'instagram.com/' + alias
                temp_result['properties'].append(profile_pic_url_thumbnail)

            if 'full_name' in item:
                full_name['full_name'] = item['full_name']
            if 'reel_auto_archive' in item:
                reel_auto_archive['reel_auto_archive'] = item['reel_auto_archive']
            if 'profile_pic_id' in item:
                profile_pic_id['profile_pic_id'] = item['profile_pic_id']
            if 'has_anonymous_profile_picture' in item:
                has_anonymous_profile_picture['has_anonymous_profile_picture'] = item['has_anonymous_profile_picture']
            if 'is_private' in item:
                is_private['is_private'] = item['is_private']
            if 'is_verified' in item:
                is_verified['is_verified'] = item['is_verified']
            if 'pk' in item:
                pk['pk'] = item['pk']
            if 'follower_count' in item:
                follower_count['follower_count'] = item['follower_count']
            if 'mutual_followers_count' in item:
                mutual_followers_count['mutual_followers_count'] = item['mutual_followers_count']

            temp_result['properties'].append(pk)
            temp_result['properties'].append(full_name)
            temp_result['special_properties'].append(latest_reel_media)
            temp_result['special_properties'].append(is_verified)
            temp_result['special_properties'].append(is_private)
            temp_result['special_properties'].append(profile_pic_id)
            temp_result['special_properties'].append(reel_auto_archive)
            temp_result['special_properties'].append(has_anonymous_profile_picture)
            temp_result['pk'] = item['pk']

            return_result['results'].append(temp_result)

        except Exception:
            continue
    if len(return_result['results']) == 0:
        raise ResultNotFoundError
    return return_result


def save_image(url, username, process_id):
    """
     :param url:  download content of this url
     :param username:  use for naming files
     :param process_id:  use for saving in correct path
     :return: the path that can download photos
     """

    if username is None:
        return ''

    storage = [
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
        '/modules/storage/' + process_id]
    base_path = storage[0]
    relative_path = storage[1]
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
        return ['', '', '']
    try:
        size = 72, 72
        thumbnail_save_path = thumbnail_full_path + file + '.jpg'
        image = Image.open(img_save_path)
        image.thumbnail(size, Image.ANTIALIAS)
        image.save(thumbnail_save_path, quality=40, optimize=True)
    except Exception:
        pass
    return [img_save_path, thumbnail_save_path, file]
