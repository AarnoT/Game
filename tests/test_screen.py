"""Module for the TestScreen class."""

import os.path
import sys
import unittest

import pygame as pg
pg.init()

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(path))
import modules.screen as sc

class TestScreen(unittest.TestCase):
    """Tests for screen.py."""

    def test_draw_from_queue(self):
        """Assert draw_queue is emptied."""
        for n in range(20):
            sc.draw_queue.append({'layer' : 0, 'surf' : pg.Surface((50, 50)),
                                  'pos' : (100, 100)})
            sc.draw_queue.append({'layer' : 100, 'func' : lambda x:x,
                                  'args' : (5,)})
        sc.draw_from_queue(sc.draw_queue)
        self.assertEqual(len(sc.draw_queue), 0)


if __name__ == '__main__':
    unittest.main()

