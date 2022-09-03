from ..all_demos import Demo
from OpenGL.GL import *
import math

class Lecture01_ColorDemo(Demo):
    def __init__(self):
        super().__init__(ui_defaults=None)

    def render_frame(self, width, height, global_time_sec, delta_time_sec):
        # oscillating values between 0 and 1
        red   = (math.sin(1.29*global_time_sec) + 1.0) * 0.5
        green = (math.sin(1.51*global_time_sec) + 1.0) * 0.5
        blue  = (math.sin(1.37*global_time_sec) + 1.0) * 0.5
        glClearColor(red,green,blue,1)
        glClear(GL_COLOR_BUFFER_BIT)


