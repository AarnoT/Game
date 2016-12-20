"""Module for text."""

import logging
from json import load
from math import hypot
from os.path import join

import pygame as pg
pg.init()

from .path import IMAGE_PATH, TEXT_PATH
from .screen import draw_queue
from .button import ButtonSet

text_box = pg.image.load(join(IMAGE_PATH, 'textbox.png'))


class Text(object):
    """
    Class for a text pop-up.

    methods: __init__, scale, next, draw
    instance variables: rect, text, surface, num, buttons, lines, font,
                        active, surf_size, pos
    """

    @classmethod
    def from_json(cls):
        """Return a list of text objects based on a json file."""
        with open(join(TEXT_PATH, 'text.json')) as text:
            text_dict = load(text)
        return {
            k : Text(v) for k, v in zip(text_dict.keys(), text_dict.values())}

    def __init__(self, text, buttons=ButtonSet([])):
        """Initialize instance variables."""
        self.buttons = buttons
        screen_width, screen_height = pg.display.get_surface().get_size()
        self.surf_size = (int(screen_width * 0.6), int(screen_height * 0.15))
        self.pos = (int((screen_width - self.surf_size[0]) / 2),
                    int(screen_height * 0.8))
        self.scale(1)
        self.text = text
        self.active = False
        self.split_lines()

    def scale(self, multiplier):
        """Scale buttons, font, rect and surface to the correct size."""
        screen_width, screen_height = pg.display.get_surface().get_size()
        self.surf_size = (int(self.surf_size[0] * multiplier),
                          int(self.surf_size[1] * multiplier))
        self.pos = (int(self.pos[0] * multiplier),
                    int(screen_height * 0.8))
        self.surface = pg.transform.scale(text_box, self.surf_size)
        self.rect = pg.Rect(
            self.pos, (self.surf_size[0], self.surf_size[1] + 1))
        font_size = int(max(self.rect.width / 20, self.rect.height / 5))
        self.font = pg.font.Font(None, font_size)
        self.buttons.scale(multiplier)

    def next(self):
        """Update text surface with new text if any is available."""
        if self.lines and not self.active:
            self.active = True
        if not self.lines:
            self.active = False
        else:
            # Reset surface.
            self.scale(1)
            line_num = int(
                self.surface.get_height()*0.9 / self.font.size('')[1])
            for n in range(min(line_num, len(self.lines))):
                line = self.font.render(self.lines.pop(0), True, (0, 0, 0))
                offset = n * self.surface.get_height() * 0.25
                self.surface.blit(
                    line, (self.surface.get_width()*0.1,
                           self.surface.get_height()*0.1 + offset))
            self.surface.convert()

    def split_lines(self):
        """Split lines so that they fit inside the text box."""
        self.lines = []
        line = ''
        for word in self.text.split():
            if (self.font.size(line + word + ' ')[0]
                <= self.surface.get_width() * 0.9):
                    line = line + word + ' '
            else:
                self.lines.append(line)
                line = word + ' '
        self.lines.append(line)

    def draw(self):
        """Add surface to the draw queue."""
        draw_queue.append(
            dict(layer=5, surf=self.surface, pos=self.rect.topleft))

