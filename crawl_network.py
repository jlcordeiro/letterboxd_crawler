import os
import re
import sys
import time
import queue
import argparse
from requests import session
from bs4 import BeautifulSoup
import threading

base_url = "https://letterboxd.com/"

class Profiles:
    def __init__(self):
        self.lock_                   = threading.Lock()
        self.profiles_               = {}
        self.queue_                  = queue.Queue()
        self.total_profiles_         = 0
        self.profiles_left_to_parse_ = 0

    def add(self, p):
        with self.lock_:
            if p not in self.profiles_:
                self.queue_.put(p)
                self.profiles_[p]            = []
                self.total_profiles_         += 1
                self.profiles_left_to_parse_ += 1

    def update(self, p, following):
        with self.lock_:
            self.profiles_[p].extend(following)
            #print("{}: {}".format(p, following))

    def next(self):
        with self.lock_:
            if self.queue_.empty():
                return None
            self.profiles_left_to_parse_ -= 1
            return self.queue_.get()

    def peek(self):
        with self.lock_:
            print("{} out of {} profiles left to parse".format(self.profiles_left_to_parse_, self.total_profiles_))

    def show(self):
        with self.lock_:
            for k in self.profiles_:
                if (self.profiles_[k]):
                    print("{}: {}".format(k, self.profiles_[k]))
        print("-----------------------------")


def crawl_network(profiles, source_profile):
    profiles.add(source_profile)

    # note: this gets changed inside the loop
    page_next = source_profile + "/following/page/1"

    while True:
        watchlist_url = base_url + page_next
        #print(watchlist_url)

        # Get first page, gather general data
        s = session()
        r = s.get(watchlist_url)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("person-table")
        table = soup.find_all("td", attrs={"class": "table-person"})

        following = []
        for person in table:
            username = person.find("a", href=True)["href"][1 : -1]
            following.append(username)

        profiles.update(source_profile, following)
        for f in following:
            profiles.add(f)

        pagination = soup.find_all("div", attrs={"class": "paginate-nextprev"})
        if len(pagination) is 0:
            break

        pagination = pagination[-1].find("a", href=True)
        if pagination is None:
            break

        page_next = pagination["href"][1:]

stop = False

class LbThread (threading.Thread):
    def __init__(self, profiles):
        threading.Thread.__init__(self)
        self.profiles = profiles

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
    profiles.add(first_profile)

    threads = []
    for i in range(4):
        thread = LbThread(profiles)
        thread.start()
        threads.append(thread)

    try:
        while True:
            time.sleep(1)
            profiles.peek()
            profiles.show()
    except KeyboardInterrupt:
        stop = True

    for t in threads:
       t.join()
    print ("Exiting Main Thread")
    profiles.show()

main(sys.argv[1:])
