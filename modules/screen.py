"""
Module for things related to the screen.

variables: info, DEFAULT_RES, screen, background, draw_queue
functions: draw_from_queue, set_display
"""

import os
import logging

import pygame as pg

info = pg.display.Info()
DEFAULT_RES = info.current_w, info.current_h
os.environ['SDL_VIDEO_CENTERED'] = 'True'
background = pg.Surface(DEFAULT_RES)

def set_display(size=DEFAULT_RES, flags=pg.RESIZABLE):
    """
    Return 'size' and a new display surface of 'size' with 'flags'.
    """
    display = pg.display.set_mode(size, flags)
    logging.info('Screen is now at %s resolution.', size)
    return size, display

res, screen = set_display()
draw_queue = []

def draw_from_queue(queue):
    """
    Draw each item in queue to the screen.
    Dicts should have the keys 'layer' and either 'surf and 'pos'
    or 'func' and 'args'.
    If the queue isn't cleared things might lag.
    """
    queue.sort(key=lambda i: i['layer'])
    while queue:
        item = queue.pop(0)
        if 'func' in item:
            item['func'](*item['args'])
        elif 'surf' in item:
            screen.blit(item['surf'], item['pos'])

