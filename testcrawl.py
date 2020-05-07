import crawl
import unittest
from bs4 import BeautifulSoup

class Parse(unittest.TestCase):
    def setUp(self):
        def html_open(x):
            f = open(x)
            data = BeautifulSoup(f.read(), "html.parser")
            f.close()
            return data

        self.soup_jlcordeiro_following_1 = html_open("testdata/jlcordeiro_following_1.html")
        self.soup_jlcordeiro_following_2 = html_open("testdata/jlcordeiro_following_2.html")

    def test_get_following_from_page(self):
        expected = ['dunkeey', 'gonfsilva', 'crispim',
                    'inesqsc', 'nihilism', 'carsonkims', 'o_serkan_o',
                    'davidehrlich', 'carolina_ab', 'nunoabreu', 'boppitybunny',
                    'apeloeh', 'wonderfulcinema', 'followtheblind', 'jkottke',
                    'sandwich', 'khoi', 'vishnevetsky', 'dmoren', 'pbones',
                    'emanuel', 'zkorpi', 'inesdelgado', 'faitherina', 'mpmont']
        self.assertEqual(expected, crawl.extract_following(self.soup_jlcordeiro_following_1))

        expected = ['siracusa']
        self.assertEqual(expected, crawl.extract_following(self.soup_jlcordeiro_following_2))

if __name__ == '__main__':
    unittest.main()
