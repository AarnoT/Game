"""
Module for game text.

Contains TextCreate and its object var.
"""

import json
import logging
import pygame

class TextCreate(object):
    """
    Class to create and store text.

    methods: __init__, make_lines, draw_text, more_text, new_text
    instance variables: font, text, text_index, text_position, rect,
    surfaces, vertical_offset
    """

    def __init__(self, screen_size):
        """Load text and create variables."""
        if 'palatinolinotype' in pygame.font.get_fonts():
            self.font = pygame.font.SysFont('palatinolinotype', 20)
        else:
            self.font = pygame.font.Font(None, 20)
        # Load text from a json file to a dictionary.
        with open('text/text.json') as text_file:
            self.text = json.load(text_file)
        self.text_index = 0
        self.text_position = (screen_size[0] / 2 - 350, screen_size[1] - 125)
        self.rect = pygame.Rect(self.text_position, (700, 100))
        self.surfaces = []
        self.vertical_offset = 35

    def make_lines(self, text):
        """Loop through words and create lines."""
        lines = []
        line = ''
        for word in text.split():
            if self.font.size(line + word + ' ')[0] <= 600:
                line = line + word + ' '
            else:
                lines.append(line)
                line = word + ' '
        lines.append(line)
        return lines

    def draw_text(self, lines, color):
        """Render text and blit it onto a surface."""
        text_box = pygame.image.load('images/textbox.png')
        num = 0
        for num, line in enumerate(lines):
            line = self.font.render(line, 0, color, (255, 255, 255))
            line.set_colorkey((255, 255, 255))
            line.convert()
            text_box.blit(line, (50, num % 3 * self.vertical_offset + 5))
            if (num + 1) % 3 == 0:
                self.surfaces.append(text_box.convert_alpha())
                text_box = pygame.image.load('images/textbox.png')
        if (num + 1) % 3 != 0:
            self.surfaces.append(text_box.convert_alpha())

    def more_text(self):
        """Increment text_index or reset text if done."""
        if self.text_index + 1 < len(self.surfaces):
            self.text_index += 1
        else:
            self.text_index = 0
            self.surfaces = []

    def new_text(self, text, color=(1, 1, 1)):
        """Create new text surfaces."""
        self.text_index = 0
        self.surfaces = []
        lines = self.make_lines(text)
        self.draw_text(lines, color)

var = TextCreate(pygame.display.get_surface().get_size())

