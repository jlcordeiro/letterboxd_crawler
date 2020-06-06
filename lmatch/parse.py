from lmatch import film
from typing import List, Tuple, Union


def _extract_value(data, key: str, start: int) -> Tuple[int, int, str]:
    """ Find and extract <value> out of a
        ..key": "<value>"....

        Returns a tuple with
        - the index to the start of the value
        - the index to the end of the value
        - the string with the value found

        If not found (-1, -1, "")
    """
    start = data.find(key, start)
    if start is -1:
        return (-1, -1, "")

    start += len(key)
    end = data.find("\"", start)
    return (start, end, data[start:end])


def next_page(page: str) -> Union[None, str]:
    """ Given the contents of a Letterboxd page, returns
        the relative path to the next page to parse. It
        handles the pagination of any type of page,
        from followers, to following, to movies watched,
        etc.

        Returns None if this is the last page already
        and there isn't another one to parse.
    """
    key_page_next = "\"next\" href=\""

    start = page.rfind("paginate-nextprev")
    start = page.find(key_page_next, start)
    if start is -1:
        return None

    start += len(key_page_next)
    end_idx = page.find("\"", start)
    return page[start + 1:end_idx]


def following(page: str) -> List[str]:
    """ Given a Letterboxd 'following' page, parses out the
    list of usernames followed in it.

    Warning: Not a lot of checks are done, if the wrong page
    is passed, most likely it'll just return an empty list.
    """
    following = []

    start = 1
    while start > 0:
        start = page.find("table-person", start)
        if start > 0:
            (start, _, followed) = _extract_value(page, "href=\"", start)
            following.append(followed[1:-1])

    return following


def movies_watched(page: str) -> List[Tuple[str, int]]:
    """ Given a Letterboxd 'films' page, parses out the
    list of movies watched by the user, as well as the
    rating given to each.

    The rating is in a scale [0, 10], wit the default value
    being 0, in case the user didn't rate the movie at all.

    Returns a list of tuples:
        [
            ('movie-a', 7),
            ('movie-b', 2)
        ]

    Warning: Not a lot of checks are done, if the wrong page
    is passed, most likely it'll just return an empty list.
    """
    movies = []

    tag_movie_container = "poster-container"
    tag_name = "data-target-link=\"/film/"
    tag_rate = " rated-"

    start = 1
    while start > 0:
        start = page.find(tag_movie_container, start)
        if start > 0:
            # some movies aren't rated. so we can only search for the rating
            # up to the beginning of the next movie
            # detect where to stop
            stop_at = page.find(tag_movie_container, start + 3)

            (start, _, movie_name) = _extract_value(page, tag_name, start)
            (_, start, movie_rate) = _extract_value(page, tag_rate, start)

            if start > stop_at or start is -1:
                start = stop_at - 1
                movie_rate = 0

            movies.append((movie_name[:-1], int(movie_rate)))

    return movies


def parse_film(page: str) -> film.Film:
    """ Given a Letterboxd 'film' page, parses out the
    film details.
    """

    tag_id = "filmData = { id: "
    start = 1
    start = page.find(tag_id, start) + len(tag_id)
    end = page.find(", ", start)
    id = int(page[start:end])

    (start, end, name) = (_extract_value(page, "name: \"", start))
    (start, end, path) = (_extract_value(page, "path: \"/film/", start))
    (start, end, avg_rate) = (_extract_value(page, "ratingValue\":", start))
    avg_rate = float(avg_rate[:-1]) * 2

    return film.Film(id, path[:-1], name, avg_rate)
