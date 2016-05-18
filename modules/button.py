"""Module for the button class."""

import logging
import pygame
pygame.init()

import screen

class Button(object):
    """
    Button class.

    Methods: __init__, draw, check, clear, action
    Instance variables: rect, real_y, text, font, surf
    """

    def __init__(self, rect, text, font, action):
        """
        Create a button.

        rect should be a pygame.Rect.
        action should be a function.
        """
        self.rect = rect
        self.real_y = self.rect.y
        self.text = text
        self.font = font
        self.action = action
        self.surf = None

    def draw(self, pos, scroll):
        """Render text and blit it onto the foreground."""
        if self.rect.contains(pygame.Rect(pos, self.font.size(self.text))):
            self.surf = self.font.render(
                self.text, 0, (0, 0, 255), (255, 255, 255)).convert()
            self.surf.set_colorkey((255, 255, 255))
            x, y = pos
            screen.var.foreground.blit(self.surf, (x, y + scroll))
        else:
            logging.warning('Button text is too large.')

    def check(self, pos):
        """If position collides with button call button action."""
        if self.rect.collidepoint(pos):
            self.action()

    def clear(self, scroll):
        """
        Draw a white rectangle on the button.

        White should be the colorkey of foreground.
        """
        self.rect.y = self.real_y + scroll
        pygame.draw.rect(screen.var.foreground, (0, 0, 0), self.rect)
        self.rect.y = self.real_y

