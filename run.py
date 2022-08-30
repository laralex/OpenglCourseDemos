import argparse
from src.demos.all_demos import ProxyDemo
from src.demos.common.window import *

def parse_arguments():
    parser = argparse.ArgumentParser(prog='CourseDemos', description='OpenGL ISP course demos and homeworks')
    parser.add_argument('startup_demo', nargs='?', default='lec1_01_triangle',
                    help='Directory of the demo that will show up first (helps to debug)')
    return parser.parse_args()

def main():
    args = parse_arguments()

    with GlfwInstance():
        window = glfw_create_window('OpenGL Course Demos', window_size=(512, 512))
        loader = ProxyDemo(ui_defaults=None, startup_demo_id=args.startup_demo)
        loader.load(window)
        loader.render_loop(window)

if __name__ == "__main__":
   main()