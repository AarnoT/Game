"""
Module for states.

classes:
State, MenuState, WorldState, BattleState, SelectTile, SelectAction
"""

import logging

import pygame as pg

from . import level
from . import screen as sc
from .button import Button, ButtonSet
from .sprite import Player, main_group


class State(object):
    """Base class for states."""

    @classmethod
    def change_state(cls, state, args=()):
        """Post event to change state."""
        event = pg.event.Event(pg.USEREVENT, {'state' : state, 'args' : args})
        pg.event.post(event)

    def exit(self):
        """Called when exiting a state. Can be overridden."""


class MenuState(State):
    """
    State for the menu.

    instance variables: button_set
    methods: __init__, scale, update, on_event, on_click, on_arrow_key,
    on_return
    class methods: create_main_menu, start_game, fullscreen, exit_game
    """

    def __init__(self, button_set):
        """Create menu."""
        logging.info('Menu is active')
        sc.draw_queue.append({'layer' : 1, 'func' : sc.background.fill,
                              'args' : ((255, 255, 255),)})
        self.button_set = button_set

    def scale(self, multiplier):
        """Resize the button set and clear the background."""
        self.button_set.scale(multiplier)
        sc.draw_queue.append({'layer' : 1, 'func' : sc.background.fill,
                              'args' : ((255, 255, 255),)})

    def update(self, time):
        """
        Call functions to draw the menu.
        Should be called every frame.
        """
        sc.draw_queue.append(
            {'layer' : 1, 'surf' : sc.background, 'pos' : (0, 0)})
        self.button_set.highlight()
        sc.draw_queue.append(
            {'layer' : 25, 'func' : self.button_set.draw, 'args' : (0,)})

    def on_event(self, event):
        """Call function depending on event."""
        if event.type == pg.MOUSEBUTTONDOWN:
            self.on_click()
        elif event.type == pg.KEYDOWN:
            if pg.key.name(event.key) in ('up', 'down', 'left', 'right'):
                self.on_arrow_key(pg.key.name(event.key))
            elif pg.key.name(event.key) == 'return':
                self.on_return()

    def on_click(self):
        """
        If mouse is above a button activate it.
        Should be called from the event loop.
        """
        self.button_set.press()

    def on_arrow_key(self, key_name):
        """Select a button depending on which key was pressed."""
        num = len(self.button_set.buttons)
        arrow_dict = {'up' : -1, 'down' : 1, 'left' : -num, 'right' : num}
        if self.button_set.highlighted_id is not None:
            self.button_set.highlighted_id = min(num - 1, max(
                0, self.button_set.highlighted_id + arrow_dict[key_name]))
        else:
            self.button_set.highlighted_id = 0

    def on_return(self):
        """Press the highlighted button."""
        self.button_set.highlighted_button.press()

    @classmethod
    def create_main_menu(cls):
        """
        Return instance of 'ButtonSet'.
        Scales based on screen size.
        """
        w, h = sc.screen.get_width() / 8, sc.screen.get_height() / 8
        x, y = sc.screen.get_width()/2 - w/2, sc.screen.get_height() / 5
        button_set = ButtonSet([
            Button(pg.Rect(x, y, w, h), 'START GAME', cls.start_game),
            Button(pg.Rect(x, y + h*1.5, w, h), 'FULLSCREEN', cls.fullscreen),
            Button(pg.Rect(x, y + h*3, w, h), 'EXIT GAME', cls.exit_game)])
        return button_set

    @classmethod
    def start_game(cls):
        """Post an event to change the state."""
        args = (WorldState.level, WorldState.player_anim,
                WorldState.pos_1, WorldState.player_image)
        event = pg.event.Event(
            pg.USEREVENT, {'state' : WorldState, 'args' : args})
        pg.event.post(event)

    @classmethod
    def fullscreen(cls):
        """Make the game fullscreen."""
        size = pg.display.list_modes()[0]
        pg.event.post(pg.event.Event(
            pg.VIDEORESIZE, {'size' : size, 'flags' : pg.FULLSCREEN}))

    @classmethod
    def exit_game(cls):
        """Post an event to quit the game."""
        pg.event.post(pg.event.Event(pg.QUIT, {}))


class WorldState(State):
    """
    The world state.

    instance variables: level, player
    methods: __init__, scale, update, on_event, on_click
    class variables: level, player_anim, pos_1, player_image
    """

    level = 'level_one.tmx'
    player_anim = ['dude1.png', 'dude2.png', 'dude3.png', 'dude2.png']
    pos_1 = (100, 100)
    player_image = ['guy.png']

    def __init__(self, level_name, anim, pos, image):
        """Set instance variables."""
        logging.info('World is active')
        self.level = level.Level(level_name)
        self.player = Player(pos, image, anim)
        sc.screen.blit(sc.background, (0, 0))

    def scale(self, multiplier): # Player pos inaccurate after scaling.
        """Scale things specific to the state."""
        prev_scroll = self.player.prev_scroll
        prev_y_pos = self.player.y_pos
        self.level.reload()
        self.player.prev_scroll *= multiplier
        for sprite in main_group:
            sprite.scale(multiplier)
        level_height = self.level.tile_width * self.level.level.height
        if self.player.y_pos + self.player.prev_scroll > (
                - sc.screen.get_height()/2):
            self.player.y_pos -= (
                self.player.scroll(level_height) + self.player.y_pos) - (
                    prev_scroll * multiplier + prev_y_pos * multiplier)
        blit_rect = pg.Rect(
            (0, self.player.scroll(level_height)), sc.screen.get_size())
        sc.draw_queue.append({'layer' : 25, 'func' : sc.screen.blit,
                              'args' : (sc.background, (0, 0), blit_rect)})

    def update(self, time):
        """Update the state. Should be called every loop."""
        self.update_level(time)
        self.update_sprites(time)

    def update_level(self, time):
        """Scroll and animate level."""
        prev_scroll = self.player.prev_scroll
        scroll = self.player.scroll(
            self.level.level.height * self.level.tile_width)
        if scroll != prev_scroll:
            blit_rect = pg.Rect((0, scroll), sc.screen.get_size())
            sc.draw_queue.append({'layer' : 1, 'func' : sc.screen.blit,
                                  'args' : (sc.background, (0, 0), blit_rect)})
            self.level.animate(time, scroll, draw=True)
        else:
            self.level.animate(time, scroll)

    def update_sprites(self, time):
        """Update and draw each sprite."""
        main_group.update(time)
        for sprite in main_group.sprites():
            pos = sprite.rect.topleft
            clear_rect = pg.Rect(
                (sprite.rect.x, sprite.rect.y + self.player.prev_scroll),
                sprite.rect.size)
            sc.screen.blit(sc.background, pos, clear_rect)
        sc.draw_queue.append({
            'layer' : 15, 'func' : main_group.draw, 'args' : (sc.screen,)})

    def on_event(self, event):
        """Call function depending on event."""
        if event.type == pg.MOUSEBUTTONDOWN:
            self.on_click(event.pos)

    def on_click(self, pos):
        """Move self.player to 'pos'."""
        self.player.move(pos)


class BattleState(State):
    pass


class SelectTile(BattleState):
    pass


class SelectAction(BattleState):
    pass

