import os
import re
import sys
import json
import time
import queue
import argparse
from requests import session
import threading

class Profile:
    """
    Class that contains all the data relative to a
    Letterboxd profile / account.
    """
    def __init__(self, username, following = []):
        self.username  = username
        self.following = following

    def __hash__(self):
        return hash(self.username)

    def __eq__(self, other):
        return self.username == other.username

class ProfileCrawler:
    """
    Class that wraps the logic behind crawling Letterboxd. Maintains
    several sets of usernames / profiles:
        - parsed profiles (profiles that have been fully parsed)
        - ongoing profiles (actively being parsed)
        - queued profiles (waiting for a free thread)

    This class is thread-safe.
    """
    def __init__(self):
        self.lock_             = threading.Lock()
        self.parsed_profiles   = set()
        self.queued_usernames  = set()
        self.ongoing_usernames = set()
        self.keep_parsing      = True

    def stop_parsing(self):
        """ Flag to anyone using the crawler that they should stop. """
        with self.lock_:
            self.keep_parsing = False

    def cancel_ongoing_jobs(self):
        """
        Move all jobs / profiles being parsed back to the queue. Whatever
        was already parsed is lost.
        Should be used to guaranteed a return to a known state where
        all profiles are either fully parsed or waiting to be picked up.
        """
        with self.lock_:
            while len(self.ongoing_usernames):
                cancelled_username = self.ongoing_usernames.pop()
                self.queued_usernames.add(cancelled_username)

    def enqueue(self, username):
        """
        Adds a user name to the list of profiles to be queued and processed
        later. If this profile has been parsed in the past, the method
        will just ignore it silently.
        """
        with self.lock_:
            if username not in self.ongoing_usernames \
                and Profile(username) not in self.parsed_profiles:
                self.queued_usernames.add(username)

    def on_parsed(self, username, following):
        """
        This method creates a profile with the details passed as parameter.
        The profile is put on the list of parsed profiles and its
        username is removed from the list of ongoing jobs.

        Any other users that are seen in the details of this profiles
        (following, follower, etc), if never seen before, are adding to the 
        queue to be processed in the future.
        """
        for f in following:
            self.enqueue(f)

        p = Profile(username, following)
        with self.lock_:
            self.parsed_profiles.add(p)
            self.ongoing_usernames.discard(username)

    def next_job(self):
        """
        Get a "random" job out of the queue of profiles. If there are
        no profiles waiting, returns None.

        Warning: this profile is immediately removed from
        queued and moved to ongoing, despite of whether or not
        the client does something with it.
        """
        with self.lock_:
            if len(self.queued_usernames) == 0:
                return None

            popped_username = self.queued_usernames.pop()
            self.ongoing_usernames.add(popped_username)
            return popped_username

    def dump(self):
        """ Dump the whole internal stte as a dictionary. """
        return {"parsed": [(p.username, p.following) for p in self.parsed_profiles],
                "queued": list(self.queued_usernames),
                "ongoing": list(self.ongoing_usernames)}

    def loads(self, str):
        """ Load state from a string. """
        d = json.loads(str)
        self.queued_usernames = set(d["queued"])
        self.ongoing_usernames = set(d["ongoing"])

        for p in d["parsed"]:
            self.parsed_profiles.add(Profile(p[0], p[1]))


def extract_value(str, key, start):
    start = str.find(key, start) + len(key)
    end = str.find("\"", start)
    return (start, end, str[start : end])

def extract_next_page(str):
    key_page_next = "\"next\" href=\""

    start = str.rfind("paginate-nextprev")
    start = str.find(key_page_next, start)
    if start is -1:
        return None

    start += len(key_page_next)
    end_idx = str.find("\"", start)
    return str[start + 1 : end_idx]

def extract_following(page):
    following = []

    start = 1
    while start > 0:
        start = page.find("table-person", start)
        if start > 0:
            (start, _, followed) = extract_value(page, "href=\"", start)
            following.append(followed[1 : -1])

    return following

def extract_movies(page_contents):
    movies = []

    start = 1
    while start > 0:
        start = page_contents.find("poster-container", start)
        if start > 0:
            (start, _, movie_name) = extract_value(page_contents, "data-target-link=\"/film/", start)
            (_, start, movie_rate) = extract_value(page_contents, " rated-", start)

            movies.append((movie_name[:-1], int(movie_rate)))


    page_next = extract_next_page(page_contents)

    return (movies, page_next)

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

        following.extend(extract_following(r.text))
        page_next = extract_next_page(r.text)

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

    crawler = ProfileCrawler()

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
