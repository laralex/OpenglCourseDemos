from functools import partial
from .common.window import *
import sys, os

def register_all_demos():
    from .lec1_01_triangle.demo import Lecture01_TriangleDemo

    classes = [Lecture01_TriangleDemo]
    demos = {}
    for demo_class in classes:
        demo = demo_class()
        demos[demo.demo_id()] = demo

    return demos

class Demo:
    def demo_id(self) -> str:
        path = os.path.abspath(sys.modules[self.__class__.__module__].__file__)
        folder_name = os.path.normpath(path).split(os.path.sep)[-2]
        return folder_name

    def __init__(self, ui_defaults):
        self.ui_defaults = ui_defaults

    def keyboard_callback(self, window, key, scancode, action, mods):
        pass

    def mouse_button_callback(self):
        pass

    def mouse_scroll_callback(self):
        pass

    def load(self, window):
        glfw_set_input_callbacks(window=window,
            keyboard_callback=partial(self.keyboard_callback, self),
            mouse_button_callback=partial(self.mouse_button_callback, self),
            mouse_scroll_callback=partial(self.mouse_scroll_callback, self))

