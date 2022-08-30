import argparse
from src.demos.demo import register_all_demos
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
        demos = register_all_demos()
        print(demos.keys())
        current_demo = demos[args.startup_demo]
        current_demo.load(window)
        glfw_render_loop(
            window=window,
            render_frame_func=lambda window: None)

if __name__ == "__main__":
   main()