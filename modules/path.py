"""Module for storing file paths."""

import os.path

PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

IMAGE_PATH = os.path.join(PATH, 'images')
LEVEL_PATH = os.path.join(PATH, 'levels')
TEXT_PATH = os.path.join(PATH, 'text')

