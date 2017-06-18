from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty

Builder.load_string('''
<TestWidget>:
    canvas:
        Color:
            rgba: app.theme_cls.primary_color
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        text:root.title



''')


class TestWidget(FloatLayout):
    title = StringProperty()

    def __init__(self, *args, **kwargs):
        super(TestWidget, self).__init__(*args, **kwargs)