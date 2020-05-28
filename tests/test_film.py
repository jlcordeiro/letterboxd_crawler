import unittest
from lmatch import film

class TestFilm(unittest.TestCase):
    def setUp(self):
        self.sample_film = film.Film(412, "path_that", "name_this", 5.21)

    def test_ctor(self):
        self.assertEqual(self.sample_film.id, 412)
        self.assertEqual(self.sample_film.name, "name_this")
        self.assertEqual(self.sample_film.url, "path_that")
        self.assertEqual(self.sample_film.avg_rate, 5.21)

    def test_hash(self):
        self.assertEqual(hash(self.sample_film), 412)

    def test_eq(self):
        f1 = film.Film(412, "a", "b", 1.0)
        f2 = film.Film(411, "a", "b", 1.0)
        self.assertEqual(True, f1 == self.sample_film)
        self.assertEqual(False, f2 == self.sample_film)

    def test_repr(self):
        self.assertEqual(repr(self.sample_film), "name_this")
