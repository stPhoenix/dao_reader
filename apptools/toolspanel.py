# -*- coding: utf-8 -*-
from kivy.lang import Builder
from  kivy.core.window import Window
from kivymd.elevationbehavior import RectangularElevationBehavior
from kivymd.theming import ThemableBehavior

from apptools.verticalslider import VerticalSlidingPanel

Builder.load_string('''
<ToolsPanel>
    elevation: 0
    canvas:
        Color:
            rgba: root.theme_cls.bg_light
        Rectangle:
            size: root.size
            pos: root.pos
''')


class ToolsPanel(VerticalSlidingPanel, ThemableBehavior, RectangularElevationBehavior):

    def resize(self, obj, width, height):
        self.y = Window.height if self.side == 'up' else -1 * self.height

    def __init__(self):
        Window.bind(on_resize=self.resize)
        super(ToolsPanel, self).__init__()