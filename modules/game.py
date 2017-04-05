"""Module for the Game class."""

import logging
logging.basicConfig(
    format='%(levelname)s [%(asctime)s] %(message)s', level=logging.WARNING)

import pygame as pg

from . import screen as sc
from .state import MenuState, WorldState, BattleState


class Game(object):
    """Static class for running the game."""

    max_fps = 4000
    clock = pg.time.Clock()
    caption = 'The Game, FPS:{}'
    running = True
    state = MenuState(MenuState.create_main_menu())
    average_fps = []

    @classmethod
    def main_loop(cls):
        """Call game functions in a loop until user quits."""
        logging.info('Game starting.')
        while cls.running:
            cls.clock.tick(cls.max_fps)
            cls.event_loop()
            cls.state.update(cls.clock.get_time())
            rect_list = sc.draw_from_queue(sc.draw_queue)
            pg.display.update(rect_list)
            cls.update_fps()
        logging.info('Game quitting.')

    @classmethod
    def update_fps(cls):
        """Update the average fps and the window caption."""
        cls.average_fps.append(min(cls.clock.get_fps(), 10000))
        if len(cls.average_fps) >= 240:
            current_fps = int(sum(cls.average_fps) / len(cls.average_fps))
            pg.display.set_caption(cls.caption.format(current_fps))
            cls.average_fps = list()

    @classmethod
    def event_loop(cls):
        """
        Loop through all the events.
        Should be called every frame.
        """
        for event in pg.event.get():
            if event.type == pg.QUIT:
                cls.running = False
            elif event.type == pg.KEYDOWN and (
                    pg.key.name(event.key) == 'escape'):
                cls.running = False
            elif event.type == pg.VIDEORESIZE:
                if hasattr(event, 'flags'):
                    cls.resize(event.size, event.flags)
                else:
                    cls.resize(event.size)
            elif event.type == pg.USEREVENT:
                if hasattr(event, 'state'):
                    cls.state.exit()
                    cls.state = event.state(*event.args)
            else:
                cls.state.on_event(event)

    @classmethod
    def resize(cls, res=sc.DEFAULT_RES, flags=pg.RESIZABLE):
        """Scale the game objects to 'res'."""
        multiplier = float(res[0]) / sc.res[0]
        logging.info('Scaling game to %f scale.', multiplier)
        sc.res, sc.screen = sc.set_display(res, flags)
        cls.state.scale(multiplier)


