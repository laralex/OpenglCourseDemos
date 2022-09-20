import argparse
from src.demos_loader import DemosLoader
from src.common.window import *

from src.common import defines
from OpenGL.GL import *

def parse_arguments():
    parser = argparse.ArgumentParser(prog='CourseDemos', description='OpenGL ISP course demos and homeworks')
    parser.add_argument('startup_demo', nargs='?', default='L01_7_julia',
                    help='Directory of the demo that will show up first (helps to debug)')
    parser.add_argument('--nogui', dest='use_gui', action='store_false')
    return parser.parse_args()

def main():
    args = parse_arguments()

    # GLFW is cross platform library for creating and interacting with windows
    if not glfw.init():
        raise SystemError("Can't initialize windowing library GLFW")

    try:
        window = glfw_create_window('OpenGL Course Demos', window_size=(800, 600))

        # OpenGL commands can be called from one and only thread
        # this commands marks the current thread as the drawing one
        glfw.make_context_current(window)

        print('> GPU Vendor:', glGetString(GL_VENDOR))
        print('> GPU Configuration', glGetString(GL_RENDERER))

        loader = DemosLoader()
        loader.load(window, use_gui=args.use_gui, startup_demo_id=args.startup_demo)
        loader.render_loop(window)
    finally:
        del loader
        glfw.terminate()

if __name__ == "__main__":
   main()