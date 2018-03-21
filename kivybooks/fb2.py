# -*- coding: utf-8 -*-
# This class created to read fb2 files
# and convert text to kivy markup for Label
# Created by Bohdan Sapovsky 2016
from io import BytesIO
import base64
from bs4 import BeautifulSoup as Bs
import time
from bs4.element import NavigableString as NV
from functools import wraps

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='debug.log')

logger = logging.getLogger(__name__)

ALIGN = {'center': 'center', 'left': 'left', 'right': 'right'}


def recursive(func):
    @wraps(func)
    def wrapped(self, soup):
        line = LineModel()
        bbcode = []
        func(self, soup, line, bbcode)
        return self.finish(soup, line, bbcode)

    return wrapped


class FB2Parser:
    global ALIGN

    def __init__(self, fb2, font_size, enc='utf-8'):
        self.__soup = Bs(fb2, 'xml', from_encoding=enc)
        self.__text = []
        self.__font_size = int(font_size)
        self.__title_font_size = self.__font_size + 12
        self.__subtitle_font_size = self.__font_size + 8
        self.__setup_markdown()

    def __setup_markdown(self):
        # TODO: Add link engine
        # TODO: Add table engine
        self.__markdown = {'body': self.body,
                           'section': self.section,
                           'description': self.description,
                           'binary': self.binary,
                           'FictionBook': self.fiction_book,
                           '[document]': self.document,
                           'title': self.title,
                           'epigraph': self.epigraph,
                           'subtitle': self.subtitle,
                           'annotation': self.annotation,
                           'p': self.p,
                           'empty-line': self.empty_line,
                           'strong': self.strong,
                           'emphasis': self.emphasis,
                           'sub': self.sub,
                           'sup': self.sup,
                           'strikethrough': self.strikethrough,
                           'code': self.code,
                           'poem': self.poem,
                           'stanza': self.stanza,
                           'v': self.v,
                           'text-author': self.text_author,
                           'date': self.date,
                           'cite': self.cite,
                           'image': self.image}

    def get_text(self):
        return self.__text

    def start(self):
        self.prepare(self.__soup)
        self.clear_text(2)

    def prepare(self, soup):
        line = LineModel()
        bbcode = []
        if soup.name in self.__markdown.keys():
            return self.__markdown[soup.name](soup)
        else:
            return self.finish(soup, line, bbcode)

    def finish(self, soup, line, bbcode):
        if type(soup) != NV:
            old_text = soup.get_text()
            text = ' '
            for child in soup.children:
                new_t = self.prepare(child)
                if new_t is not None:
                    remove = self.__text.pop(-1)
                    text = old_text.replace(new_t['old'], new_t['new'])
            text = bbcode[0] + text + bbcode[1] if bbcode != [] else text
            line.set_tag(soup.name)
            if line.get_text() is None:
                line.set_text(text)
            self.__text.append(line)
            return dict(old=old_text, new=text)
        else:
            line.set_tag('text')
            line.set_text(soup)
            self.__text.append(line)
            return dict(old=soup.strip('\n'), new=soup.strip('\n'))

    def get_coverpage(self):
        coverpage = GetCoverImage(self.__soup)
        return coverpage.get_response()

    def clear_text(self, counter):
        for item in self.__text:
            if item.get_tag() == 'text' or item.get_text() is None or item.get_tag() is None:
                self.__text.remove(item)
        if counter > 0:
            counter -= 1
            self.clear_text(counter)

    def body(self, soup):
        for child in soup.children:
            self.prepare(child)
        return None

    def section(self, soup):
        # TODO add sections
        # if soup.get('id') is not None:
        #     line.set_text(soup['id'])
        # self.__text.append(line)
        #return self.body(soup)
        self.body(soup)
        return None

    def description(self, soup):
        return None

    def binary(self, soup):
        return None

    def fiction_book(self, soup):
        self.body(soup)
        return None

    def document(self, soup):
        self.body(soup)
        return None

    @recursive
    def title(self, soup, line, bbcode):
        bbcode.append('[size=%s]' % self.__title_font_size)
        bbcode.append('[/size]')

    @recursive
    def epigraph(self, soup, line, bbcode):
        line.set_align(ALIGN['right'])
        bbcode.append('[i]')
        bbcode.append('[/i]')

    @recursive
    def subtitle(self, soup, line, bbcode):
        bbcode.append('[size=%s]' % self.__subtitle_font_size)
        bbcode.append('[/size]')

    @recursive
    def image(self, soup, line, bbcode):
        href = soup.get('l:href')
        if href is None:
            href = soup.get('xlink:href')
        if href[0] == "#":
            href = href.strip('#')
            cover_image = self.__soup.find('binary', attrs={'id': href})
            if cover_image is not None:
                cover_image = cover_image.get_text().strip('\n')
            else:
                cover_image = 'default'
            line.set_text(cover_image)

    @recursive
    def annotation(self, soup, line, bbcode):
        bbcode.append('[i]')
        bbcode.append('[/i]')

    @recursive
    def p(self, soup, line, bbcode):
        bbcode.append('\t')
        # To get not None
        bbcode.append(' ')

    @recursive
    def empty_line(self, soup, line, bbcode):
        bbcode.append('\n')
        # To get not None
        bbcode.append(' ')

    @recursive
    def strong(self, soup, line, bbcode):
        bbcode.append('[b]')
        bbcode.append('[/b]')

    @recursive
    def emphasis(self, soup, line, bbcode):
        bbcode.append('[i]')
        bbcode.append('[/i]')

    @recursive
    def sub(self, soup, line, bbcode):
        bbcode.append('[sub]')
        bbcode.append('[/sub]')

    @recursive
    def sup(self, soup, line, bbcode):
        bbcode.append('[sup]')
        bbcode.append('[/sup]')

    @recursive
    def strikethrough(self, soup, line, bbcode):
        bbcode.append('[strikethrough]')
        bbcode.append('[/strikethrough]')

    @recursive
    def code(self, soup, line, bbcode):
        bbcode.append('[code]')
        bbcode.append('[/code]')

    @recursive
    def poem(self, soup, line, bbcode):
        line.set_align(ALIGN['center'])

    @recursive
    def stanza(self, soup, line, bbcode):
        bbcode.append('\n')
        bbcode.append(' ')

    @recursive
    def v(self, soup, line, bbcode):
        line.set_align(ALIGN['center'])
        bbcode.append('\n')
        bbcode.append(' ')

    @recursive
    def text_author(self, soup, line, bbcode):
        line.set_align(ALIGN['right'])
        bbcode.append('\n')
        bbcode.append(' ')

    @recursive
    def date(self, soup, line, bbcode):
        line.set_align(ALIGN['right'])
        bbcode.append('\n')
        bbcode.append(' ')

    @recursive
    def cite(self, soup, line, bbcode):
        line.set_align(ALIGN['right'])
        bbcode.append('[i]"')
        bbcode.append('"[/i]')


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


#####################################
class LineModel:
    __slots__ = ('__text', '__align', '__tag')
    global ALIGN

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

####__main__ only for testing!
if __name__ == '__main__':
    coverpage = ''
    with open('asterisk.fb2', 'r', encoding='UTF-8') as fb2:
        t0 = time.time()
        xml = fb2.read()
        parser = FB2Parser(xml, 16)
        parser.start()
        t1 = time.time() - t0
        print("TIME %s" % t1)
        #print(parser.get_coverpage())
        print('LEN IS %s' % len(parser.get_text()))
        for child in parser.get_text():
            if child.get_tag() == 'image':
                logging.info(child.get_text()[0])
            else:
                logging.info('%s' % child.get_text())
            #logging.info(child.get_tag())
        # coverpage = parser.get_coverpage()['coverimage']

    #from kivy.core.image import Image as CoreImage

    #bb = base64.standard_b64decode(coverpage)
    #im = CoreImage(BytesIO(bb), ext='jpeg')
