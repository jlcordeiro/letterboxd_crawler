import json
import threading


class Profile:
    """
    Class that contains all the data relative to a
    Letterboxd profile / account.
    """
    def __init__(self, username, following=None, movies=None):
        self.username = username
        self.following = following
        self.movies = movies

    def isEmpty(self):
        return self.following is None or self.movies is None

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
        self.lock_ = threading.Lock()
        self.parsed_profiles = set()
        self.queued_usernames = set()
        self.ongoing_usernames = set()
        self.keep_parsing = True

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

    def on_parsed(self, username, following, movies):
        """
        This method creates a profile with the details passed as parameter.
        The profile is put on the list of parsed profiles and its
        username is removed from the list of ongoing jobs.

        Any other users that are seen in the details of this profiles
        - following, follower, etc) - if never seen before, are adding to the
        queue to be processed in the future.
        """
        for f in following:
            self.enqueue(f)

        p = Profile(username, following, movies)
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
        return {"parsed": [(p.username, p.following, p.movies)
                           for p in self.parsed_profiles],
                "queued": list(self.queued_usernames),
                "ongoing": list(self.ongoing_usernames)}

    def loads(self, str):
        """ Load state from a string. """
        d = json.loads(str)
        self.queued_usernames = set(d["queued"])
        self.ongoing_usernames = set(d["ongoing"])

        for p in d["parsed"]:
            self.parsed_profiles.add(Profile(p[0], p[1], p[2]))
