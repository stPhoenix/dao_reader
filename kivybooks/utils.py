from functools import wraps
from io import BytesIO
import base64

ALIGN = {'center': 'center', 'left': 'left', 'right': 'right'}


def recursive(func):
    @wraps(func)
    def wrapped(self, soup):
        line = LineModel()
        bbcode = []
        func(self, soup, line, bbcode)
        return self.finish(soup, line, bbcode)

    return wrapped


class GetCoverImage:
    def __init__(self, soup):
        self.response = {'title': 'Unknown', 'author': 'Unknown', 'coverimage': None}
        self.__soup = soup
        self.title_info = self.__soup.find('title-info')
        if self.title_info is not None:
            self.start()

    def get_response(self):
        return self.response

    def start(self):
        options = {
            'author': self.author,
            'book-title': self.book_title,
            'coverpage': self.coverpage,
        }
        for item in self.title_info.children:
            if item.name in options.keys():
                options[item.name](item)

    def author(self, item):
        if item.nickname is not None:
            self.response['author'] += '(' + item.get_text() + ')'
        else:
            self.response['author'] = ''
            for child in item.children:
                self.response['author'] += child.get_text() + ' '

    def book_title(self, item):
        self.response['title'] = item.get_text()

    def coverpage(self, item):
        href = item.image.get('l:href')
        if href is None:
            href = item.image.get('xlink:href')
        if href[0] == "#":
            href = href.strip('#')
            cover_image = self.__soup.find('binary', attrs={'id': href})
            if cover_image is not None:
                cover_image = cover_image.get_text().strip('\n')
                self.response['coverimage'] = BytesIO(base64.standard_b64decode(cover_image))
            else:
                self.response['coverimage'] = 'default'


class LineModel:
    __slots__ = ('__text', '__align', '__tag')

    def __init__(self, text=None, align=ALIGN['left'], tag=None):
        self.__align = align
        self.__tag = tag
        self.__text = text

    def set_text(self, text):
        self.__text = text

    def set_align(self, align):
        self.__align = align

    def set_tag(self, tag):
        self.__tag = tag

    def get_text(self):
        return self.__text

    def get_align(self):
        return self.__align

    def get_tag(self):
        return self.__tag