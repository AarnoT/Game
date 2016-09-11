"""For tests related to 'game.py'."""

import os.path
import sys
import unittest
from datetime import datetime, timedelta

import pygame as pg
pg.init()

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(path))
from game import Game


class TestGame(unittest.TestCase):
    """For tests related to Game."""

    def test_quit_event(self):
        """Game should stop running after 'QUIT' is posted."""
        Game.running = True
        pg.event.post(pg.event.Event(pg.QUIT, {}))
        Game.event_loop()
        self.assertIs(Game.running, False)

    def test_keydown_event(self):
        """Game should stop after escape is pressed."""
        Game.running = True
        pg.event.post(pg.event.Event(pg.KEYDOWN, {'key' : pg.K_ESCAPE}))
        Game.event_loop()
        self.assertIs(Game.running, False)

    def test_video_resize_event(self):
        """Assert game resizes to the correct size and flags."""
        pg.event.post(pg.event.Event(
            pg.VIDEORESIZE, {'size' : (300, 300), 'flags' : pg.RESIZABLE}))
        Game.event_loop()
        self.assertTupleEqual((300, 300), pg.display.get_surface().get_size())
        # 0x00000010 is the bitmask for the 'RESIZABLE' flag.
        self.assertEqual(
            pg.RESIZABLE, pg.display.get_surface().get_flags() & 0x00000010)

    def test_event_queue(self):
        """Event queue should be empty after looping through it."""
        Game.event_loop()
        self.assertEqual(len(pg.event.get()), 0)

    def test_resize(self):
        """Try different input resolutions."""
        Game.resize(res=(800, 600))
        Game.resize(res=(1980, 1080))


if __name__ == '__main__':
    unittest.main()

