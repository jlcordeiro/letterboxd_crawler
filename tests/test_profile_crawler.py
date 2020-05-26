import json
import unittest
from lmatch import profile_crawler
Profile = profile_crawler.Profile


class ProfileCrawler(unittest.TestCase):
    def setUp(self):
        pass

    def test_ctor(self):
        c = profile_crawler.ProfileCrawler()
        self.assertEqual(0, len(c.parsed_))
        self.assertEqual(0, len(c.queued_))
        self.assertEqual(0, len(c.ongoing_usernames))
        self.assertEqual(True, c.keep_parsing)

    def test_stop(self):
        c = profile_crawler.ProfileCrawler()
        self.assertEqual(True, c.keep_parsing)
        c.stop_parsing()
        self.assertEqual(False, c.keep_parsing)
        c.stop_parsing()
        self.assertEqual(False, c.keep_parsing)

    def test_cancel_ongoing(self):
        c = profile_crawler.ProfileCrawler()
        c.parsed_ = {1, 2, 3}  # put some junk in
        c.ongoing_usernames = {"a", "b", "c"}
        c.queued_ = {Profile("d"), Profile("e"), Profile("f")}

        c.cancel_ongoing_jobs()

        # checked that the profiles already parsed don't get affected
        self.assertEqual(3, len(c.parsed_))
        self.assertTrue({1, 2, 3}, c.parsed_)

        # all ongoing jobs should be gone...
        self.assertEqual(0, len(c.ongoing_usernames))

        # ... and moved to queued
        self.assertEqual(6, len(c.queued_))
        self.assertEqual({Profile("a"), Profile("b"), Profile("c"),
            Profile("d"), Profile("e"), Profile("f")}, c.queued_)

    def test_enqueue(self):
        c = profile_crawler.ProfileCrawler()

        a_profile = profile_crawler.Profile("joe")
        c.parsed_ = {a_profile}

        # check that a new username is added to the queue
        c.enqueue("jack")
        self.assertEqual({Profile("jack")}, c.queued_)
        c.enqueue("john")
        c.enqueue("jess")
        self.assertEqual({Profile("john"), Profile("jess"), Profile("jack")}, c.queued_)
        # but one that was seen before isn't
        c.enqueue("joe")  # same as put on the set of parsed profiles
        self.assertEqual({Profile("john"), Profile("jess"), Profile("jack")}, c.queued_)
        # and just adding one that exists in the queue, obviously does nothing
        c.enqueue("john")
        c.enqueue("jess")
        self.assertEqual({Profile("john"), Profile("jess"), Profile("jack")}, c.queued_)

    def test_next_job(self):
        c = profile_crawler.ProfileCrawler()

        c.enqueue("p1")
        c.enqueue("p2")
        c.enqueue("p3")

        # quick sanity check
        self.assertEqual(3, len(c.queued_))
        self.assertEqual(0, len(c.ongoing_usernames))

        job1 = c.next_job()
        self.assertEqual({job1}, c.ongoing_usernames)
        self.assertTrue(job1 not in c.queued_)

        job2 = c.next_job()
        self.assertTrue(job1 not in c.queued_)
        self.assertTrue(job2 not in c.queued_)
        self.assertEqual({job1, job2}, c.ongoing_usernames)

        job3 = c.next_job()
        self.assertTrue(job1 not in c.queued_)
        self.assertTrue(job2 not in c.queued_)
        self.assertTrue(job3 not in c.queued_)
        self.assertEqual({job1, job2, job3}, c.ongoing_usernames)

        self.assertEqual(0, len(c.queued_))
        self.assertEqual(3, len(c.ongoing_usernames))
        self.assertEqual(None, c.next_job())

    def test_on_parsed(self):
        # setup
        c = profile_crawler.ProfileCrawler()
        c.parsed_ = {profile_crawler.Profile("parsed1"),
                             profile_crawler.Profile("parsed2"),
                             profile_crawler.Profile("parsed3")}
        c.ongoing_usernames = {"ongoing1", "ongoing2"}
        c.queued_ = {"q1", "q2", "q3"}

        c.on_parsed("ongoing2",
                    ["newp1", "newp2", "newp3", "parsed2",
                        "ongoing1", "ongoing2"],
                    [])

        # ongoing2 should have been moved to parsed. ongoing 1 remains
        self.assertTrue("ongoing1" in c.ongoing_usernames)
        self.assertTrue("ongoing2" not in c.ongoing_usernames)
        self.assertTrue(profile_crawler.Profile("ongoing2")
                        in c.parsed_)

        # other users seen should be queued
        self.assertTrue(Profile("newp1") in c.queued_)
        self.assertTrue(Profile("newp3") in c.queued_)
        # unless they've been parsed already
        self.assertTrue(Profile("parsed2") not in c.queued_)
        # or even on one of the other sets
        self.assertTrue(Profile("ongoing1") not in c.queued_)
        self.assertTrue(Profile("ongoing2") not in c.queued_)

    def test_laod(self):
        c = profile_crawler.ProfileCrawler()
        c.loads("""
        {
          "parsed": [
            [
              "carolina_ab",
              [
                "inesgoncalves",
                "nunoabreu",
                "inesdelgado",
                "jlcordeiro"
              ],
              []
            ],
            [
              "jlcordeiro",
              [
                "dunkeey",
                "gonfsilva",
                "nihilism",
                "siracusa"
              ],
              [
                ["extraction-2020", 6 ],
                [ "sinister", 6 ],
                [ "breathless", 0 ]
              ]
            ]
          ],
          "queued": [
            ["ingridgoeswest", null, null],
            ["gonfsilva", null, null],
            ["kika", null, null],
            ["flacerda", null, null]
          ],
          "ongoing": []
        }
        """)

        self.assertEqual(set(), c.ongoing_usernames)
        self.assertEqual({Profile("ingridgoeswest"), Profile("gonfsilva"),
            Profile("kika"), Profile("flacerda")},
                         c.queued_)

        self.assertEqual(2, len(c.parsed_))
        self.assertTrue(profile_crawler.Profile("carolina_ab")
                        in c.parsed_)
        self.assertTrue(profile_crawler.Profile("jlcordeiro")
                        in c.parsed_)

        def check_profile(profile):
            if profile.username == "jlcordeiro":
                self.assertEqual(
                        {"dunkeey", "gonfsilva", "nihilism", "siracusa"},
                        set(profile.following))
                self.assertEqual( [['extraction-2020', 6], ['sinister', 6], ['breathless', 0]], profile.movies)
            else:
                self.assertEqual(
                  {"inesgoncalves", "nunoabreu", "inesdelgado", "jlcordeiro"},
                  set(profile.following))
                self.assertEqual([], profile.movies)

        check_profile(c.parsed_.pop())
        check_profile(c.parsed_.pop())

    def test_dump(self):
        c = profile_crawler.ProfileCrawler()
        c.enqueue("p1")
        c.enqueue("p2")
        c.enqueue("p3")

        d = c.dump()

        self.assertEqual([], d["parsed"])
        self.assertEqual([], d["ongoing"])

        self.assertEqual({"p1", "p2", "p3"}, set([p[0] for p in d["queued"]]))

        c.on_parsed("p4", ["p1", "p2"], [])
        d = c.dump()

        self.assertEqual(1, len(d["parsed"]))
        self.assertEqual("p4", d["parsed"][0][0])
        self.assertEqual({"p1", "p2"}, set(d["parsed"][0][1]))
        self.assertEqual([], d["ongoing"])
        self.assertEqual({"p1", "p2", "p3"}, set([p[0] for p in d["queued"]]))


if __name__ == '__main__':
    unittest.main()
