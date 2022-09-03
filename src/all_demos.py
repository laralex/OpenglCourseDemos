from ast import Pass
import time
from .common.window import *
import sys, os
from .common.defines import *
from OpenGL.GL import *
import inspect

# Base class for lecture and homework demos
class Demo:
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

    def load(self, window):
        pass

    def unload(self):
        pass


# A wrapper class to import all separate demos
# and render them in one window with convenient switching between demos
class ProxyDemo(Demo):
    def __init__(self, ui_defaults, startup_demo_id):
        super().__init__(ui_defaults=ui_defaults)
        self.register_all_demos()
        self.current_demo_idx = 0
        for idx, (demo_id, _) in enumerate(self.demos):
            if demo_id == startup_demo_id:
                self.current_demo_idx = idx

        self.windowed_position = None
        self.windowed_size = None

    @property
    def current_demo(self):
        return self.demos[self.current_demo_idx][1]

    @property
    def current_demo_id(self):
        return self.demos[self.current_demo_idx][0]

    def load_current_demo(self, window):
        demo_fp = inspect.getfile(self.current_demo.__class__)
        demo_dp = os.path.dirname(demo_fp)
        print('> Loading demo', demo_dp)
        os.chdir(demo_dp)
        self.current_demo.load(window)
        self.windowed_position = glfw.get_window_pos(window)
        self.windowed_size = glfw.get_window_size(window)
        self.window_size_callback(window, *self.windowed_size)

    def keyboard_callback(self, window, key, scancode, action, mods):
        super().keyboard_callback(window, key, scancode, action, mods)
        changed_demo = False
        running_demo = self.current_demo
        if (key, action) == (glfw.KEY_LEFT_BRACKET, glfw.PRESS):
            # previous demo
            self.current_demo_idx -= 1
            changed_demo = True
        if (key, action) == (glfw.KEY_RIGHT_BRACKET, glfw.PRESS):
            # next demo
            self.current_demo_idx += 1
            changed_demo = True
        if (key, action) == (glfw.KEY_F, glfw.PRESS):
            # toggle fullscreen
            is_fullscreen = glfw_is_fullscreen(window)
            if not is_fullscreen:
                self.windowed_position = glfw.get_window_pos(window)
                self.windowed_size = glfw.get_window_size(window)
            glfw_switch_fullscreen(window, 
            enable_fullscreen=not is_fullscreen,
                window_position=self.windowed_position,
                window_size=self.windowed_size)
        if changed_demo:
            running_demo.unload()
            self.current_demo_idx = (self.current_demo_idx + len(self.demos)) % (len(self.demos))
            self.load_current_demo(window)
        else:
            self.current_demo.keyboard_callback(window, key, scancode, action, mods)

    def mouse_button_callback(self, window, button, action, mods):
        super().mouse_button_callback(window, button, action, mods)
        self.current_demo.mouse_button_callback(window, button, action, mods)

    def mouse_scroll_callback(self, window, xoffset, yoffset):
        super().mouse_scroll_callback(window, xoffset, yoffset)
        self.current_demo.mouse_scroll_callback(window, xoffset, yoffset)

    def window_size_callback(self, window, width, height):
        super().window_size_callback(window, width, height)
        glViewport(0, 0, width, height)
        self.current_demo.window_size_callback(window, width, height)

    def register_all_demos(self):
        from .L01_0_clear_color.demo   import Lecture01_ColorDemo
        from .L01_1_triangle.demo      import Lecture01_TriangleDemo
        from .L01_2_texture.demo       import Lecture01_TextureDemo

        classes = [Lecture01_ColorDemo, Lecture01_TriangleDemo, Lecture01_TextureDemo]
        self.demos = []
        for demo_class in classes:
            demo = demo_class()
            self.demos.append( (demo.demo_id, demo) )

    def render_loop(self, window):
        last_time_sec = float('inf')

        # infinite render loop, until the window is requested to close
        while not glfw.window_should_close(window):
            width, height = glfw.get_framebuffer_size(window)
            global_time_sec = time.time()
            if self.current_demo.is_loaded:
                delta_time_sec = max(global_time_sec - last_time_sec, 1e-5)
                self.current_demo.render_frame(width, height, global_time_sec, delta_time_sec) # draw to memory
                glfw.swap_buffers(window) # flush from memory to the screen pixels
                last_time_sec = global_time_sec
            glfw.poll_events()        # handle keyboard/mouse/window events

    def load(self, window):
        self.load_current_demo(window)
        glfw_set_input_callbacks(window=window,
            keyboard_callback=self.keyboard_callback,
            mouse_button_callback=self.mouse_button_callback,
            mouse_scroll_callback=self.mouse_scroll_callback)
        glfw_set_window_callbacks(window,
            window_size_callback=self.window_size_callback)





