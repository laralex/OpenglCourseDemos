from functools import partial
from typing import OrderedDict
from .common.window import *
import sys, os


class Demo:
    def __init__(self, ui_defaults):
        self.ui_defaults = ui_defaults

    @property
    def demo_id(self) -> str:
        path = os.path.abspath(sys.modules[self.__class__.__module__].__file__)
        folder_name = os.path.normpath(path).split(os.path.sep)[-2]
        return folder_name

    def keyboard_callback(self, window, key, scancode, action, mods):
        print('KEY', key, scancode, action, mods)

    def mouse_button_callback(self):
        pass

    def mouse_scroll_callback(self):
        pass

    def render_frame(self, window):
        pass

    def load(self, window):
        glfw_set_input_callbacks(window=window,
            keyboard_callback=self.keyboard_callback,
            mouse_button_callback=self.mouse_button_callback,
            mouse_scroll_callback=self.mouse_scroll_callback)

class ProxyDemo(Demo):
    def __init__(self, ui_defaults, startup_demo_id):
        super().__init__(ui_defaults=ui_defaults)
        self.register_all_demos()
        self.current_demo_idx = 0
        for idx, (demo_id, _) in enumerate(self.demos):
            if demo_id == startup_demo_id:
                self.current_demo_idx = idx

    @property
    def current_demo(self):
        return self.demos[self.current_demo_idx][1]

    @property
    def current_demo_id(self):
        return self.demos[self.current_demo_idx][0]

    def keyboard_callback(self, window, key, scancode, action, mods):
        changed = False
        if (key, action) == (glfw.KEY_LEFT_BRACKET, glfw.PRESS):
            self.current_demo_idx -= 1
            changed = True
        if (key, action) == (glfw.KEY_RIGHT_BRACKET, glfw.PRESS):
            self.current_demo_idx += 1
            changed = True

        if changed:
            self.current_demo_idx = (self.current_demo_idx + len(self.demos)) % (len(self.demos))
        else:
            self.current_demo.keyboard_callback(window, key, scancode, action, mods)

    def register_all_demos(self):
        from .lec1_01_triangle.demo import Lecture01_TriangleDemo
        from .lec1_02_cube.demo import Lecture01_CubeDemo
        from .lec2.demo import Lecture02_Demo

        classes = [Lecture01_TriangleDemo, Lecture01_CubeDemo, Lecture02_Demo]
        self.demos = []
        for demo_class in classes:
            demo = demo_class()
            self.demos.append( (demo.demo_id, demo) )

    def render_loop(self, window):
        # GLFW allows multiple windows, select this window as active
        glfw.make_context_current(window)

        # infinite render loop, until the window is requested to close
        while not glfw.window_should_close(window):
            self.current_demo.render_frame(window) # draw to memory
            glfw.swap_buffers(window) # flush what was drawn to the screen pixels
            glfw.poll_events()        # handle keyboard/mouse/window events



