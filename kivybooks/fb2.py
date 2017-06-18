# -*- coding: utf-8 -*-
# This class created to read fb2 files
# and convert text to kivy markup for Label
# Created by Bohdan Sapovsky 2016
from io import BytesIO
import base64
from bs4 import BeautifulSoup as Bs
import time
from bs4.element import NavigableString as NV

ALIGN = {'center': 'center', 'left': 'left', 'right': 'right'}


#############################
class FB2Parser:
    global ALIGN

    def __init__(self, fb2, font_size, enc='utf-8'):
        self.__soup = Bs(fb2, 'xml', from_encoding=enc)
        self.__text = []
        self.__font_size = int(font_size)
        self.__title_font_size = self.__font_size + 12
        self.__subtitle_font_size = self.__font_size + 8
        #logging.info('Init success')

    def get_text(self):
        return self.__text

    def start(self):
        self.prepare(self.__soup)

    def prepare(self, soup):
        line = LineModel()
        bbcode = []
        if soup.name == 'body':
            for child in soup.children:
                self.prepare(child)
        elif soup.name == 'section':
            line.set_tag('section')
            #TODO add sections
            # if soup.get('id') is not None:
            #     line.set_text(soup['id'])
            # self.__text.append(line)
            for child in soup.children:
                self.prepare(child)
        elif soup.name == 'description':
            pass
        elif soup.name == 'binary':
            pass
        elif soup.name == 'FictionBook':
            for child in soup.children:
                self.prepare(child)
        elif soup.name == '[document]':
            for child in soup.children:
                self.prepare(child)
            # This func for removing empty TEXT strings
            self.clear_text(2)
        else:
            if soup.name == 'title':
                bbcode.append('[size=%s]' % self.__title_font_size)
                bbcode.append('[/size]')
            elif soup.name == 'subtitle':
                bbcode.append('[size=%s]' % self.__subtitle_font_size)
                bbcode.append('[/size]')
            elif soup.name == 'epigraph':
                line.set_align(ALIGN['right'])
                bbcode.append('[i]')
                bbcode.append('[/i]')
            elif soup.name == 'image':
                # print('IMAGE FOUND!')
                href = soup.get('l:href')
                #print('href is %s' % href)
                if href is None:
                    href = soup.get('xlink:href')
                    #print('href is %s' % href)
                if href[0] == "#":
                    href = href.strip('#')
                    cover_image = self.__soup.find('binary', attrs={'id': href})
                    if cover_image is not None:
                        cover_image = cover_image.get_text().strip('\n')
                        #line.set_text(BytesIO(base64.standard_b64decode(cover_image)))
                        # print("IMAGE BIN: %s" % cover_image)
                    else:
                        cover_image = 'default'
                    line.set_text(cover_image)

            elif soup.name == 'annotation':
                bbcode.append('[i]')
                bbcode.append('[/i]')

            elif soup.name == 'p':
                bbcode.append('\t')
                # To get not None
                bbcode.append(' ')
            elif soup.name == 'empty-line':
                bbcode.append('\n')
                # To get not None
                bbcode.append(' ')
            elif soup.name == 'strong':
                bbcode.append('[b]')
                bbcode.append('[/b]')
            elif soup.name == 'emphasis':
                bbcode.append('[i]')
                bbcode.append('[/i]')
            elif soup.name == 'sub':
                bbcode.append('[sub]')
                bbcode.append('[/sub]')
            elif soup.name == 'sup':
                bbcode.append('[sup]')
                bbcode.append('[/sup]')
            elif soup.name == 'strikethrough':
                bbcode.append('[strikethrough]')
                bbcode.append('[/strikethrough]')
            elif soup.name == 'code':
                bbcode.append('[code]')
                bbcode.append('[/code]')
            elif soup.name == 'poem':
                line.set_align(ALIGN['center'])
            elif soup.name == 'stanza':
                bbcode.append('\n')
                bbcode.append(' ')
            elif soup.name == 'v':
                line.set_align(ALIGN['center'])
                bbcode.append('\n')
                bbcode.append(' ')
            elif soup.name == 'text-author':
                line.set_align(ALIGN['right'])
                bbcode.append('\n')
                bbcode.append(' ')
            elif soup.name == 'date':
                line.set_align(ALIGN['right'])
                bbcode.append('\n')
                bbcode.append(' ')
            elif soup.name == 'cite':
                line.set_align(ALIGN['right'])
                bbcode.append('[i]"')
                bbcode.append('"[/i]')
            elif soup.name == 'a':
                pass
                # TODO: Add link engine
                # bbcode.append('[]')
                # bbcode.append('[]')
            elif soup.name == 'table':
                pass
                # TODO: Add table engine
                # bbcode.append('[]')
                # bbcode.append('[]')
            elif soup.name == 'tr':
                pass
                # TODO: Add table engine
                # bbcode.append('[]')
                # bbcode.append('[]')
            elif soup.name == 'th':
                pass
                # TODO: Add table engine
                # bbcode.append('[]')
                # bbcode.append('[]')
            elif soup.name == 'td':
                pass
                # TODO: Add table engine
                # bbcode.append('[]')
                # bbcode.append('[]')
            # elif soup.name is None:
            #     pass
            # elif soup.name == '':
            #     bbcode.append('[]')
            #     bbcode.append('[]')
            # elif soup.name == '':
            #     bbcode.append('[]')
            #     bbcode.append('[]')
            # elif soup.name == '':
            #     bbcode.append('[]')
            #     bbcode.append('[]')
            # elif soup.name == '':
            #     bbcode.append('[]')
            #     bbcode.append('[]')
            else:
                pass

            if type(soup) != NV:
                old_text = soup.get_text()
                # print(old_text)
                text = ' '
                for child in soup.children:
                    new_t = self.prepare(child)
                    # print('child %s : %s'%(child.name, new_t))
                    if new_t is not None:
                        removed = self.__text.pop(-1)
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
        return None

    def get_coverpage(self):
        response = {'title': 'Unknown', 'author': 'Unknown', 'coverimage': None}
        title_info = self.__soup.find('title-info')
        if title_info is not None:
            for item in title_info.children:
                if item.name == 'author':
                    if item.nickname is not None:
                        response['author'] += '(' + item.get_text() + ')'
                    else:
                        response['author'] = ''
                        for child in item.children:
                            response['author'] += child.get_text() + ' '
                elif item.name == 'book-title':
                    response['title'] = item.get_text()
                elif item.name == 'coverpage':
                    href = item.image.get('l:href')
                    #print('href is %s' % href)
                    if href is None:
                        href = item.image.get('xlink:href')
                        #print('href is %s' % href)
                    if href[0] == "#":
                        #href = item.image['l:href']
                        href = href.strip('#')
                        #print(href)
                        cover_image = self.__soup.find('binary', attrs={'id': href})
                        if cover_image is not None:
                            cover_image = cover_image.get_text().strip('\n')
                            #response['coverimage'] = cover_image
                            response['coverimage'] = BytesIO(base64.standard_b64decode(cover_image))
                        else:
                            response['coverimage'] = 'default'
        return response

    def clear_text(self, counter):
        for item in self.__text:
            if item.get_tag() == 'text' or item.get_text() is None:
                self.__text.remove(item)
        if counter > 0:
            counter -= 1
            self.clear_text(counter)


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
                print(child.get_text()[0])
            else:
                print('%s' % child.get_text())
        # coverpage = parser.get_coverpage()['coverimage']

    #from kivy.core.image import Image as CoreImage

    #bb = base64.standard_b64decode(coverpage)
    #im = CoreImage(BytesIO(bb), ext='jpeg')
