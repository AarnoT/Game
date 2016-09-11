"""For tests related to 'sprite.py'."""

import os.path
import sys
import unittest
from math import hypot

import pygame as pg
pg.init()

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(path))
import modules.sprite as sprite


class TestSprite(unittest.TestCase):
    """Tests for 'Sprite'."""

    def setUp(self):
        """Create 'Sprite' instance."""
        self.sprite = sprite.Sprite((0, 0), ['guy.png'], [
            'dude1.png', 'dude2.png', 'dude3.png', 'dude2.png'])

    def test_load_frames(self):
        """Assert function returns a list."""
        self.assertIsInstance(self.sprite.load_frames([]), list)

    def test_move(self):
        """Assert sprite moves to the correct position."""
        self.sprite.move((200, 200), 2000)
        self.sprite.update(1000000)
        self.assertTupleEqual(
            (round(self.sprite.x_pos), round(self.sprite.y_pos)), (200, 200))

    def test_sprite_speed(self):
        """Assert speed is equal to max speed."""
        self.sprite.move((500, 500), 2000)
        self.assertEqual(
            hypot(self.sprite.x_vel, self.sprite.y_vel), self.sprite.max_speed)


if __name__ == '__main__':
    unittest.main()

