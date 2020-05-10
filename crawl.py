import sys
import json
import time
import argparse
import threading
from requests import session
from lmatch import profile_crawler, parse

s = session()
def crawl_network(profiles, source_profile):
    # note: this gets changed inside the loop
    page_next = source_profile + "/following/page/1"

    following = []
    while page_next is not None:
        if profiles.keep_parsing is False:
            return

        base_url = "https://letterboxd.com/"
        r = s.get(base_url + page_next)

        following.extend(parse.following(r.text))
        page_next = parse.next_page(r.text)

    profiles.on_parsed(source_profile, following)

class LbThread (threading.Thread):
    def __init__(self, profiles, thread_id):
        threading.Thread.__init__(self)
        self.profiles = profiles
        self.thread_id = thread_id

    def run(self):
        while self.profiles.keep_parsing is True:
            n = self.profiles.next_job()
            if n is None:
                time.sleep(.5)
            else:
                crawl_network(self.profiles, n)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "letterboxd_url",
        metavar="LETTERBOXD_PROFILE",
        help="URL of your letterboxd profile",
    )
    args = parser.parse_args(argv)
    first_profile = args.letterboxd_url

    crawler = profile_crawler.ProfileCrawler()

    dump_filename = 'dump.lmatch'
    try:
        with open(dump_filename, 'r') as infile:
            print("Loading previous state.")
            str = infile.read()
            crawler.loads(str)
            infile.close()
            print("State successfully loaded.")
    except FileNotFoundError:
        crawler.enqueue(first_profile)

    threads = []
    for i in range(4):
        thread = LbThread(crawler, i + 1)
        thread.start()
        threads.append(thread)

    try:
        while True:
            print("{} parsed. {} ongoing. {} queued.".format(len(crawler.parsed_profiles),
                                                             len(crawler.ongoing_usernames),
                                                             len(crawler.queued_usernames)))
            time.sleep(10)
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
