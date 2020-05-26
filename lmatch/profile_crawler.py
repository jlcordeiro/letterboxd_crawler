import json
import threading
from typing import Dict, List, Set, Union

class Profile:
    """
    Class that contains all the data relative to a
    Letterboxd profile / account.
    """
    def __init__(self, username: str,
            following: List[str] = None,
            movies: List[str] = None):

        self.username = username
        self.following = following
        self.movies = movies

    def isEmpty(self) -> bool:
        """ Check whether or not the profile is empty / not parsed. """
        return self.following is None or self.movies is None

    def __hash__(self):
        return hash(self.username)

    def __eq__(self, other):
        return self.username == other.username

    def __repr__(self):
        return (self.username)

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
        self.parsed_profiles: Set[Profile] = set()
        self.queued_: Set[Profile] = set()
        self.ongoing_usernames: Set[str] = set()
        self.keep_parsing = True

    def stop_parsing(self) -> None:
        """ Flag to anyone using the crawler that they should stop. """
        with self.lock_:
            self.keep_parsing = False

    def cancel_ongoing_jobs(self) -> None:
        """
        Move all jobs / profiles being parsed back to the queue. Whatever
        was already parsed is lost.
        Should be used to guaranteed a return to a known state where
        all profiles are either fully parsed or waiting to be picked up.
        """
        with self.lock_:
            while len(self.ongoing_usernames):
                cancelled_username = self.ongoing_usernames.pop()
                self.queued_.add(Profile(cancelled_username))

    def enqueue(self, username: str) -> None:
        """
        Adds a user name to the list of profiles to be queued and processed
        later. If this profile has been parsed in the past, the method
        will just ignore it silently.
        """
        with self.lock_:
            if username not in self.ongoing_usernames \
                    and Profile(username) not in self.parsed_profiles:
                self.queued_.add(Profile(username))

    def on_parsed(self, username: str, following: List[str],
            movies: List[str]) -> None:
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

    def next_job(self) -> Union[None, str]:
        """
        Get a "random" job out of the queue of profiles. If there are
        no profiles waiting, returns None.

        Warning: this profile is immediately removed from
        queued and moved to ongoing, despite of whether or not
        the client does something with it.
        """
        with self.lock_:
            if len(self.queued_) == 0:
                return None

            popped_username = self.queued_.pop().username
            self.ongoing_usernames.add(popped_username)
            return popped_username

    def dump(self) -> Dict:
        """ Dump the whole internal stte as a dictionary. """
        def repr_set(s):
            return  [(p.username, p.following, p.movies) for p in s]

        return {"parsed": repr_set(self.parsed_profiles),
                "queued": repr_set(self.queued_),
                "ongoing": list(self.ongoing_usernames)}

    def loads(self, data: str) -> None:
        """ Load state from a string. """
        d = json.loads(data)
        self.queued_ = set()
        for p in d["queued"]:
            self.queued_.add(Profile(p[0], p[1], p[2]))
        self.ongoing_usernames = set(d["ongoing"])

        for p in d["parsed"]:
            self.parsed_profiles.add(Profile(p[0], p[1], p[2]))
