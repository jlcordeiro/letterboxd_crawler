
def _extract_value(str, key, start):
    start = str.find(key, start) + len(key)
    end = str.find("\"", start)
    return (start, end, str[start : end])

def next_page(str):
    key_page_next = "\"next\" href=\""

    start = str.rfind("paginate-nextprev")
    start = str.find(key_page_next, start)
    if start is -1:
        return None

    start += len(key_page_next)
    end_idx = str.find("\"", start)
    return str[start + 1 : end_idx]

def following(page):
    following = []

    start = 1
    while start > 0:
        start = page.find("table-person", start)
        if start > 0:
            (start, _, followed) = _extract_value(page, "href=\"", start)
            following.append(followed[1 : -1])

    return following

def movies_watched(page_contents):
    movies = []

    start = 1
    while start > 0:
        start = page_contents.find("poster-container", start)
        if start > 0:
            (start, _, movie_name) = _extract_value(page_contents, "data-target-link=\"/film/", start)
            (_, start, movie_rate) = _extract_value(page_contents, " rated-", start)

            movies.append((movie_name[:-1], int(movie_rate)))


    page_next = next_page(page_contents)

    return (movies, page_next)

