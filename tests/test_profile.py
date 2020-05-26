import unittest
from lmatch import profile_crawler
Profile = profile_crawler.Profile

class TestProfile(unittest.TestCase):
    def setUp(self):
        pass

    def test_ctor(self):
        p1 = Profile("j", 0)
        self.assertEqual(p1.username, "j")
        self.assertEqual(p1.following, None)
        self.assertEqual(p1.movies, None)

        p2 = Profile("j", 0, [], [])
        self.assertEqual(p2.username, "j")
        self.assertEqual(p2.following, [])
        self.assertEqual(p2.movies, [])

    def test_is_empty(self):
        p1 = Profile("j", 0)
        self.assertEqual(p1.isEmpty(), True)

        p2 = Profile("j", 0, [], [])
        self.assertEqual(p2.isEmpty(), False)
