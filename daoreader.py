# -*- coding: utf-8 -*-
import logging
from io import BytesIO
import base64
import sys
import os, copy, time, random
from concurrent.futures import ThreadPoolExecutor
import csv
from memory_profiler import profile
from kivymd.navigationdrawer import NavigationDrawer
import kivy
from kivy.graphics import *
kivy.require('1.9.1')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.uix.label import Label
from kivy.core.image import Image as CoreImage
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import get_color_from_hex as ghex
from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.uix.image import Image

from kivymd.theming import ThemeManager
from kivymd.ripplebehavior import RectangularRippleBehavior
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.list import BaseListItem
from kivymd.menu import MDMenuItem
from kivymd.spinner import MDSpinner

from apptools import sett
from apptools.gesture_box import GestureBox as Gesture
from kivybooks.fb2 import FB2Parser
from apptools.toolspanel import ToolsPanel

#############################
class Main(BoxLayout):
    books = []

    def __init__(self, **kwargs):
        super(Main, self).__init__(**kwargs)
        self.executor = ThreadPoolExecutor()
        self.tpanel = TPanel()
        self.p = self.tpanel.pos
        self.config = App.get_running_app().config
        self.font_size = int(self.config.get('section1', 'font_size'))
        self.bg_color = None
        self.text_color = None
        self.config_changes('bg_color', self.config.get('section1', 'bg_color'))
       # self.ids.scr_mng.current = 'main_screen'
        App.get_running_app().bind(on_stop=self.write_books)
        Window.bind(on_draw=self.load_saved)

    def load_saved(self, *largs, **kwargs):
        Window.unbind(on_draw=self.load_saved)
        try:
            with open('books.csv') as csvfile:
                reader = csv.DictReader(csvfile)
                # for row in reader:
                #     #self.load_book(path=row['path'], lindex=int(row['lindex']))
                #     threading.Thread(target=self.load_book, kwargs={'path': row['path'], 'lindex': int(row['lindex'])}).start()
                #     #Clock.schedule_once(lambda dt: self.load_book(path=row['path'], lindex=int(row['lindex'])))
                pool = {self.executor.submit(self.load_book, row['path'], int(row['lindex'])): row for row in reader}
        except Exception as e:
            print('error %s' % e)

    def write_books(self, obj):
        with open('books.csv', 'w') as csvfile:
            fieldnames = ['path', 'lindex']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for book in self.books:
                writer.writerow({'path': book.get_path(), 'lindex': str(book.get_last_index())})

    def config_changes(self, key, value):
        self.config = App.get_running_app().config
        print('config changes')
        self.config.set('section1', key, value)
        self.config.write()
        token = (key, value)
        if token == ('bg_color', 'White'):
            self.bg_color = (255, 255, 255, 1)
            self.text_color = ghex('#000000')
        elif token == ('bg_color', 'Black'):
            self.bg_color = (0, 0, 0, 1)
            self.text_color = ghex('#ffffff')
        elif token == ('bg_color', 'Sepia'):
            self.bg_color = (255, 247, 196, 1)
            self.text_color = ghex('#949391')
        elif key == 'font_size':
            self.font_size = int(value)

        if key == 'bg_color':
            App.get_running_app().nav_drawer.ids.fcolor.text = 'Колір фону: %s' % value
        elif key == 'font_size':
            App.get_running_app().nav_drawer.ids.fsize.text = 'Розмір кегля: %s' % value
        elif key == 'font':
            App.get_running_app().nav_drawer.ids.font.text = 'Кегель: %s' % value

    def add_book(self):
        self.dialog = MDDialog(title="Add book",
                               content=LoadDialog(),
                               #size_hint=(.8, None),
                               #height=dp(200),
                               auto_dismiss=False)

        self.dialog.add_action_button("Dismiss",
                                      action=lambda
                                          *x: self.dialog.dismiss())
        #self.dialog.add_action_button('Load', lambda x: )
        self.dialog.open()

    def load_file(self, path, selection):
        if selection is not None and selection != []:
            self.dialog.dismiss()
            Clock.schedule_once(lambda dt: self.executor.submit(self.load_book(os.path.join(path, selection[0]))), 1)

        else:
            content = MDLabel(font_style='Body1',
                              theme_text_color='Secondary',
                              text="Please choose a book!",
                              valign='top')

            content.bind(size=content.setter('text_size'))
            error_dialog = MDDialog(title='NO BOOK CHOOSE',
                                    content=content,
                                    size_hint=(.3, .3),
                                    auto_dismiss=True)
            error_dialog.open()

            print('Selection is none')

    def load_book(self, path, lindex=0,  **kwargs):
        #path = kwargs['path']
        #lindex = kwargs['lindex']
        print(path)
        book = Book(path=path, font_size=self.font_size, text_color=self.text_color, lindex=lindex)
        book.cover_page()
        self.books.append(book)
        Clock.schedule_once(lambda dt: self.kk(book))

    def kk(self, book):
        im = book.get_coverpage()['coverimage']
        try:
            im = CoreImage(im, ext='jpeg').texture
        except Exception as e:
            im = CoreImage('noimage.jpg').texture
        coverpage = CoverPage()
        coverpage.text = book.get_coverpage()['title'] + ' ' + book.get_coverpage()['author']
        coverpage.texture = im
        coverpage.index = self.books.index(book)
        self.ids.recent_read.add_widget(coverpage)
        coverpage_shelf = CoverPage()
        coverpage_shelf.index = coverpage.index
        coverpage_shelf.text = book.get_coverpage()['title'] + ' ' + book.get_coverpage()['author']
        coverpage_shelf.texture = im
        self.ids.book_shelf.add_widget(coverpage_shelf)

    def start_read(self, index):
        self.ids.scr_mng.current = 'reader_screen'
        book = self.books[index]
        book.set_font_size(self.font_size)
        book.set_text_color(self.text_color)
        # Clock.schedule_once(lambda dt: book.start(), 0.5)
        pages_counter = None
        pages = None
        new_page = None
        counter = None
        sm = ScreenManager()
        #self.ids.reader_screen_swipes.clear_widgets()
        #self.ids.reader_screen_swipes.add_widget(sm)
        with self.ids.reader_screen_swipes.canvas:
            #Color(self.bg_color)
            Color(self.bg_color[0], self.bg_color[1], self.bg_color[2], self.bg_color[3])
            Rectangle(pos=self.ids.reader_screen_swipes.pos, size=self.size)
        last_page = []
        title_font_size = self.font_size - 4

        def add_pages(index_p=0):
            nonlocal pages, sm, last_page
            last_page = []
            #for child in sm.screens:
            #    sm.clear_widget(child)
            del sm
            self.ids.reader_screen_swipes.clear_widgets()
            sm = ScreenManager()
            self.ids.reader_screen_swipes.add_widget(sm)
            pages = book.make(index_p)
            for p in pages:
                screen = Screen(name=str(p.id))
                page = FloatLayout()
                title = Label(text=(book.get_coverpage()['author'] + book.get_coverpage()['title']),
                              font_size=str(title_font_size) + 'sp', markup=True, size_hint=[None, None])
                title.color = self.text_color
                title.texture_update()
                title.size = [Window.width, title.texture_size[1]]

                curr_page = Label(text=str(p.id)+'/'+counter,
                                  font_size=str(title_font_size) + 'sp', markup=True, size_hint=[None, None])
                curr_page.color = self.text_color
                curr_page.texture_update()
                curr_page.size = [Window.width, title.texture_size[1]]
                title.pos_hint = {'top': 1}
                p.pos_hint = {'top': .95}
                curr_page.pos_hint = {'bottom': 1}
                page.add_widget(title)
                page.add_widget(p)
                page.add_widget(curr_page)
                screen.add_widget(page)
                sm.add_widget(screen)
                last_page.append(int(p.id))
            print(sys.getsizeof(sm))
            sm.current = str(new_page)

        def update_tpanel():
            self.tpanel.text = str(new_page) + '/' + counter
            self.tpanel.value = new_page
            book.set_last_index(new_page)

        def turn_page_forward(widget):
            nonlocal new_page
            curr_page = int(sm.current)
            new_page = curr_page + 1
            if last_page[-1] < new_page <= int(counter):
                update_tpanel()
                self.ids.reader_screen_swipes.clear_widgets()
                self.ids.reader_screen_swipes.add_widget(waitlabel)
                Clock.schedule_once(lambda dt: add_pages(new_page), 1)

            elif new_page > int(counter):
                pass
            else:
                update_tpanel()
                sm.current = str(new_page)

        def turn_page_backward(widget):
            nonlocal new_page
            curr_page = int(sm.current)
            new_page = curr_page - 1
            if 0 <= new_page < last_page[0]:
                update_tpanel()
                self.ids.reader_screen_swipes.clear_widgets()
                self.ids.reader_screen_swipes.add_widget(waitlabel)
                Clock.schedule_once(lambda dt: add_pages(new_page), 1)
            elif new_page < 0:
                pass
            else:
                update_tpanel()
                sm.current = str(new_page)

        def turn_page(obj, val):
            nonlocal new_page
            if type(val) == float or type(val) == int:
                val = int(val)
            elif type(val) == str:
                try:
                    val = int(val)
                except:
                    val = 0
            new_page = val
            if last_page[-1] < val <= int(counter):
                update_tpanel()
                self.ids.reader_screen_swipes.add_widget(waitlabel)
                Clock.schedule_once(lambda dt: add_pages(val), 1)

            elif val > int(counter):
                pass
            elif 0 <= val < last_page[0]:
                update_tpanel()
                self.ids.reader_screen_swipes.add_widget(waitlabel)
                Clock.schedule_once(lambda dt: add_pages(val), 1)
            elif val < 0:
                pass
            elif last_page[0] < val < last_page[-1]:
                update_tpanel()
                sm.current = str(val)

        def toggle(self):
            App.get_running_app().root.tpanel.toggle()

        def unbind_all(self):
            nonlocal book, pages_counter, sm, pages, last_page, new_page, counter, title_font_size
            self.tpanel.unbind(new_page=turn_page)
            self.tpanel.icon.unbind(on_release=end_read)
            self.ids.reader_screen_swipes.unbind(on_right_to_left_line=turn_page_forward)
            self.ids.reader_screen_swipes.unbind(on_left_to_right_line=turn_page_backward)
            self.ids.reader_screen_swipes.unbind(on_wheel_up_to_down=turn_page_forward)
            self.ids.reader_screen_swipes.unbind(on_wheel_down_to_up=turn_page_backward)
            self.ids.reader_screen_swipes.unbind(on_up_to_down_line=toggle)
            App.get_running_app().nav_drawer.ids.nchange.unbind(on_release=update_text)
            Window.unbind(on_resize=resize)
            del book, pages_counter, sm, pages, last_page, new_page, counter, title_font_size
            #del book

        def end_read(self):
            self = App.get_running_app().root
            unbind_all(self)
            self.ids.scr_mng.current = 'main_screen'
            self.tpanel.toggle()

        def update_text(widget, *largs, **kwargs):
            #self = App.get_running_app().root
            if self.ids.scr_mng.current == 'reader_screen':
                unbind_all(self)
                self.ids.reader_screen_swipes.clear_widgets()
                self.ids.reader_screen_swipes.add_widget(waitlabel)
                Clock.schedule_once(lambda dt: self.start_read(index), 1)

        def resize(self, width , height):
            self = App.get_running_app().root
            unbind_all(self)
            Clock.schedule_once(lambda dt: self.start_read(index), 0.5)

        def on_future(future):
            nonlocal book, pages_counter, sm, pages, last_page, new_page, counter, title_font_size
            book.start()
            pages_counter = len(book.get_pages_counter()) - 1
            new_page = book.get_last_page()
            counter = str(pages_counter)
            self.tpanel.max = pages_counter
            self.tpanel.text = '0/' + counter
            add_pages(book.get_last_page())
            update_tpanel()

        #self.executor.submit(book.start).add_done_callback(on_future)
        #book.start()
        waitlabel = Label(text='Зачекайте, книга відкривається...', font_size=self.font_size, color=self.text_color,
                          pos_hint={'top': 1})
        self.ids.reader_screen_swipes.add_widget(waitlabel)
        Clock.schedule_once(lambda dt: on_future(12), 1)
        #on_future(12)
        self.tpanel.bind(new_page=turn_page)
        self.tpanel.icon.bind(on_release=end_read)
        self.ids.reader_screen_swipes.bind(on_right_to_left_line=turn_page_forward)
        self.ids.reader_screen_swipes.bind(on_left_to_right_line=turn_page_backward)
        self.ids.reader_screen_swipes.bind(on_wheel_up_to_down=turn_page_forward)
        self.ids.reader_screen_swipes.bind(on_wheel_down_to_up=turn_page_backward)
        self.ids.reader_screen_swipes.bind(on_up_to_down_line=toggle)
        App.get_running_app().nav_drawer.ids.nchange.bind(on_release=update_text)
        Window.bind(on_resize=resize)

    def build_menu(self, key):
        values = []
        items = []
        if key == 'bg_color':
            values = ['White', 'Black', 'Sepia']
        elif key == 'font_size':
            values = range(6, 32, 2)
        elif key == 'font':
            values = ['Times New Roman', 'Arial']
        for v in values:
            items.append({'viewclass': 'MenuItem', 'text': str(v), 'key': key})
        return items


#######################


#########################################
class Book:
    def __init__(self, path, font_size, text_color, lindex):
        self.__pages = []
        self.__path = path
        self.__font_size = font_size
        self.__coverpage = None
        self.__text = []
        self.__title_font_size = font_size - 4
        self.__pages_counter = [0]
        self.__text_color = text_color
        self.__last_index = lindex
        self.__last_page = 0

    def start(self):
        xml = None
        enc = 'utf-8'
        try:
            with open(self.__path, 'r', encoding='UTF-8') as fb2:
                xml = fb2.read()
        except Exception as e:
            print("Error: %s" % e)
            print('Parsing windows-1251')
            with open(self.__path, 'r', encoding='windows-1251') as fb2:
                xml = fb2.read()
                enc = 'windows-1251'
        parser = FB2Parser(xml, self.__font_size, enc)
        parser.start()
        self.__text = parser.get_text()
        del parser
        self.__pages_counter = [0]
        self.count_pages()

    def cover_page(self):
        xml = None
        enc = 'utf-8'
        try:
            with open(self.__path, 'r', encoding='UTF-8') as fb2:
                xml = fb2.read()
        except Exception as e:
            print("Error: %s" % e)
            print('Parsing windows-1251')
            with open(self.__path, 'r', encoding='windows-1251') as fb2:
                xml = fb2.read()
                enc = 'windows-1251'
        parser = FB2Parser(xml, self.__font_size, enc)
        self.__coverpage = parser.get_coverpage()
        del parser

    def count_pages(self):
        layout = 0
        print('count pages entered')
        height = Window.height
        title = Label(text=self.__coverpage['author'] + self.__coverpage['title'],
                      font_size=str(self.__title_font_size)+'sp', markup=True,
                      size_hint=[None, None])
        title.text_size = ((Window.width * .9), None)
        title.texture_update()
        title.size = [Window.width, title.texture_size[1]]
        theight = title.height * 2
        page = Label(font_size=self.__font_size, markup=True, size_hint=[None, None],
                     text_size=((Window.width * .9), None))

        def paging(p):
            nonlocal height, title, layout, theight, page
            page.halign=p.get_align()
            pheight = 0
            #page.text_size = ((Window.width * .9), None)
            #page.halign = p.get_align()
            if p.get_tag() == 'image':
                it = BytesIO(base64.standard_b64decode(p.get_text()))
                im = CoreImage(it, ext='jpeg')
                koff = float(im.height / im.width)
                w = 0
                h = 0
                if im.height > Window.height:
                    h = Window.height * 0.7
                    w = float(h * koff)
                if im.width > Window.width and w > Window.width:
                    w = Window.width * 0.7
                    h = float(w * koff)
                pheight = theight + h + layout
                print(pheight)
                del im, koff

            else:
                page.text = p.get_text()
                page.texture_update()
                page.size = [Window.width, page.texture_size[1]]
                pheight = theight + page.texture_size[1] + layout
            #del page
            #page = None
            #print(pheight)
            if pheight < height:
                layout += (pheight - layout - theight)
            elif pheight >= height:
                self.__pages_counter.append(self.__text.index(p))
                #print(self.__text.index(p))
                layout = (pheight - layout - theight)
                #print('L: %s' % layout)
                #print('L ref: %s ' % sys.getsizeof(layout))
                # del layout
                # layout = StackLayout()
                # layout.add_widget(page)
            else:
                print('oops')
            del pheight

            #print('P ref: %s ' % sys.getrefcount(page))
        pl = list(map(paging, self.__text))
        del layout, title, height, pl, page

    def set_font_size(self, font_size):
        self.__font_size = font_size
        self.__title_font_size = font_size - 4

    def set_text_color(self, text_color):
        self.__text_color = text_color

    def set_last_index(self, page_index):
        self.__last_index = self.__pages_counter[page_index]
        self.__last_page = page_index

    def make(self, page_index=0):
        pages = []
        height = Window.height
        title = Label(text=self.__coverpage['author'] + self.__coverpage['title'],
                      font_size=str(self.__title_font_size)+'sp', markup=True,
                      size_hint=[None, None])
        title.text_size = ((Window.width * .9), None)
        title.texture_update()
        title.size = [Window.width, title.texture_size[1]]
        theight = title.height * 2
        counter = 0
        start_index = 0
        end_index = 0
        for i in range(page_index, 0, -1):
            start_index = i
            if counter == 15:
                counter = 0
                break
            else:
                counter += 1
        counter = 0
        for j in range(page_index, len(self.__pages_counter)):
            end_index = j
            if counter == 15:
                counter = 0
                break
            else:
                counter += 1
        counter = 0

        def paging(k):
            nonlocal counter, height, title, pages, theight
            p = self.__text[k]
            page = Label(font_size=self.__font_size, markup=True, size_hint=[None, None])
            page.text_size = ((Window.width * .9), None)
            page.halign = p.get_align()
            page.color = self.__text_color
            pheight = 0
            if p.get_tag() == 'image':
                ik = BytesIO(base64.standard_b64decode(p.get_text()))
                ik = CoreImage(ik, ext='jpeg')
                koff = float(ik.height / ik.width)
                w = 0
                h = 0
                if ik.height > Window.height:
                    h = Window.height * 0.7
                    w = float(h * koff)
                if ik.width > Window.width and w > Window.width:
                    w = Window.width * 0.7
                    h = float(w * koff)
                page = BookImage(width=w, height=h, texture=ik.texture)
                pheight = theight + h
                print(pheight)
            else:
                page.text = p.get_text()
                page.texture_update()
                page.size = [Window.width, page.texture_size[1]]
                pheight = theight + page.texture_size[1]
            if pages == []:
                layout = StackLayout()
                layout.id = str(self.__pages_counter.index(k))
                layout.add_widget(page)
                pages.append(layout)
            else:
                for child in pages[counter].children:
                    pheight += child.height
                if pheight < height:
                    pages[counter].add_widget(page)
                elif pheight >= height:
                    layout = StackLayout()
                    layout.id = str(self.__pages_counter.index(k))
                    layout.add_widget(page)
                    pages.append(layout)
                    counter += 1
                else:
                    print('oops')
        start_index -= 1 if start_index != 0 else start_index
        if end_index == len(self.__pages_counter)-1:
            pl = list(map(paging, range(self.__pages_counter[start_index], len(self.__text))))
        else:
            pl = list(map(paging, range(self.__pages_counter[start_index], self.__pages_counter[end_index+1])))
        #print("PAGES %s" % len(self.__pages_counter))
        del pl
        return pages

    def get_pages(self):
        return self.__pages

    def get_coverpage(self):
        return self.__coverpage

    def get_pages_counter(self):
        return self.__pages_counter

    def get_last_index(self):
        return int(self.__last_index)

    def get_last_page(self):
        for v in self.__pages_counter:
            if v >= self.__last_index:
                return self.__pages_counter.index(v)

    def get_path(self):
        return self.__path


#########################################
class MainApp(App):
    theme_cls = ThemeManager()
    # settings_cls = AppSettings
    nav_drawer = ObjectProperty()

    def build_config(self, config):
        config.setdefaults('section1', {
            'font': 'Times New Roman',
            'font_size': '14',
            'bg_color': 'White'
        })

    def build_settings(self, settings):
        json_data = sett.json_d
        settings.add_json_panel('Settings',
                                self.config, data=json_data)

    def build(self):
        self.nav_drawer = AppNavDraw()
        self.nav_drawer.ids.fcolor.text = 'Колір фону: %s' % self.config.get('section1', 'bg_color')
        self.nav_drawer.ids.fsize.text = 'Розмір кегля: %s' % self.config.get('section1', 'font_size')
        self.nav_drawer.ids.font.text = 'Кегель: %s' % self.config.get('section1', 'font')
        return Main()


##########################
class CoverPage(ButtonBehavior, RectangularRippleBehavior, FloatLayout):
    text = ObjectProperty()
    texture = ObjectProperty()
    source = ObjectProperty()
    index = NumericProperty()
    #def __init__(self, **kwargs):
     #   super(TestPage,self).__init__(**kwargs)
        #self.source = 'bg.png'
    #def on_press(self):
     #   print('click')


##############################################
class BookImage(Image):
    w = NumericProperty()
    h = NumericProperty()

    def __init__(self, width=0, height=0, texture=None):
        self.w = width
        self.h = height
        self.width = self.w
        self.height = self.h
        self.texture = texture
        super(BookImage, self).__init__()
############################################
class MenuItem(MDMenuItem):
    key = StringProperty()

    def on_release(self):
        App.get_running_app().root.config_changes(self.key, self.text)

#########################################
class AppNavDraw(NavigationDrawer):

    def add_widget(self, widget, index=0):
        if issubclass(widget.__class__, BaseListItem):
            self._list.add_widget(widget, index)
        else:
            super(AppNavDraw, self).add_widget(widget, index)


##########################################
class TPanel(ToolsPanel):
    max = NumericProperty(100)
    text = StringProperty('1/2000')
    value = NumericProperty(0)
    new_page = ObjectProperty()
    icon = ObjectProperty()


###########################################
class BookNavDraw(NavigationDrawer):
    pass


#################################
class RScreen(Gesture):
    pass

##########################################


class LoadDialog(BoxLayout):
    pass

#########################################




if __name__ == '__main__':
    MainApp().run()
