from kivybooks.utils import recursive, ALIGN


class Tags:
    def __init__(self, font_size, finish, soup):
        self.__font_size = int(font_size)
        self.__title_font_size = self.__font_size + 12
        self.__subtitle_font_size = self.__font_size + 8
        self.finish = finish
        self.__soup = soup
        self.tags = {
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
            'image': self.image
                }
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