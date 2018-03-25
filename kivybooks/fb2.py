# -*- coding: utf-8 -*-
# This class created to read fb2 files
# and convert text to kivy markup for Label
# Created by Bohdan Sapovsky 2016
from bs4 import BeautifulSoup as Bs
import time
from bs4.element import NavigableString as NV
from kivybooks.utils import GetCoverImage, LineModel, ALIGN
from kivybooks.tags import Tags

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='debug.log')

logger = logging.getLogger(__name__)


class FB2Parser:
    global ALIGN

    def __init__(self, fb2, font_size, enc='utf-8'):
        self.__soup = Bs(fb2, 'xml', from_encoding=enc)
        self.__text = []
        self.__tags =  Tags(font_size=font_size, finish = self.finish, soup = self.__soup)
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
                          }
        self.__markdown = dict(**self.__markdown, **self.__tags.tags)

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
        # return self.body(soup)
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


# __main__ only for testing!
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
