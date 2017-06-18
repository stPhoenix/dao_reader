from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty, BooleanProperty
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivymd.label import MDLabel
import json
from kivy.config import ConfigParser
import os
from kivy.compat import string_types, text_type
from kivymd.list import MDList, TwoLineIconListItem, IRightBodyTouch

Builder.load_string('''
#:import TwoLineListItem kivymd.list.OneLineListItem
#:import MDList kivymd.list.MDList
<AppSettingItem>:
    content: content
    text: root.title or ''
    secondary_text: root.desc or ''
    SettingsContent:
        id: content


<AppSettings>:
    #orientation: 'horizontal'
    canvas:
        Color:
            rgba: app.theme_cls.primary_color
        Rectangle:
            pos: self.pos
            size: self.size
'''
                    )


##########################3
class SettingsContent(IRightBodyTouch, BoxLayout):
    pass


##################################
class SettingsTitle(MDLabel):
    title = MDLabel.text
    panel = ObjectProperty(None)


#################################################
class AppSettings(MDList):
    def __init__(self, *args, **kwargs):
        self._types = {}
        super(AppSettings, self).__init__(*args, **kwargs)
        self.register_type('string', SettingString)
        self.register_type('numeric', SettingNumeric)
        self.register_type('options', SettingOptions)
        self.register_type('title', SettingsTitle)
        config = None
        try:
            config = ConfigParser.get_configparser('app')
        except KeyError:
            config = None
        if config is None:
            config = ConfigParser(name='app')
        self.config = config
    # def __init__(self, *args, **kwargs):
    #     global main_kv
    #     #Builder.load_string(main_kv)
    #     self.interface_cls = SettingsInterface
    #     super(AppSettings, self).__init__(*args, **kwargs)
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            super(AppSettings, self).on_touch_down(touch)
            return True

    def register_type(self, tp, cls):
        '''Register a new type that can be used in the JSON definition.
        '''
        self._types[tp] = cls

    def on_close(self, *args):
        pass

    def on_config_change(self, config, section, key, value):
        pass

    def create_json_panel(self, filename=None, data=None):
        '''Create new :class:`SettingsPanel`.
        .. versionadded:: 1.5.0
        Check the documentation of :meth:`add_json_panel` for more information.
        '''
        if filename is None and data is None:
            raise Exception('You must specify either the filename or data')
        if filename is not None:
            with open(filename, 'r') as fd:
                data = json.loads(fd.read())
        else:
            data = json.loads(data)
        if type(data) != list:
            raise ValueError('The first element must be a list')

        for setting in data:
            # determine the type and the class to use
            if not 'type' in setting:
                raise ValueError('One setting are missing the "type" element')
            ttype = setting['type']
            print(ttype)
            cls = self._types.get(ttype)
            if cls is None:
                raise ValueError(
                    'No class registered to handle the <%s> type' %
                    setting['type'])

            # create a instance of the class, without the type attribute
            del setting['type']
            str_settings = {}
            for key, item in setting.items():
                print('KEY: %s ITEM: %s'%(key, item))
                str_settings[str(key)] = item

            instance = cls(panel=self, **str_settings)##!!!!!!!!!!!!!!!!!!!!!!!THIS

            # instance created, add to the panel
            self.add_widget(instance)

        #return panel########??!!!!!!!!!!!!THIS

    def get_value(self, section, key):
        config = self.config
        if not config:
            return
        return config.get(section, key)

    def set_value(self, section, key, value):
        current = self.get_value(section, key)
        if current == value:
            return
        config = self.config
        if config:
            config.set(section, key, value)
            config.write()
        ###TODO ADD DISPATCH ON CONFIG_CHANGE

#########################


class AppSettingItem(TwoLineIconListItem):
    title = StringProperty('<No title set>')
    desc = StringProperty(None, allownone=True)
    disabled = BooleanProperty(False)
    section = StringProperty(None)
    key = StringProperty(None)
    value = ObjectProperty(None)
    panel = ObjectProperty(None)
    content = ObjectProperty(None)
    selected_alpha = NumericProperty(0)

    __events__ = ('on_release', )

    def __init__(self, **kwargs):
        super(AppSettingItem, self).__init__(**kwargs)
        self.value = self.panel.get_value(self.section, self.key)

    def add_widget(self, *largs):
        pass
        #if self.content is None:
         #   return super(AppSettingItem, self).add_widget(*largs)
        #return self.content.add_widget(*largs)

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return
        if self.disabled:
            return
        touch.grab(self)
        self.selected_alpha = 1
        return super(AppSettingItem, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.dispatch('on_release')
            Animation(selected_alpha=0, d=.25, t='out_quad').start(self)
            return True
        return super(AppSettingItem, self).on_touch_up(touch)

    def on_release(self):
        pass

    def on_value(self, instance, value):
        if not self.section or not self.key:
            return
        # get current value in config
        panel = self.panel
        if not isinstance(value, string_types):
            value = str(value)
        panel.set_value(self.section, self.key, value)

###############################################

class SettingString(AppSettingItem):
    '''Implementation of a string setting on top of a :class:`SettingItem`.
    It is visualized with a :class:`~kivy.uix.label.Label` widget that, when
    clicked, will open a :class:`~kivy.uix.popup.Popup` with a
    :class:`~kivy.uix.textinput.Textinput` so the user can enter a custom
    value.
    '''

    popup = ObjectProperty(None, allownone=True)
    '''(internal) Used to store the current popup when it's shown.
    :attr:`popup` is an :class:`~kivy.properties.ObjectProperty` and defaults
    to None.
    '''

    textinput = ObjectProperty(None)
    '''(internal) Used to store the current textinput from the popup and
    to listen for changes.
    :attr:`textinput` is an :class:`~kivy.properties.ObjectProperty` and
    defaults to None.
    '''

    def on_panel(self, instance, value):
        if value is None:
            return
        #self.fbind('on_release', self._create_popup)

    def _dismiss(self, *largs):
        if self.textinput:
            self.textinput.focus = False
        if self.popup:
            self.popup.dismiss()
        self.popup = None

    def _validate(self, instance):
        self._dismiss()
        value = self.textinput.text.strip()
        self.value = value

    # def _create_popup(self, instance):
    #     # create popup layout
    #     content = BoxLayout(orientation='vertical', spacing='5dp')
    #     popup_width = min(0.95 * Window.width, dp(500))
    #     self.popup = popup = Popup(
    #         title=self.title, content=content, size_hint=(None, None),
    #         size=(popup_width, '250dp'))
    #
    #     # create the textinput used for numeric input
    #     self.textinput = textinput = TextInput(
    #         text=self.value, font_size='24sp', multiline=False,
    #         size_hint_y=None, height='42sp')
    #     textinput.bind(on_text_validate=self._validate)
    #     self.textinput = textinput
    #
    #     # construct the content, widget are used as a spacer
    #     content.add_widget(Widget())
    #     content.add_widget(textinput)
    #     content.add_widget(Widget())
    #     content.add_widget(SettingSpacer())
    #
    #     # 2 buttons are created for accept or cancel the current value
    #     btnlayout = BoxLayout(size_hint_y=None, height='50dp', spacing='5dp')
    #     btn = Button(text='Ok')
    #     btn.bind(on_release=self._validate)
    #     btnlayout.add_widget(btn)
    #     btn = Button(text='Cancel')
    #     btn.bind(on_release=self._dismiss)
    #     btnlayout.add_widget(btn)
    #     content.add_widget(btnlayout)
    #
    #     # all done, open the popup !
    #     popup.open()

##############################################

#############################################
class SettingNumeric(SettingString):
    '''Implementation of a numeric setting on top of a :class:`SettingString`.
    It is visualized with a :class:`~kivy.uix.label.Label` widget that, when
    clicked, will open a :class:`~kivy.uix.popup.Popup` with a
    :class:`~kivy.uix.textinput.Textinput` so the user can enter a custom
    value.
    '''

    def _validate(self, instance):
        # we know the type just by checking if there is a '.' in the original
        # value
        is_float = '.' in str(self.value)
        self._dismiss()
        try:
            if is_float:
                self.value = text_type(float(self.textinput.text))
            else:
                self.value = text_type(int(self.textinput.text))
        except ValueError:
            return
########################################################

#########################################################

class SettingOptions(AppSettingItem):
    '''Implementation of an option list on top of a :class:`SettingItem`.
    It is visualized with a :class:`~kivy.uix.label.Label` widget that, when
    clicked, will open a :class:`~kivy.uix.popup.Popup` with a
    list of options from which the user can select.
    '''

    options = ListProperty([])
    '''List of all availables options. This must be a list of "string" items.
    Otherwise, it will crash. :)
    :attr:`options` is a :class:`~kivy.properties.ListProperty` and defaults
    to [].
    '''

    popup = ObjectProperty(None, allownone=True)
    '''(internal) Used to store the current popup when it is shown.
    :attr:`popup` is an :class:`~kivy.properties.ObjectProperty` and defaults
    to None.
    '''

    def on_panel(self, instance, value):
        if value is None:
            return
        #self.fbind('on_release', self._create_popup)

    def _set_option(self, instance):
        self.value = instance.text
        self.popup.dismiss()

    # def _create_popup(self, instance):
    #     # create the popup
    #     content = BoxLayout(orientation='vertical', spacing='5dp')
    #     popup_width = min(0.95 * Window.width, dp(500))
    #     self.popup = popup = Popup(
    #         content=content, title=self.title, size_hint=(None, None),
    #         size=(popup_width, '400dp'))
    #     popup.height = len(self.options) * dp(55) + dp(150)
    #
    #     # add all the options
    #     content.add_widget(Widget(size_hint_y=None, height=1))
    #     uid = str(self.uid)
    #     for option in self.options:
    #         state = 'down' if option == self.value else 'normal'
    #         btn = ToggleButton(text=option, state=state, group=uid)
    #         btn.bind(on_release=self._set_option)
    #         content.add_widget(btn)
    #
    #     # finally, add a cancel button to return on the previous panel
    #     content.add_widget(SettingSpacer())
    #     btn = Button(text='Cancel', size_hint_y=None, height=dp(50))
    #     btn.bind(on_release=popup.dismiss)
    #     content.add_widget(btn)
    #
    #     # and open the popup !
    #     popup.open()
##############################################################
class SettingsPanel(GridLayout):
    '''This class is used to contruct panel settings, for use with a
    :class:`Settings` instance or subclass.
    '''

    title = StringProperty('Default title')
    '''Title of the panel. The title will be reused by the :class:`Settings` in
    the sidebar.
    '''

    config = ObjectProperty(None, allownone=True)
    '''A :class:`kivy.config.ConfigParser` instance. See module documentation
    for more information.
    '''

    settings = ObjectProperty(None)
    '''A :class:`Settings` instance that will be used to fire the
    `on_config_change` event.
    '''

    def __init__(self, **kwargs):
        if 'cols' not in kwargs:
            self.cols = 1
        super(SettingsPanel, self).__init__(**kwargs)

    def on_config(self, instance, value):
        if value is None:
            return
        if not isinstance(value, ConfigParser):
            raise Exception('Invalid config object, you must use a'
                            'kivy.config.ConfigParser, not another one !')

    def get_value(self, section, key):
        '''Return the value of the section/key from the :attr:`config`
        ConfigParser instance. This function is used by :class:`SettingItem` to
        get the value for a given section/key.
        If you don't want to use a ConfigParser instance, you might want to
        override this function.
        '''
        config = self.config
        if not config:
            return
        return config.get(section, key)

    def set_value(self, section, key, value):
        current = self.get_value(section, key)
        if current == value:
            return
        config = self.config
        if config:
            config.set(section, key, value)
            config.write()
        settings = self.settings
        if settings:
            settings.dispatch('on_config_change',
                              config, section, key, value)
####################################################################33
