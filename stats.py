import sys
import json
import argparse
import statistics
from requests import session
from lmatch import profile_crawler, parse


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
    with open(dump_filename, 'r') as infile:
        str = infile.read()
        crawler.loads(str)
        infile.close()

    main_profile = None
    for p in crawler.parsed_:
        if p.username == first_profile:
            main_profile = p

    if main_profile is None:
        print("User not found.")
        sys.exit(1)

    main_movies = {k: v for (k, v) in main_profile.movies if v}

    matches = []
    for p in crawler.parsed_:
        if p.username == main_profile.username:
            continue

        deltas = []

        for (this_name, this_rating) in p.movies:
            if this_rating is 0 or this_name not in main_movies:
                continue

            (main_name, main_rating) = (this_name, main_movies[this_name])
            deltas.extend([this_rating - main_rating])

        matches.extend([[p.username,
                         len(deltas),
                         (sum(deltas) * 1.0 / len(deltas)) if sum(deltas) else
                         0]])

        matches = sorted(matches, key=lambda m: abs(m[2]))

    for match in matches:
        if match[1]:
            print("[{}] {:20} {:5} movies in common. Avg rating diff: {}"
                    .format('x' if match[0] in main_profile.following else ' ',
                        match[0], match[1], match[2]))

if __name__ == "__main__":
    main(sys.argv[1:])
