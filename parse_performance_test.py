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

def validate(expected, result):
    if (result != expected):
        print("Error!\nExpected: {}\nGot: {}".format(expected, result))
    else:
        print("ok")

if __name__ == "__main__":
    def run_tests(filename):
        with open(filename, 'r') as file:
            data = file.read()

        n_cycles = 5

        print("== string scanning")
        absolute_start_time = datetime.now()
        for x in range(n_cycles):
            start_time = datetime.now()
            for _ in range(100):
                result = parse_strfind(data)

            end_time = datetime.now()
            print('Test {}. Duration: {}'.format(x, end_time - start_time))
        print('Total. Duration: {}\n\n'.format(end_time - absolute_start_time))


        print("== BeautifulSoup")
        absolute_start_time = datetime.now()
        for x in range(n_cycles):
            start_time = datetime.now()
            for _ in range(100):
                expected = parse_beautiful_soup(data)

            end_time = datetime.now()
            print('Test {}. Duration: {}'.format(x, end_time - start_time))
        validate(expected, result)
        print('Total. Duration: {}'.format(end_time - absolute_start_time))

    run_tests("testdata/jlcordeiro_following_1.html")
    run_tests("testdata/jlcordeiro_following_2.html")
