import json
import threading
from typing import Dict, List, Set, Union, Tuple


class Profile:
    """
    Class that contains all the data relative to a
    Letterboxd profile / account.
    """

    def __init__(self,
                 username: str,
                 depth: int = 0,
                 following: List[str] = None,
                 movies: Dict[str, int] = None):

        self.username = username
        self.depth = depth
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
        self.parsed_: Set[Profile] = set()
        self.queued_: Set[Profile] = set()
        self.ongoing_: Set[Profile] = set()
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
            while len(self.ongoing_):
                self.queued_.add(self.ongoing_.pop())

    def enqueue(self, username: str, depth: int = 0) -> None:
        """
        Adds a user name to the list of profiles to be queued and processed
        later. If this profile has been parsed in the past, the method
        will just ignore it silently.
        """
        with self.lock_:
            if Profile(username) not in self.ongoing_ \
                    and Profile(username) not in self.parsed_:
                self.queued_.add(Profile(username, depth))

    def on_parsed(self, username: str, depth: int, following: List[str],
                  movies: Dict[int, float]) -> None:
        """
        This method creates a profile with the details passed as parameter.
        The profile is put on the list of parsed profiles and its
        username is removed from the list of ongoing jobs.

        Any other users that are seen in the details of this profiles
        - following, follower, etc) - if never seen before, are adding to the
        queue to be processed in the future.
        """
        for f in following:
            self.enqueue(f, depth + 1)

        p = Profile(username, depth, following, movies)
        with self.lock_:
            print(p.username, p.depth)
            self.parsed_.add(p)
            self.ongoing_.discard(p)

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

            popped_profile = self.queued_.pop()
            self.ongoing_.add(popped_profile)
            return popped_profile

    def dump(self) -> Dict:
        """ Dump the whole internal stte as a dictionary. """
        def repr_set(s):
            def repr_p(p):
                if p.isEmpty():
                    return (p.username, p.depth)
                movies = [[k, v] for (k, v) in p.movies.items()]
                return (p.username, p.depth, p.following, movies)

            return [repr_p(p) for p in s]

        return {"parsed": repr_set(self.parsed_),
                "queued": repr_set(self.queued_)}

    def loads(self, data: str) -> None:
        """ Load state from a string. """
        d = json.loads(data)
        self.queued_ = set()
        for p in d["queued"]:
            self.queued_.add(Profile(p[0], p[1]))

        for p in d["parsed"]:
            movies = {int(k): v for (k, v) in p[3]}
            self.parsed_.add(Profile(p[0], p[1], p[2], movies))
