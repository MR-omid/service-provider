import unittest
from modules.twitter.v_1_0.twitter import Twitter
from vendor.custom_exception import ResultNotFoundError, InvalidInputError


class TestTwitter(unittest.TestCase):
    valid_key = {"consumer_key": "FVwtwnnQhkecUTnbnfxeGbHYJ",
                 "consumer_secret": "y6tvwIIXbvGF6McaZuvgkaFqcZAnJHm3NOnWale6XxUWgHgC3X",
                 "access_key": "922436153638359040-gSnTdp9l10sPEUGQjbctNAMe5SMAWSb",
                 "access_secret": "jFA2kjmEXsvfdkmHGw4AdibIkGExNNT6qWHnsSytPuUd8"}

    # testing invalid keys and notfounderror
    def test_unauthorized_consumer(self):
        # define invalid value
        consumer_key = 'invalid'
        consumer_secret = 'invalid'
        access_key = 'invalid'
        access_secret = 'invalid'

        tweeter_1 = Twitter(consumer_key, TestTwitter.valid_key['consumer_secret'], TestTwitter.valid_key['access_key'],
                            TestTwitter.valid_key['access_secret'])
        tweeter_2 = Twitter(TestTwitter.valid_key['consumer_key'], consumer_secret, TestTwitter.valid_key['access_key'],
                            TestTwitter.valid_key['access_secret'])
        tweeter_3 = Twitter(TestTwitter.valid_key['consumer_key'], TestTwitter.valid_key['consumer_secret'], access_key,
                            TestTwitter.valid_key['access_secret'])
        tweeter_4 = Twitter(TestTwitter.valid_key['consumer_key'], TestTwitter.valid_key['consumer_secret'],
                            TestTwitter.valid_key['access_key'], access_secret)
        tweeter_valid = Twitter(TestTwitter.valid_key['consumer_key'], TestTwitter.valid_key['consumer_secret'],
                                TestTwitter.valid_key['access_key'], TestTwitter.valid_key['access_secret'])
        # testing invalid keys
        with self.assertRaises(InvalidInputError):
            tweeter_1.search(query='football', count=None)
            tweeter_1.follower_list(user_id='football', count=None)
            tweeter_1.friends_list(user_id='football', count=None)
            tweeter_1.show_user(user_id='football')
        # testing invalid keys
        with self.assertRaises(InvalidInputError):
            tweeter_2.search(query='football', count=None)
            tweeter_2.follower_list(user_id='football', count=None)
            tweeter_2.friends_list(user_id='football', count=None)
            tweeter_2.show_user(user_id='football')
        # testing invalid keys
        with self.assertRaises(InvalidInputError):
            tweeter_3.search(query='football', count=None)
            tweeter_3.follower_list(user_id='football', count=None)
            tweeter_3.friends_list(user_id='football', count=None)
            tweeter_3.show_user(user_id='football')
        # testing invalid keys
        with self.assertRaises(InvalidInputError):
            tweeter_4.search(query='football', count=None)
            tweeter_4.follower_list(user_id='football', count=None)
            tweeter_4.friends_list(user_id='football', count=None)
            tweeter_4.show_user(user_id='football')

        # testing notfounderror
        with self.assertRaises(ResultNotFoundError):
            tweeter_valid.search(query='adsfvasfgverwfgawefvefklfnklweamnfawfmlawemfklfnklwae', count=None)
            tweeter_valid.friends_list(user_id='adsfvasfgverwfgawefvefklfnklweamnfawfmlawemfklfnklwae', count=None)
            tweeter_valid.follower_list(user_id='adsfvasfgverwfgawefvefklfnklweamnfawfmlawemfklfnklwae', count=None)
            tweeter_valid.show_user(user_id='adsfvasfgverwfgawefvefklfnklweamnfawfmlawemfklfnklwae')

        test_cases = ['football', 'soccer', 'sony', 'msi', 'bmw']
        for test_case in test_cases:
            # testing format
            module_result_1 = tweeter_valid.show_user(test_case)
            module_result_2 = tweeter_valid.follower_list(test_case)['results'][-1]
            module_result_3 = tweeter_valid.friends_list(test_case)['results'][-1]
            module_result_4 = tweeter_valid.search(test_case, None)['results'][-1]

            special_keys = ["sub_type", "screen_name", "location", "verified", "followers_count", "friends_count",
                            "protected", "listed_count", "favourites_count", "statuses_count", "created_at",
                            "geo_enabled",
                            "lang", "contributors_enabled", "profile_background_image_url", "profile_banner_url",
                            "profile_image_url"]
            result_keys = ['domain']
            properties_keys = ['name', 'description', 'url']

            # test show user
            for each in module_result_1['special_properties']:
                for k in each.keys():
                    if k != 'type':
                        self.assertIn(k, special_keys)

            for each in module_result_1['result']:
                for k in each.keys():
                    if k != 'type':
                        self.assertIn(k, result_keys)
            for each in module_result_1['properties']:
                for k in each.keys():
                    if k != 'type':
                        self.assertIn(k, properties_keys)

            # test friedns list
            for each in module_result_2['special_properties']:
                for k in each.keys():
                    if k != 'type':
                        self.assertIn(k, special_keys)

            for each in module_result_2['properties']:
                for k in each.keys():
                    if k != 'type':
                        self.assertIn(k, properties_keys)

            # test follower list
            for each in module_result_3['special_properties']:
                for k in each.keys():
                    if k != 'type':
                        self.assertIn(k, special_keys)

            for each in module_result_3['properties']:
                for k in each.keys():
                    if k != 'type':
                        self.assertIn(k, properties_keys)

            # test search list
            for each in module_result_4['special_properties']:
                for k in each.keys():
                    if k != 'type':
                        self.assertIn(k, special_keys)

            for each in module_result_4['properties']:
                for k in each.keys():
                    if k != 'type':
                        self.assertIn(k, properties_keys)


if __name__ == '__main__':
    unittest.main()
