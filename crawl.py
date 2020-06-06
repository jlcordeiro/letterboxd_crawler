import sys
import json
import time
import argparse
import threading
from requests import session
from lmatch import profile_crawler, parse

s = session()

def crawl(profiles, profile, first_page, parser):
    base_url = "https://letterboxd.com/"
    result = []
    page_next = first_page
    while page_next is not None:
        if profiles.keep_parsing is False:
            return None

        r = s.get(base_url + page_next)
        result.extend(parser(r.text))
        page_next = parse.next_page(r.text)

    return result

def crawl_profile(profiles, source_profile):
    following = crawl(profiles, source_profile.username,
                      source_profile.username + "/following/page/1",
                      parse.following)

    movies = crawl(profiles, source_profile.username,
                   source_profile.username + "/films/page/1",
                   parse.movies_watched)

    if following and movies:
        movies_dict = {k: v for (k, v) in movies}
        profiles.on_parsed(source_profile.username, source_profile.depth,
                following, movies_dict)

class LbThread (threading.Thread):
    def __init__(self, profiles, thread_id, max_depth = None):
        threading.Thread.__init__(self)
        self.profiles = profiles
        self.thread_id = thread_id
        self.max_depth = max_depth

    def run(self):
        while self.profiles.keep_parsing is True:
            profile = self.profiles.next_job()
            if profile is None:
                time.sleep(.5)
            elif profile.depth > self.max_depth:
                return
            else:
                crawl_profile(self.profiles, profile)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "first_profile",
        metavar="LETTERBOXD_PROFILE",
        help="username of the profile to use as the top of the crawl tree",
    )
    args = parser.parse_args(argv)

    crawler = profile_crawler.ProfileCrawler()

    dump_filename = 'dump.lmatch'
    try:
        with open(dump_filename, 'r') as infile:
            crawler.loads(infile.read())
            infile.close()
    except FileNotFoundError:
        crawler.enqueue(args.first_profile)

    threads = []
    for i in range(40):
        thread = LbThread(crawler, i + 1, 3)
        thread.start()
        threads.append(thread)

    try:
        while True:
            print("{} parsed. {} ongoing. {} queued.".format(len(crawler.parsed_),
                                                             len(crawler.ongoing_),
                                                             len(crawler.queued_)))
            time.sleep(10)

            # all threads stopped
            if not any([t.isAlive() for t in threads]):
                print("Ended successfully.")
                break
    except KeyboardInterrupt:
        crawler.stop_parsing()

    print("Waiting for ongoing threads")
    for t in threads:
       t.join()

    print("Moving ongoing jobs back to queued")
    crawler.cancel_ongoing_jobs()

    print("Saving state to persistence layer")
    with open(dump_filename, 'w') as outfile:
        json.dump(crawler.dump(), outfile)


    print ("Exiting Main Thread")


if __name__ == "__main__":
    main(sys.argv[1:])
