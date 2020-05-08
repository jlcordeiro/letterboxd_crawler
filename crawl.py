import os
import re
import sys
import time
import queue
import argparse
from requests import session
from bs4 import BeautifulSoup
import threading

class Profile:
    def __init__(self, username, following = []):
        self.username  = username
        self.following = following

    def __hash__(self):
        return hash(self.username)

    def __eq__(self, other):
        return self.username == other.username

class Profiles:
    def __init__(self):
        self.lock_             = threading.Lock()
        self.parsed_profiles   = set()
        self.queued_usernames  = set()
        self.ongoing_usernames = set()

    def enqueue(self, username):
        with self.lock_:
            if Profile(username) not in self.parsed_profiles:
                self.queued_usernames.add(username)

    def on_parsed(self, username, following):
        for f in following:
            self.enqueue(f)

        p = Profile(username, following)
        with self.lock_:
            self.parsed_profiles.add(p)
            self.ongoing_usernames.discard(username)
            print("{} parsed. {} ongoing. {} queued.".format(len(self.parsed_profiles),
                                                             len(self.ongoing_usernames),
                                                             len(self.queued_usernames)))

    def next(self):
        with self.lock_:
            if len(self.queued_usernames) == 0:
                return None

            popped_username = self.queued_usernames.pop()
            self.ongoing_usernames.add(popped_username)
            return popped_username


def extract_following(soup):
    table = soup.find_all("td", attrs={"class": "table-person"})
    return [person.find("a", href=True)["href"][1 : -1] for person in table]


def extract_next_page(soup):
    pagination = soup.find_all("div", attrs={"class": "paginate-nextprev"})
    if len(pagination) is 0:
        return None

    pagination = pagination[-1].find("a", href=True)
    if pagination is None:
        return None

    return pagination["href"][1:]

s = session()
def crawl_network(profiles, source_profile):
    # note: this gets changed inside the loop
    page_next = source_profile + "/following/page/1"

    following = []
    while page_next is not None:
        base_url = "https://letterboxd.com/"
        r = s.get(base_url + page_next)
        soup = BeautifulSoup(r.text, "html.parser")

        following.extend(extract_following(soup))
        page_next = extract_next_page(soup)

    profiles.on_parsed(source_profile, following)

stop = False

class LbThread (threading.Thread):
    def __init__(self, profiles, thread_id):
        threading.Thread.__init__(self)
        self.profiles = profiles
        self.thread_id = thread_id

    def run(self):
        while stop is False:
            n = self.profiles.next()
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

    profiles = Profiles()
    profiles.enqueue(first_profile)

    threads = []
    for i in range(4):
        thread = LbThread(profiles, i + 1)
        thread.start()
        threads.append(thread)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("ASKED TO STOP!!!")
        stop = True

    for t in threads:
       t.join()
    print ("Exiting Main Thread")

if __name__ == "__main__":
    main(sys.argv[1:])
