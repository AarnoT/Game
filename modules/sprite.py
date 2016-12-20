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

from . import screen as sc
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

    def draw(self, level_height):
        """
        Draw each sprite to the surf at the correct position.
        """
        screen_height = sc.screen.get_height()
        for sprite in self.sprites():
            if level_height - sprite.rect.y < screen_height/2:
                real_y = screen_height - (level_height - sprite.rect.y)
            else:
                real_y = min(screen_height/2, sprite.rect.y)
            sc.draw_queue.append(dict(layer=20, surf=sprite.image,
                                      pos=(sprite.rect.x, real_y)))


main_group = Group()


class Sprite(pg.sprite.Sprite):
    """
    Class to extend the pygame sprite class.

    instance variables: x_pos, y_pos, steps, image,
    rect, size, state
    methods: __init__, load_frames, scale, move, animate, update, stop
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
        width = sc.screen.get_width() * 0.04
        height = width * (self.image.get_height() / self.image.get_width())
        self.size = [int(width), int(height)]
        self.image = pg.transform.scale(self.image, self.size)
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
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

    def stop(self):
        """Stop and update sprite."""
        self.steps = 0
        self.x_vel, self.y_vel = 0.0, 0.0
        self.state = 'still'
        self.frames['time'] = 100

    def move(self, pos, level_height):
        """Move sprite towards 'pos'."""
        screen_height = pg.display.get_surface().get_height()
        if level_height - self.y_pos < screen_height/2:
            real_y = screen_height - (level_height - self.y_pos)
        else:
            real_y = min(screen_height/2, self.y_pos)
        distance = hypot(self.x_pos - pos[0], real_y - pos[1])
        self.steps = max(1, distance / self.max_speed)
        self.x_vel = (pos[0] - self.x_pos) / self.steps
        self.y_vel = (pos[1] - real_y) / self.steps
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
        self.x_pos += self.x_vel * min(self.steps, (elapsed_time / 16.0))
        self.y_pos += self.y_vel * min(self.steps, (elapsed_time / 16.0))
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.steps -= elapsed_time / 16.0
        if self.state != 'still' and self.steps <= 0:
            self.stop()
        self.animate(elapsed_time)

