"""Module for the TestLevel class."""

import os.path
import sys
import unittest

import pygame as pg
pg.init()

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(path))
import modules.level as level


class TestLevel(unittest.TestCase):
    """Tests for the Level class."""

    def setUp(self):
        """Create 'Level' instance."""
        self.level = level.Level(os.path.join(path, 'levels', 'level_one.tmx'))

    def test_tile_size(self):
        """Assert tile size is a tuple."""
        self.assertIsInstance(self.level.tile_size, tuple)

    def test_load_tiles(self):
        """Assert enough tiles are loaded."""
        level_size = self.level.level.width * self.level.level.height
        # 'reload' calls load_tiles.
        self.level.reload()
        self.assertGreaterEqual(len(self.level.tiles), level_size)


if __name__ == '__main__':
    unittest.main()

