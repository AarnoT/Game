"""For tests related to 'button.py'."""

import os.path
import sys
import unittest

import pygame as pg
pg.init()

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(path))
from modules.button import Button, ButtonSet


class TestButtonSet(unittest.TestCase):
    """Tests for 'ButtonSet'."""

    def setUp(self):
        """Set up the button set."""
        b1 = Button(pg.Rect(100, 100, 100, 100), '123', lambda x: x * 3)
        b2 = Button(pg.Rect(200, 200, 100, 100), '456', lambda x: x - 3)
        b3 = Button(pg.Rect(300, 300, 100, 100), '789', lambda x: x + 3)
        self.set = ButtonSet([b1, b2, b3])

    def test_next_id(self):
        """Assert next_id is equal to the button set length."""
        self.assertEqual(len(self.set.buttons), self.set.next_id)

    def test_toggle(self):
        """Assert all buttons in the set are in the same state."""
        self.set.active = False
        self.assertIs(
            all(b.active == self.set.active for b in self.set.buttons), False)
        self.set.toggle()
        self.assertIs(
            all(b.active == self.set.active for b in self.set.buttons), True)

    def test_scale(self):
        """Assert buttons scale properly."""
        rects = [button.rect.width for button in self.set.buttons]
        self.set.scale(0.5)
        new_rects = [button.rect.width for button in self.set.buttons]
        for rect, new_rect in zip(rects, new_rects):
            self.assertLess(new_rect, rect)

    def test_highlighted_button(self):
        """Assert 'highlighted_button' is a button."""
        self.set.highlighted_id = 0
        self.assertIsInstance(self.set.highlighted_button, Button)


if __name__ == '__main__':
    unittest.main()

