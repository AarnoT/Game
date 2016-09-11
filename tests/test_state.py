"""For tests related to 'state.py'."""

import os.path
import sys
import unittest

import pygame as pg
pg.init()

path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.join(path))
from modules.state import State, MenuState, WorldState
import modules.state as state


class TestState(unittest.TestCase):
    """Tests for state.State."""

    def test_change_state(self):
        """Assert a user event is posted."""
        State().change_state(MenuState)
        self.assertGreater(len(pg.event.get(pg.USEREVENT)), 0)


class TestMenu(unittest.TestCase):
    """Tests for state.MenuState."""

    def setUp(self):
        """Create 'MenuState' instance."""
        self.state = MenuState(MenuState.create_main_menu())
    
    def test_on_arrow_key(self):
        """Assert highlighted id is correct."""
        self.state.button_set.highlighted_id = 0
        self.state.on_arrow_key('left')
        self.assertEqual(self.state.button_set.highlighted_id, 0)

    def test_create_main_menu(self):
        """Assert return value is an instance of ButtonSet."""
        self.assertIsInstance(MenuState.create_main_menu(), state.ButtonSet)
    
    def test_start_game(self):
        """Assert an user event is posted."""
        MenuState.start_game()
        self.assertGreater(len(pg.event.get(pg.USEREVENT)), 0)
    
    def test_exit_game(self):
        """Assert a quit event is posted."""
        MenuState.exit_game()
        self.assertGreater(len(pg.event.get(pg.QUIT)), 0)


class TestWorld(unittest.TestCase):
    """Tests for state.WorldState."""

    def setUp(self):
        """Create an instance of WorldState."""
        args = (WorldState.level, WorldState.player_anim,
                WorldState.pos_1, WorldState.player_image)
        self.state = WorldState(*args)

    def test_scale(self):
        """Try small and large inputs for scale."""
        self.state.scale(20.0)
        self.state.scale(1.0/40.0)

    def test_scroll(self):
        """Assert scroll is positive and not too large."""
        self.assertGreaterEqual(self.state.scroll, 0)
        level_height = (
            self.state.level.tile_height * self.state.level.level.height)
        self.assertLessEqual(
            self.state.scroll, level_height - state.sc.screen.get_height())
        self.assertIsInstance(self.state.scroll, (int, float))


if __name__ == '__main__':
    unittest.main()

