from .common.window import *
import sys, os

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

    def render_frame(self, window, width, height):
        pass

    def load(self, window):
        self.is_loaded = True

    def unload(self):
        self.is_loaded = False

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
            self.current_demo.load(window)
        else:
            self.current_demo.keyboard_callback(window, key, scancode, action, mods)

    def mouse_button_callback(self, window, button, action, mods):
        super().mouse_button_callback(window, button, action, mods)
        self.current_demo.mouse_button_callback(window, button, action, mods)

    def mouse_scroll_callback(self, window, xoffset, yoffset):
        super().mouse_scroll_callback(window, xoffset, yoffset)
        self.current_demo.mouse_scroll_callback(window, xoffset, yoffset)

    def register_all_demos(self):
        from .lec1_00_clear_color.demo   import Lecture01_ColorDemo
        from .lec1_01_triangle.demo import Lecture01_TriangleDemo
        from .lec1_02_cube.demo     import Lecture01_CubeDemo

        classes = [Lecture01_ColorDemo, Lecture01_TriangleDemo, Lecture01_CubeDemo]
        self.demos = []
        for demo_class in classes:
            demo = demo_class()
            self.demos.append( (demo.demo_id, demo) )

    def render_loop(self, window):
        # infinite render loop, until the window is requested to close
        while not glfw.window_should_close(window):
            width, height = glfw.get_framebuffer_size(window)
            if self.current_demo.is_loaded:
                self.current_demo.render_frame(window, width, height) # draw to memory
                glfw.swap_buffers(window) # flush from memory to the screen pixels
            glfw.poll_events()        # handle keyboard/mouse/window events

    def load(self, window):
        self.current_demo.load(window)
        glfw_set_input_callbacks(window=window,
            keyboard_callback=self.keyboard_callback,
            mouse_button_callback=self.mouse_button_callback,
            mouse_scroll_callback=self.mouse_scroll_callback)



