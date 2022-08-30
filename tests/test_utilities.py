import unittest
import os
import pathlib

from src.common import parse_json

class TestUtilities(unittest.TestCase):
    def test_json_parsing(self):
        demos_dir = pathlib.Path.cwd()/'src'/'demos'
        self.assertTrue(os.path.exists(demos_dir))
        for subdir_name in os.listdir(demos_dir):
            subdir = os.path.join(demos_dir, subdir_name)
            if not os.path.isdir(subdir):
                continue

            ui_defaults_json = os.path.join(subdir, 'ui_defaults.json')
            if not os.path.exists(ui_defaults_json):
                continue
            fields = ["screen_width", "screen_height"]
            ui_defaults = parse_json.parse_json(ui_defaults_json, "UiLecture1", fields)
            for field in fields:
                self.assertIn(field, ui_defaults.__dir__())