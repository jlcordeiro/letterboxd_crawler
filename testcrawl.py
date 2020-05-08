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

    def test_get_next_page(self):
        self.assertEqual("jlcordeiro/following/page/2/",
                         crawl.extract_next_page(self.soup_jlcordeiro_following_1))

        self.assertEqual(None,
                         crawl.extract_next_page(self.soup_jlcordeiro_following_2))

class Crawler(unittest.TestCase):
    def setUp(self):
        pass

    def test_ctor(self):
        c = crawl.ProfileCrawler()
        self.assertEqual(0, len(c.parsed_profiles))
        self.assertEqual(0, len(c.queued_usernames))
        self.assertEqual(0, len(c.ongoing_usernames))
        self.assertEqual(True, c.keep_parsing)

    def test_stop(self):
        c = crawl.ProfileCrawler()
        self.assertEqual(True, c.keep_parsing)
        c.stop_parsing()
        self.assertEqual(False, c.keep_parsing)
        c.stop_parsing()
        self.assertEqual(False, c.keep_parsing)

    def test_cancel_ongoing(self):
        c = crawl.ProfileCrawler()
        c.parsed_profiles = {1, 2, 3} #put some junk in
        c.ongoing_usernames = {"a", "b", "c"}
        c.queued_usernames = {"d", "e", "f"}

        c.cancel_ongoing_jobs()

        # checked that the profiles already parsed don't get affected
        self.assertEqual(3, len(c.parsed_profiles))
        self.assertTrue({1, 2, 3}, c.parsed_profiles)

        # all ongoing jobs should be gone...
        self.assertEqual(0, len(c.ongoing_usernames))

        # ... and moved to queued
        self.assertEqual(6, len(c.queued_usernames))
        self.assertEqual({"a", "b", "c", "d", "e", "f"}, c.queued_usernames)

    def test_enqueue(self):
        c = crawl.ProfileCrawler()

        a_profile = crawl.Profile("joe")
        c.parsed_profiles = {a_profile}

        # check that a new username is added to the queue
        c.enqueue("jack")
        self.assertEqual({"jack"}, c.queued_usernames)
        c.enqueue("john")
        c.enqueue("jess")
        self.assertEqual({"john", "jess", "jack"}, c.queued_usernames)
        # but one that was seen before isn't
        c.enqueue("joe") # same as put on the set of parsed profiles
        self.assertEqual({"john", "jess", "jack"}, c.queued_usernames)
        # and just adding something that exists in the queue, obviously does nothing
        c.enqueue("john")
        c.enqueue("jess")
        self.assertEqual({"john", "jess", "jack"}, c.queued_usernames)

    def test_next_job(self):
        c = crawl.ProfileCrawler()

        c.enqueue("p1")
        c.enqueue("p2")
        c.enqueue("p3")

        # quick sanity check
        self.assertEqual(3, len(c.queued_usernames))
        self.assertEqual(0, len(c.ongoing_usernames))

        job1 = c.next_job()
        self.assertEqual({job1}, c.ongoing_usernames)
        self.assertTrue(job1 not in c.queued_usernames)

        job2 = c.next_job()
        self.assertTrue(job1 not in c.queued_usernames)
        self.assertTrue(job2 not in c.queued_usernames)
        self.assertEqual({job1, job2}, c.ongoing_usernames)

        job3 = c.next_job()
        self.assertTrue(job1 not in c.queued_usernames)
        self.assertTrue(job2 not in c.queued_usernames)
        self.assertTrue(job3 not in c.queued_usernames)
        self.assertEqual({job1, job2, job3}, c.ongoing_usernames)

        self.assertEqual(0, len(c.queued_usernames))
        self.assertEqual(3, len(c.ongoing_usernames))
        self.assertEqual(None, c.next_job())

    def test_on_parsed(self):
        # setup
        c = crawl.ProfileCrawler()
        c.parsed_profiles = {crawl.Profile("parsed1"),
                             crawl.Profile("parsed2"),
                             crawl.Profile("parsed3")}
        c.ongoing_usernames = {"ongoing1", "ongoing2"}
        c.queued_usernames = {"q1", "q2", "q3"}

        c.on_parsed("ongoing2", ["newp1", "newp2", "newp3", "parsed2"])

        # ongoing2 should have been moved to parsed. ongoing 1 remains
        self.assertTrue("ongoing1" in c.ongoing_usernames)
        self.assertTrue("ongoing2" not in c.ongoing_usernames)
        self.assertTrue(crawl.Profile("ongoing2") in c.parsed_profiles)

        # other users seen should be queued
        self.assertTrue("newp1" in c.queued_usernames)
        self.assertTrue("newp3" in c.queued_usernames)
        # unless they've been parsed already
        self.assertTrue("parsed2" not in c.queued_usernames)


if __name__ == '__main__':
    unittest.main()
