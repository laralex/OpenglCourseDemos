from dataclasses import dataclass
from ..common import parse_json, window
from ..demo import Demo

@dataclass
class UiDefaults:
    color: int

class Lecture01_TriangleDemo(Demo):

    def __init__(self):
        #ui_defaults = parse_json.parse_json('ui_defaults.json', UiDefaults.__name__, ['color'])
        super().__init__(ui_defaults=None)


