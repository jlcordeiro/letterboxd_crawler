from bs4 import BeautifulSoup
from datetime import datetime
from crawl import extract_following, extract_next_page

def parse_beautiful_soup(page_contents):
    following = []
    soup = BeautifulSoup(page_contents, "html.parser")
    following.extend(extract_following(soup))
    page_next = extract_next_page(soup)
    return (following, page_next)

def parse_strfind(page_contents):
    following = []

    key_username = "href=\""
    key_page_next = "\"next\" href=\""

    start_idx = 0
    while True:
        start_idx = page_contents.find("table-person", start_idx)
        if start_idx is -1:
            break
        start_idx = page_contents.find(key_username, start_idx) + len(key_username)
        end_idx = page_contents.find("\"", start_idx)

        following.append(page_contents[start_idx + 1 : end_idx - 1])

        start_idx = end_idx

    page_next = None
    start_idx = page_contents.rfind("paginate-nextprev")
    if start_idx > 0:
        start_idx = page_contents.find(key_page_next, start_idx)
        if start_idx > 0:
            start_idx += len(key_page_next)
            end_idx = page_contents.find("\"", start_idx)
            page_next = page_contents[start_idx + 1 : end_idx]

    return (following, page_next)

def extract_movies(page_contents):
    movies = []

    def extract_value(str, key, start):
        start = str.find(key, start) + len(key)
        end = str.find("\"", start)
        return (start, end, str[start : end])

    start = 1
    while start > 0:
        start = page_contents.find("poster-container", start)
        if start > 0:
            (start, _, movie_name) = extract_value(page_contents, "data-target-link=\"/film/", start)
            (_, start, movie_rate) = extract_value(page_contents, " rated-", start)

            movies.append((movie_name[:-1], int(movie_rate)))


    # pagination

    key_page_next = "\"next\" href=\""

    page_next = None
    start = page_contents.rfind("paginate-nextprev")
    start = page_contents.find(key_page_next, start)
    if start > 0:
        start += len(key_page_next)
        end_idx = page_contents.find("\"", start)
        page_next = page_contents[start + 1 : end_idx]

    return (movies, page_next)


def validate(expected, result):
    if (result != expected):
        print("Error!\nExpected: {}\nGot: {}".format(expected, result))
    else:
        print("ok")

if __name__ == "__main__":
    def run_tests(test_name, test_func, test_data_filename):
        with open(test_data_filename, 'r') as file:
            test_data = file.read()

        n_cycles = 5
        n_runs   = 100

        print("== ", test_name)
        absolute_start_time = datetime.now()
        for x in range(n_cycles):
            start_time = datetime.now()
            for _ in range(n_runs):
                output = test_func(test_data)

            end_time = datetime.now()
            print('Test {}. Duration: {}'.format(x, end_time - start_time))
        print('Total. Duration: {}\n\n'.format(end_time - absolute_start_time))

        return output


    def compare_tests(filename):
        result = run_tests("string scanning", parse_strfind, filename)
        expected = run_tests("BeautifulSoup", parse_beautiful_soup, filename)
        validate(expected, result)

    compare_tests("testdata/jlcordeiro_following_1.html")
    compare_tests("testdata/jlcordeiro_following_2.html")

    print("----- running preliminary tests for movie pages parsing  -------")

    m1 = run_tests("movies1", extract_movies, "testdata/jlcordeiro_watched_1.html")
    m3 = run_tests("movies3", extract_movies, "testdata/jlcordeiro_watched_3.html")
    m7 = run_tests("movies7", extract_movies, "testdata/jlcordeiro_watched_7.html")

    print(m1[1], m3[1], m7[1])
