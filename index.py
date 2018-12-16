import requests
from bs4 import BeautifulSoup
from helpers import store_index


BASE_URL = "https://kubernetes.io"
IGNORE_LIST = [
    "/docs/home/"
]

def main():
    page = requests.get("%s/docs/home/" % BASE_URL)
    soup = BeautifulSoup(page.text, 'lxml')
    index = create_index(soup)
    store(index)

def create_index(soup):
    i = 0
    index = []
    chapters = soup.select(".browsedocs > .browsesection") #  > .docstitle a
    for elem in chapters:
        title = elem.select_one('.docstitle a')
        sections = elem.select('.pages a')
        if title.get('href') in IGNORE_LIST:
            continue
        i += 1
        chapter = {
            'number': i,
            'title': title.text,
            'link': "%s%s" % (BASE_URL, title.get('href')),
            'sections': list(map(lambda x: {
                'title': x.text,
                'link': "%s%s" % (BASE_URL, x.get('href')),
            }, sections))
        }

        index.append(chapter)
    return index

if __name__ == '__main__':
    main()
