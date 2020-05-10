import unittest
from lmatch import parse

class Parse(unittest.TestCase):
    def setUp(self):
        def html_open(x):
            f = open(x)
            data = f.read()
            f.close()
            return data

        self.soup_jlcordeiro_following_1 = html_open("tests/data/jlcordeiro_following_1.html")
        self.soup_jlcordeiro_following_2 = html_open("tests/data/jlcordeiro_following_2.html")

    def test_get_following_from_page(self):
        expected = ['dunkeey', 'gonfsilva', 'crispim',
                    'inesqsc', 'nihilism', 'carsonkims', 'o_serkan_o',
                    'davidehrlich', 'carolina_ab', 'nunoabreu', 'boppitybunny',
                    'apeloeh', 'wonderfulcinema', 'followtheblind', 'jkottke',
                    'sandwich', 'khoi', 'vishnevetsky', 'dmoren', 'pbones',
                    'emanuel', 'zkorpi', 'inesdelgado', 'faitherina', 'mpmont']
        self.assertEqual(expected, parse.following(self.soup_jlcordeiro_following_1))

        expected = ['siracusa']
        self.assertEqual(expected, parse.following(self.soup_jlcordeiro_following_2))

    def test_get_next_page(self):
        self.assertEqual("jlcordeiro/following/page/2/",
                         parse.next_page(self.soup_jlcordeiro_following_1))

        self.assertEqual(None,
                         parse.next_page(self.soup_jlcordeiro_following_2))

if __name__ == '__main__':
    unittest.main()
