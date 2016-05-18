"""Module that contains the Screen class and its object var."""

import os
import logging
import pygame

class Screen(object):
    """
    Stores the screen and the game surfaces for easy access.

    methods: __init__
    instance variables: screen, background, midground, foreground
    """

    def __init__(
        self, res=pygame.display.list_modes()[0], flags=pygame.RESIZABLE):
        """Create instance variables."""
        os.environ['SDL_VIDEO_CENTERED'] = "True"
        self.screen = pygame.display.set_mode(res, flags)
        logging.info('Screen now running at %s resolution.', str(res))
        self.background = pygame.Surface((2000, 2000))
        self.midground = pygame.Surface((2000, 2000))
        self.foreground = pygame.Surface((2000, 2000))
        self.midground.set_colorkey((0, 0, 0))
        self.foreground.set_colorkey((0, 0, 0))

var = Screen()

