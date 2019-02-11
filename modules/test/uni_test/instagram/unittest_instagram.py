import unittest
from modules.instagram.v_1_0.instagram import Instagram
from vendor.custom_exception import ResultNotFoundError, LoginError


class TestInstagram(unittest.TestCase):
    valid_key = {"username": "chelsea.naspnetworks",
                 "password": "Hivaithai2",
                 }

    # testing invalid keys and notfounderror
    def test_unauthorized_consumer(self):
        # define invalid value
        username = 'invalid'
        password = 'invalid'

        instagram_1 = Instagram(username, TestInstagram.valid_key['password'])
        instagram_2 = Instagram(TestInstagram.valid_key['username'], password)

        instagram_valid = Instagram(TestInstagram.valid_key['username'], TestInstagram.valid_key['password'])

        # testing invalid username
        with self.assertRaises(LoginError):
            instagram_1.profile('2248414940')

        # testing invalid password
        with self.assertRaises(LoginError):
            instagram_2.profile('2248414940')

        # testing notfounderror
        with self.assertRaises(ResultNotFoundError):
            instagram_valid.profile('adsfvasfgverwfgawefvefklfnklweamnfawfmlawemfklfnklwae')

        # add valid test case (valid profile) to test input key: value
        # attention: if test case exceed from 10 (approximately) req in loop, got ApiConstraint exception
        test_cases = ['football', 'danielsturridge', 'danielsturridge', 'treysongz', 'mikeyk', 'realmadrid',
                      'fcbarcelona', '2248414940', 'davidbeckham', 'camerondallas']
        for test_case in test_cases:
            # testing format
            module_result_1 = instagram_valid.profile(test_case)

            special_keys = ['is_private', 'school', 'fb_page_call_to_action_id', 'has_anonymous_profile_picture',
                            'has_chaining', 'external_lynx_url', 'has_placed_orders', 'auto_expand_chaining',
                            'has_unseen_besties_media', 'include_direct_blacklist_status', 'has_highlight_reels',
                            "has_placed_url", "sub_type",
                            "has_biography_translation", "has_biography_translation", "is_business", "follower_count",
                            "following_count",
                            "business_contact_method", "category", "geo_media_count", "is_call_to_action_enabled", "pk",
                            "media_count",
                            "is_verified", "is_favorite", "is_eligible_for_school", "direct_messaging",
                            "reel_auto_archive", "usertags_count", "has_persistent_profile_school"]

            properties_keys = ['full_name', 'username', "city_name", "public_email", "public_phone_number",
                               "contact_phone_number", "external_url", "zip",
                               "address_street", "latitude", "longitude", "city_id", "biography"]

            # test show profile
            for each in module_result_1['special_properties']:
                for k in each.keys():
                    if k != 'type':
                        self.assertIn(k, special_keys)

            for each in module_result_1['properties']:
                for k in each.keys():
                    if k != 'type':
                        self.assertIn(k, properties_keys)


if __name__ == '__main__':
    unittest.main()
