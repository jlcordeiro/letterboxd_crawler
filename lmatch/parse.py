
def _extract_value(str, key, start):
    start = str.find(key, start)
    if start is -1:
        return (-1, -1, "")

    start += len(key)
    end = str.find("\"", start)
    return (start, end, str[start:end])


def next_page(str):
    key_page_next = "\"next\" href=\""

    start = str.rfind("paginate-nextprev")
    start = str.find(key_page_next, start)
    if start is -1:
        return None

    start += len(key_page_next)
    end_idx = str.find("\"", start)
    return str[start + 1:end_idx]


def following(page):
    following = []

    start = 1
    while start > 0:
        start = page.find("table-person", start)
        if start > 0:
            (start, _, followed) = _extract_value(page, "href=\"", start)
            following.append(followed[1:-1])

    return following


def movies_watched(page):
    movies = []

    tag_movie_container = "poster-container"
    tag_movie_name = "data-target-link=\"/film/"
    tag_movie_rate = " rated-"

    start = 1
    while start > 0:
        start = page.find(tag_movie_container, start)
        if start > 0:
            # some movies aren't rated. so we can only search for the rating
            # up to the beginning of the next movie
            # detect where to stop
            stop_at = page.find(tag_movie_container, start + 3)

            (start, _, movie_name) = _extract_value(page, tag_movie_name, start)
            (_, start, movie_rate) = _extract_value(page, tag_movie_rate, start)

            if start > stop_at or start is -1:
                start = stop_at - 1
                movie_rate = 0

            movies.append((movie_name[:-1], int(movie_rate)))

    return movies
