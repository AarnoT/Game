"""
Module for sprites.

classes: Group, Sprite, Player
objects: main_group
"""

import logging
from os.path import join
from math import hypot
from itertools import cycle

import pygame as pg

from .path import IMAGE_PATH

class Group(pg.sprite.Group):
    """Class to extend the pygame group class."""

    def draw_health(self):
        """
        Draw each sprites health above it.
        Unimplemented for now.
        """
        for sprite in self.sprites():
            pass


main_group = Group()


class Sprite(pg.sprite.Sprite):
    """
    Class to extend the pygame sprite class.

    instance variables:
    x_pos, y_pos, steps, prev_scroll, image, rect, size, state
    methods: __init__, load_frames, scale, move, animate, update
    """

    def __init__(self, pos, still, moving):
        """Set instance variables and load sprite frames."""
        self.groups = [main_group]
        pg.sprite.Sprite.__init__(self, self.groups)
        self.x_pos, self.y_pos = pos
        self.x_vel, self.y_vel = 0.0, 0.0
        self.steps = 0.0
        self.max_speed = pg.display.get_surface().get_height() / 240.0

        still = self.load_frames(still)
        moving = self.load_frames(moving)
        flipped = (pg.transform.flip(frame, True, False) for frame in moving)
        self.frames = {'still' : cycle(still),
                       'moving_right' : cycle(moving),
                       'moving_left' : cycle(flipped),
                       'time' : 0}
        self.image = next(self.frames['still'])
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.size = self.rect.size
        self.state = 'still'

    def load_frames(self, frames):
        """Load frames from an iterable of strings."""
        return [pg.image.load(join(IMAGE_PATH, frame)) for frame in frames]

    def scale(self, multiplier):
        """Scale sprite by 'multiplier'."""
        self.x_pos *= multiplier
        self.y_pos *= multiplier
        self.max_speed *= multiplier
        self.size = [int(num * multiplier) for num in self.size]

    def move(self, pos):
        """Move sprite towards 'pos'."""
        distance = hypot(self.x_pos - pos[0], self.y_pos - pos[1])
        self.steps = distance / self.max_speed
        self.x_vel = (pos[0] - self.x_pos) / self.steps
        self.y_vel = (pos[1] - self.y_pos) / self.steps
        if self.x_vel < 0:
            self.state = 'moving_left'
        else:
            self.state = 'moving_right'

    def animate(self, elapsed_time):
        """
        Update sprite frame if enough time has passed.
        Should be called every frame.
        """
        self.frames['time'] += elapsed_time
        frame_duration = 100
        if self.frames['time'] >= frame_duration:
            self.frames['time'] -= frame_duration
            self.image = next(self.frames[self.state])
        if self.image.get_size() != self.size:
            self.image = pg.transform.scale(self.image, self.size)

    def update(self, elapsed_time):
        """Update sprite position. Should be called every frame."""
        self.animate(elapsed_time)
        self.x_pos += self.x_vel * (elapsed_time / 16.0)
        self.y_pos += self.y_vel * (elapsed_time / 16.0)
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.steps -= elapsed_time / 16.0
        if self.steps <= 0:
            self.x_vel, self.y_vel = 0.0, 0.0
            self.state = 'still'


class Player(Sprite):
    """
    Player class to extend the sprite class.

    methods: scroll
    instance variables: prev_scroll
    """
    def __init__(self, pos, still, moving):
        super(Player, self).__init__(pos, still, moving)
        self.prev_scroll = 0

    def scroll(self, level_height):
        """Return amount level should be scrolled."""
        height = pg.display.get_surface().get_height()
        if self.y_pos + self.prev_scroll < height / 2:
            scroll = 0
        elif height > level_height:
            scroll = 0
        elif self.y_pos + self.prev_scroll > (level_height - height / 2):
            scroll = level_height - height
        else:
            # All sprites have to be moved
            # the same amount the scroll is adjusted.

            y_change = self.y_pos - height / 2
            for sprite in main_group:
                sprite.y_pos -= y_change
            scroll = self.prev_scroll + y_change
        self.prev_scroll = scroll
        return scroll

