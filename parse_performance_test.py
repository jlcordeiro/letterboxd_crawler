from requests import session
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

    start_idx = page_contents.rfind("paginate-nextprev")
    if start_idx is -1:
        page_next = None
    start_idx = page_contents.find(key_page_next, start_idx)
    if start_idx is -1:
        page_next = None
    start_idx += len(key_page_next)
    end_idx = page_contents.find("\"", start_idx)

    page_next = page_contents[start_idx + 1 : end_idx]

    return (following, page_next)

def validate(result):
    expected = (['dunkeey', 'gonfsilva', 'crispim', 'inesqsc', 'nihilism', 'carsonkims', 'o_serkan_o', 'davidehrlich', 'carolina_ab', 'nunoabreu', 'boppitybunny', 'apeloeh', 'wonderfulcinema', 'followtheblind', 'jkottke', 'sandwich', 'khoi', 'vishnevetsky', 'dmoren', 'pbones', 'emanuel', 'zkorpi', 'inesdelgado', 'faitherina', 'mpmont'], 'jlcordeiro/following/page/2/')
    if (result != expected):
        print("Error!\nExpected: {}\nGot: {}".format(expected, result))
    else:
        print("ok")

if __name__ == "__main__":
    filename = "testdata/jlcordeiro_following_1.html"
    with open(filename, 'r') as file:
        data = file.read()


    print("== string scanning")
    absolute_start_time = datetime.now()
    for x in range(10):
        start_time = datetime.now()
        for _ in range(100):
            result = parse_strfind(data)

        end_time = datetime.now()
        print('Test {}. Duration: {}'.format(x, end_time - start_time))
    validate(result)
    print('Total. Duration: {}\n\n'.format(end_time - absolute_start_time))


    print("== BeautifulSoup")
    absolute_start_time = datetime.now()
    for x in range(10):
        start_time = datetime.now()
        for _ in range(100):
            result = parse_beautiful_soup(data)

        end_time = datetime.now()
        print('Test {}. Duration: {}'.format(x, end_time - start_time))
    validate(result)
    print('Total. Duration: {}'.format(end_time - absolute_start_time))

