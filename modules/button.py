"""
Module for the button class and the button set.

classes: ButtonSet, Button
"""

import logging

import pygame as pg

from . import screen as sc


class ButtonSet(object):
    """
    Class to interact with a set of buttons at the same time.

    instance variables: buttons, highlighted_id,
    highlighted_button, active
    methods: __init__, toggle, scale, draw, press, highlight, check,
             clear, __iter__
    """

    def __init__(self, buttons):
        """Set instance variables."""
        self.buttons = buttons
        self.highlighted_id = None
        self.active = True
        self.next_id = 0
        for button in self.buttons:
            button.id = self.next_id
            self.next_id += 1

    def __iter__(self):
        """Yield each button."""
        for button in self.buttons:
            yield button

    @property
    def highlighted_button(self):
        """Return  highlighted button."""
        if self.highlighted_id is not None:
            return self.buttons[self.highlighted_id]
        else:
            return self

    def toggle(self):
        """Toggle button states."""
        self.active = not self.active
        for button in self.buttons:
            button.active = self.active

    def scale(self, multiplier):
        """Scale all buttons in the set."""
        for button in self.buttons:
            button.scale(multiplier)

    def draw(self, scroll):
        """Draw active buttons."""
        for button in [b for b in self.buttons if b.active]:
            if button is self.highlighted_button:
                button.draw(scroll, highlighted=True)
            else:
                button.draw(scroll)

    def press(self):
        """Press button that check returns or reset highlighted id."""
        button = self.check()
        if button is not None:
            self.buttons[button].press()
        else:
            self.highlighted_id = None

    def highlight(self):
        """Highlight the button under the cursor."""
        button = self.check()
        if button is not None:
            self.highlighted_id = button

    def check(self):
        """Return button that collides with mouse position."""
        for button in [b for b in self.buttons if b.active]:
            if button.check(pg.mouse.get_pos()):
                return button.id

    def clear(self):
        """Clear buttons from the screen."""
        for button in self.buttons:
            button.clear()


class Button(object):
    """
    Class for buttons.

    instance variables: rect, pos, id, text, font, surf, active
    methods: __init__, render, press, scale, draw, clear, check
    """

    def __init__(self, rect, text, strategy):
        """Set instance variables."""
        self.text_color = (1, 1, 1)
        self.bg_color = (255, 255, 255)
        self.highlight_color = (0, 0, 255)
        self.rect = rect
        self.text = text
        self.press = strategy
        # Pos is set in the draw function.
        self.pos = (-1000, -1000)
        self.id = 0
        self.active = True
        self.font = None
        self.surf = None
        self.render()

    def render(self):
        """Set font and render button."""
        font_size = int(max(self.rect.width / 6, self.rect.height / 3))
        self.font = pg.font.Font(None, font_size)
        text_surf = self.font.render(
            self.text, 0, self.text_color, self.bg_color)
        text_pos = (self.rect.width/2 - text_surf.get_width()/2,
                    self.rect.height/2 - text_surf.get_height()/2)
        self.surf = pg.Surface(self.rect.size)
        self.surf.fill(self.bg_color)
        #self.surf.set_colorkey(self.bg_color)
        self.surf.blit(text_surf, text_pos)
        pg.draw.rect(self.surf, self.highlight_color,
                     pg.Rect((0, 0), self.rect.size), 1)

    def scale(self, multiplier):
        """Scale button using the 'multiplier' value."""
        self.rect.x *= multiplier
        self.rect.y *= multiplier
        self.rect.width *= multiplier
        self.rect.height *= multiplier
        self.render()

    def draw(self, scroll, highlighted=False):
        """
        Draw 'self.surf' to 'self.dest'.
        If 'highlighted' is true a blue border is drawn.
        """
        self.pos = (self.rect.x, self.rect.y + scroll)
        blit_rect = pg.Rect(self.pos, self.surf.get_size())
        sc.draw_queue.append(dict(layer=10, surf=self.surf, pos=self.pos))
        if highlighted:
            sc.draw_queue.append(dict(
                layer=11, func=pg.draw.rect,
                args=(sc.screen, self.highlight_color, self.rect, 2)))

    def clear(self):
        """Clear the area of 'self.rect' from 'self.dest'."""
        clear_rect = pg.Rect(
            self.pos, (self.rect.width + 2, self.rect.height + 2))
        sc.draw_queue.append(dict(
            layer=2, func=pg.draw.rect,
            args=(sc.screen, self.bg_color, clear_rect)))

    def check(self, pos):
        """Check if pos overlaps 'self.rect'. Return bool."""
        return self.rect.collidepoint(pos)

