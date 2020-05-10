import unittest
from lmatch import parse


class Parse(unittest.TestCase):
    def html_open(self, x):
        f = open(x)
        data = f.read()
        f.close()
        return data

    def setUp(self):
        self.page_following_1 = \
            self.html_open("tests/data/jlcordeiro_following_1.html")
        self.page_following_2 = \
            self.html_open("tests/data/jlcordeiro_following_2.html")

    def test_get_following_from_page(self):
        expected = ['dunkeey', 'gonfsilva', 'crispim',
                    'inesqsc', 'nihilism', 'carsonkims', 'o_serkan_o',
                    'davidehrlich', 'carolina_ab', 'nunoabreu', 'boppitybunny',
                    'apeloeh', 'wonderfulcinema', 'followtheblind', 'jkottke',
                    'sandwich', 'khoi', 'vishnevetsky', 'dmoren', 'pbones',
                    'emanuel', 'zkorpi', 'inesdelgado', 'faitherina', 'mpmont']
        self.assertEqual(expected,
                         parse.following(self.page_following_1))

        expected = ['siracusa']
        self.assertEqual(expected,
                         parse.following(self.page_following_2))

    def test_get_next_page(self):
        self.assertEqual("jlcordeiro/following/page/2/",
                         parse.next_page(self.page_following_1))

        self.assertEqual(None,
                         parse.next_page(self.page_following_2))

    def test_parse_movies(self):
        page = self.html_open("tests/data/jlcordeiro_watched_1.html")
        (movies, next_page) = parse.movies_watched(page)
        self.assertEquals("jlcordeiro/films/page/2/", next_page)

        page = self.html_open("tests/data/jlcordeiro_watched_3.html")
        (movies, next_page) = parse.movies_watched(page)
        self.assertEquals("jlcordeiro/films/page/4/", next_page)

        page = self.html_open("tests/data/jlcordeiro_watched_7.html")
        (movies, next_page) = parse.movies_watched(page)
        self.assertEquals(None, next_page)

        page = self.html_open("tests/data/tommyatlon_watched_1.html")
        (movies, next_page) = parse.movies_watched(page)
        self.assertEquals("tommyatlon/films/page/2/", next_page)

        self.assertEquals(("6-underground", 9), movies[0])
        self.assertEquals(("the-equalizer-2", 10), movies[-7])
        self.assertEquals(("jurassic-world-fallen-kingdom", 0), movies[-1])


if __name__ == '__main__':
    unittest.main()
