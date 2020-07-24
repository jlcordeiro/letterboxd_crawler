import sys
import json
import time
import argparse
import threading
from requests import session
from lmatch import profile_crawler, parse, dao, film


class MovieFacade:
    """
    Class to bridge movies between crawler and database layer.
    Inserts into DB if a movie has never been seen before.
    Caches the url -> id mapping.
    """
    def __init__(self):
        self.lock_ = threading.Lock()
        self.hash_table_ = {}

        def cacheOne(m):
            self.hash_table_[m.url] = int(m.id)
            print("Loaded ", m.url, " from db.")

        self.db_ = dao.MovieDao()
        self.db_.fetchAllMovies(lambda m: cacheOne(m))

    def getId(self, movie_url):
        with self.lock_:
            # if the url hasn't been found yet, get it.
            if movie_url not in self.hash_table_:
                film = parse.parse_film(get_page('/film/' + movie_url))
                self.db_.updateMovie(film)
                self.hash_table_[movie_url] = int(film.id)

            return self.hash_table_[movie_url]


movie_facade = MovieFacade()

s = session()
def get_page(path):
    print(":: ", path)
    base_url = "https://letterboxd.com/"
    return s.get(base_url + path).text


def crawl(profiles, profile, first_page, parser):
    result = []
    page_next = first_page
    while page_next is not None:
        if profiles.keep_parsing is False:
            return None

        try:
            page_text = get_page(page_next)
        except:
            return None

        result.extend(parser(page_text))
        page_next = parse.next_page(page_text)

    return result

def crawl_profile(profiles, source_profile):
    following = crawl(profiles, source_profile.username,
                      source_profile.username + "/following/page/1",
                      parse.following)

    movies = crawl(profiles, source_profile.username,
                   source_profile.username + "/films/page/1",
                   parse.movies_watched)

    if following and movies:

        movie_id_to_rating = {}
        for (url, rating) in movies:
            try:
                this_id = movie_facade.getId(url)
                movie_id_to_rating[this_id] = rating
            except:
                print("Failed to get: {}.".format(movie_url))

        profiles.on_parsed(source_profile.username, source_profile.depth,
                following, movie_id_to_rating)

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
            if not any([t.is_alive() for t in threads]):
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
