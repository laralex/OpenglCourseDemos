import sys, os

import imgui
import imgui.integrations.glfw

# Base class for lecture and homework demos
class BaseDemo:
    def __init__(self, ui_defaults):
        self.ui_defaults = ui_defaults
        self.is_loaded = False

    @property
    def demo_id(self) -> str:
        path = os.path.abspath(sys.modules[self.__class__.__module__].__file__)
        folder_name = os.path.normpath(path).split(os.path.sep)[-2]
        return folder_name

    def keyboard_callback(self, window, key, scancode, action, mods):
        pass

    def mouse_button_callback(self, window, button, action, mods):
        pass

    def mouse_scroll_callback(self, window, xoffset, yoffset):
        pass

    def window_size_callback(self, window, width, height):
        pass

    def render_frame(self, width, height, global_time_sec, delta_time_sec):
        pass

    def render_ui(self):
        pass

    def load(self, window):
        pass

    def unload(self):
        pass