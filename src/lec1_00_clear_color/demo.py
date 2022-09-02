from ..all_demos import Demo
from OpenGL.GL import *

class Lecture01_ColorDemo(Demo):
    def __init__(self):
        super().__init__(ui_defaults=None)

    def render_frame(self, window, width, height):
        glClearColor(1,0,0,1)
        glClear(GL_COLOR_BUFFER_BIT)


