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
        movies = parse.movies_watched(page)
        next_page = parse.next_page(page)
        self.assertEqual("jlcordeiro/films/page/2/", next_page)

        page = self.html_open("tests/data/jlcordeiro_watched_3.html")
        movies = parse.movies_watched(page)
        next_page = parse.next_page(page)
        self.assertEqual("jlcordeiro/films/page/4/", next_page)

        page = self.html_open("tests/data/jlcordeiro_watched_7.html")
        movies = parse.movies_watched(page)
        next_page = parse.next_page(page)
        self.assertEqual(None, next_page)

        page = self.html_open("tests/data/tommyatlon_watched_1.html")
        movies = parse.movies_watched(page)
        next_page = parse.next_page(page)
        self.assertEqual("tommyatlon/films/page/2/", next_page)

        self.assertEqual(("6-underground", 9), movies[0])
        self.assertEqual(("the-equalizer-2", 10), movies[-7])
        self.assertEqual(("jurassic-world-fallen-kingdom", 0), movies[-1])

    def test_parse_film(self):
        page = self.html_open("tests/data/film_the-way-back-2020.html")
        film = parse.parse_film(page)

        self.assertEqual(film.id, 458743)
        self.assertEqual(film.url, "the-way-back-2020")
        self.assertEqual(film.name, "The Way Back")
        self.assertEqual(film.avg_rate, 6.78)


if __name__ == '__main__':
    unittest.main()
