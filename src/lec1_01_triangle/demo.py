from dataclasses import dataclass
from ..common import parse_json, window
from ..all_demos import Demo
from ..common import defines
from OpenGL.GL import *

@dataclass
class UiDefaults:
    color: int

class Lecture01_TriangleDemo(Demo):

    def __init__(self):
        #ui_defaults = parse_json.parse_json('ui_defaults.json', UiDefaults.__name__, ['color'])
        super().__init__(ui_defaults=None)

    def render_frame(self, window, width, height):
        glClearColor(1,0,0,1)
        glClear(GL_COLOR_BUFFER_BIT)


