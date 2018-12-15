import requests
from bs4 import BeautifulSoup
from progress.bar import Bar
from yaml import dump


BASE_URL = "https://kubernetes.io"
IGNORE_LIST = [
    "/docs/home/"
]

def main():
    page = requests.get("%s/docs/home/" % BASE_URL)
    soup = BeautifulSoup(page.text, 'lxml')
    index = createIndex(soup)
    store(index)


def createIndex(soup):
    index = []
    chapters = soup.select(".browsedocs > .browsesection") #  > .docstitle a
    for elem in chapters:
        title = elem.select_one('.docstitle a')
        subs = elem.select('.pages a')
        if title.get('href') in IGNORE_LIST:
            continue
        chapter = {
            'title': title.text,
            'link': "%s%s" % (BASE_URL, title.get('href')),
            'sub': list(map(lambda x: {
                'title': x.text,
                'link': "%s%s" % (BASE_URL, x.get('href')),
            }, subs))
        }

        index.append(chapter)
    return index


def store(dic):
    stream = open('./output/index.yaml', 'w')
    dump(dic, stream=stream, default_flow_style=False)


if __name__ == '__main__':
    main()
