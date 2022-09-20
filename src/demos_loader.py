from contextlib import suppress
import time
import sys, os
from .common.window import *
from .common.defines import *
from OpenGL.GL import *
import inspect

import imgui
import imgui.integrations.glfw

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

    def render_ui(self):
        imgui.begin("", True)
        imgui.text('FPS: %.2f' % imgui.get_io().framerate)
        imgui.end()

    def load(self, window):
        pass

    def unload(self):
        pass


class ImguiWrapper:
    def __init__(self, glfw_window, use_gui=True):
        self.imgui_impl = None
        self.use_gui = use_gui
        if use_gui:
            imgui.create_context()
            self.imgui_impl = imgui.integrations.glfw.GlfwRenderer(glfw_window)
            io = imgui.get_io()
            io.font_global_scale *= 1.3

    def render_ui(self, other_demo, current_polygon_mode, *args):
        if self.use_gui:
            # setting polygon mode to fill, otherwise imgui is rendered 
            # with lines/points as well as the demos
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            imgui.new_frame()
            other_demo.render_ui(*args)
            imgui.render()
            self.imgui_impl.render(imgui.get_draw_data())
            imgui.end_frame()

            glPolygonMode(GL_FRONT_AND_BACK, current_polygon_mode)

    def process_inputs(self):
        if self.use_gui:
            self.imgui_impl.process_inputs()

    def __del__(self):
        if self.use_gui:
            self.imgui_impl.shutdown()


# A wrapper class to import all separate demos
# and render them in one window with convenient switching between demos
class DemosLoader:
    def __init__(self):
        self.register_all_demos()

        self.windowed_position = None
        self.windowed_size = None

        self.draw_modes = [GL_FILL, GL_LINE, GL_POINT]
        self.current_polygon_draw_mode_idx = 0
        self.current_polygon_draw_mode = self.draw_modes[self.current_polygon_draw_mode_idx]

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
        if (key, action) == (glfw.KEY_P, glfw.PRESS):
            self.current_polygon_draw_mode_idx += 1
            self.current_polygon_draw_mode_idx %= len(self.draw_modes)
            self.current_polygon_draw_mode = self.draw_modes[self.current_polygon_draw_mode_idx]
            glLineWidth(2)
            glPointSize(2)
            glPolygonMode(GL_FRONT_AND_BACK, self.current_polygon_draw_mode)

        if changed_demo:
            running_demo.unload()
            self.current_demo_idx = (self.current_demo_idx + len(self.demos)) % (len(self.demos))
            self.load_current_demo(window)
        else:
            self.current_demo.keyboard_callback(window, key, scancode, action, mods)

    def mouse_button_callback(self, window, button, action, mods):
        self.current_demo.mouse_button_callback(window, button, action, mods)

    def mouse_scroll_callback(self, window, xoffset, yoffset):
        self.current_demo.mouse_scroll_callback(window, xoffset, yoffset)

    def window_size_callback(self, window, width, height):
        glViewport(0, 0, width, height)
        self.current_demo.window_size_callback(window, width, height)

    def register_all_demos(self):
        from .L01_0_clear_color.demo          import Lecture01_ColorDemo
        from .L01_1_triangle.demo             import Lecture01_TriangleDemo
        from .L01_2_aspect_ratio.demo         import Lecture01_AspectRatioDemo
        from .L01_3_texture.demo              import Lecture01_TextureDemo
        from .L01_4_transform.demo            import Lecture01_TransformDemo
        from .L01_5_transform_matrix.demo     import Lecture01_TransformMatrixDemo
        from .L01_6_mandelbrot.demo           import Lecture01_MandelbrotDemo
        from .L01_7_julia.demo                import Lecture01_JuliaDemo
        from .L02_1_cube.demo                 import Lecture02_CubeDemo
        from .L02_2_cube_indexed.demo         import Lecture02_CubeIndexedDemo
        from .L02_3_cube_interleaved.demo     import Lecture02_CubeInterleavedDemo
        from .L02_4_mesh.demo                 import Lecture02_MeshDemo
        from .L02_5_orthographic.demo         import Lecture02_OrthographicDemo

        classes = [
            Lecture01_ColorDemo,
            Lecture01_TriangleDemo,
            Lecture01_AspectRatioDemo,
            Lecture01_TextureDemo,
            Lecture01_TransformDemo,
            Lecture01_TransformMatrixDemo,
            Lecture01_MandelbrotDemo,
            Lecture01_JuliaDemo,
            Lecture02_CubeDemo,
            Lecture02_CubeIndexedDemo,
            Lecture02_CubeInterleavedDemo,
            Lecture02_MeshDemo,
            Lecture02_OrthographicDemo,
        ]

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

            current_demo = self.current_demo
            if current_demo.is_loaded:
                delta_time_sec = max(global_time_sec - last_time_sec, 1e-5)
                current_demo.render_frame(width, height, global_time_sec, delta_time_sec) # draw to memory
                self.gui_wrapper.render_ui(current_demo, current_polygon_mode=self.current_polygon_draw_mode)
                glfw.swap_buffers(window) # flush from memory to the screen pixels
                last_time_sec = global_time_sec

            glfw.poll_events() # handle keyboard/mouse/window events
            self.gui_wrapper.process_inputs()


    def load(self, window, use_gui, startup_demo_id):
        # select startup demo index
        self.current_demo_idx = -1
        for idx, (demo_id, _) in enumerate(self.demos):
            if demo_id == startup_demo_id:
                self.current_demo_idx = idx
        if self.current_demo_idx == -1:
            print(f'> Failed to find demo: {startup_demo_id}. Loading the first available demo.')
            self.current_demo_idx = 0

        self.gui_wrapper = ImguiWrapper(window, use_gui)
        self.load_current_demo(window)

        glfw_set_input_callbacks(window=window,
            keyboard_callback=self.keyboard_callback,
            mouse_button_callback=self.mouse_button_callback,
            mouse_scroll_callback=self.mouse_scroll_callback)
        glfw_set_window_callbacks(window,
            window_size_callback=self.window_size_callback)





