# Nothing really to examine here, just utility code

from collections import namedtuple
from os import name
from pathlib import Path
import json

def parse_json(filepath: Path, class_name: str, class_fields: str):
   with open(filepath, 'r') as f:
      data_dict = json.load(f)
      return namedtuple(class_name, class_fields)(**data_dict)
