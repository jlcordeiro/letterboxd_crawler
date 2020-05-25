import unittest
from lmatch import profile_crawler

class Profile(unittest.TestCase):
    def setUp(self):
        pass

    def test_ctor(self):
        p1 = profile_crawler.Profile("j")
        self.assertEqual(p1.username, "j")
        self.assertEqual(p1.following, None)
        self.assertEqual(p1.movies, None)

        p2 = profile_crawler.Profile("j", [], [])
        self.assertEqual(p2.username, "j")
        self.assertEqual(p2.following, [])
        self.assertEqual(p2.movies, [])

    def test_is_empty(self):
        p1 = profile_crawler.Profile("j")
        self.assertEqual(p1.isEmpty(), True)

        p2 = profile_crawler.Profile("j", [], [])
        self.assertEqual(p2.isEmpty(), False)
