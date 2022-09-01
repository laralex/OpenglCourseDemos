import argparse
from src.all_demos import ProxyDemo
from src.common.window import *
import src.common.gl_texture

from src.common import defines
from OpenGL.GL import *

def parse_arguments():
    parser = argparse.ArgumentParser(prog='CourseDemos', description='OpenGL ISP course demos and homeworks')
    parser.add_argument('startup_demo', nargs='?', default='lec1_01_triangle',
                    help='Directory of the demo that will show up first (helps to debug)')
    return parser.parse_args()

def main():
    args = parse_arguments()

    # GLFW is cross platform library for creating and interacting with windows
    if not glfw.init():
        raise SystemError("Can't initialize windowing library GLFW")

    try:
        window = glfw_create_window('OpenGL Course Demos', window_size=(512, 512))

        # OpenGL commands can be called from one and only thread
        # this commands marks the current thread as the drawing one
        glfw.make_context_current(window)

        print('> GPU Vendor:', glGetString(GL_VENDOR))
        print('> GPU Configuration', glGetString(GL_RENDERER))

        loader = ProxyDemo(ui_defaults=None, startup_demo_id=args.startup_demo)
        loader.load(window)
        loader.render_loop(window)
    finally:
        glfw.terminate()

if __name__ == "__main__":
   main()