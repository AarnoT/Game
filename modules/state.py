"""Module for states."""

import logging

import pygame as pg

from . import level
from . import screen as sc
from .button import Button, ButtonSet
from .sprite import Sprite, main_group
from . import text


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
    """State for the menu."""

    def __init__(self, button_set):
        """Create menu."""
        logging.info('Menu is active')
        sc.draw_queue.append(dict(layer=1, func=sc.screen.fill,
                                  args=((255, 255, 255),)))
        self.button_set = button_set

    def scale(self, multiplier):
        """Resize the button set and clear the background."""
        self.button_set.scale(multiplier)
        sc.draw_queue.append(dict(layer=1, func=sc.screen.fill,
                                  args=((255, 255, 255),)))

    def update(self, time):
        """
        Call functions to draw the menu.
        Should be called every frame.
        """
        self.button_set.clear()
        self.button_set.highlight()
        sc.draw_queue.append(
            dict(layer=25, func=self.button_set.draw, args=(0,)))

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
    """The world state."""

    level = 'level_one.tmx'
    player_anim = ['dude1.png', 'dude2.png', 'dude3.png', 'dude2.png']
    pos_1 = (100, 100)
    player_image = ['guy.png']

    def __init__(self, level_name, anim, pos, image):
        """Set instance variables."""
        logging.info('World is active')
        self.level = level.Level(level_name)
        self.player = Sprite(pos, image, anim)
        self.level.draw(self.scroll)
        self.nodes = level.NodeGroup.from_level(self.level.level,
                                                text.Text.from_json())
        self.nodes.draw(self.scroll)
        self.prev_scroll = self.scroll
        self.real_scroll = 0
        self.actual_scroll = 0
        main_group.draw(self.level.tile_height * self.level.level.height)
        self.redraw = False


    def scale(self, multiplier):
        """Scale things specific to the state."""
        self.level.reload()
        for sprite in main_group:
            sprite.scale(multiplier)
        self.nodes.scale(multiplier)
        self.redraw = 3

    @property
    def scroll(self):
        """Return how much the screen should be scrolled."""
        level_height = self.level.tile_height * self.level.level.height
        screen_height = sc.screen.get_height()
        return max(0, min(
            self.player.rect.top - screen_height/2,
            level_height - screen_height))

    def zoom(self):
        """Zoom level and scale things."""
        old_width = self.level.tile_width
        self.level.zoomed = pg.key.get_pressed()[pg.K_z]
        self.level.reload()
        new_width = self.level.tile_width
        sc.draw_queue.append(dict(layer=1, func=sc.screen.fill,
                                  args=((0, 0, 0),)))
        self.scale(new_width / old_width)
        level_width = self.level.tile_width * self.level.level.width
        if self.level.zoomed:
            y_pos = int(sc.screen.get_height() * 0.8)
            for node in [node for node in self.nodes if node.text]:
                node.text.pos = (level_width/2 - (
                    node.text.surface.get_width()/2), y_pos)

    def update(self, time):
        """Update the state. Should be called every loop."""
        if self.redraw:
            self.level.draw(self.scroll)
            self.redraw -= 1
        if pg.key.get_pressed()[pg.K_z] != self.level.zoomed:
            self.zoom()
        self.update_sprites(time)
        self.update_level(time)
        self.prev_scroll = self.scroll

    def scroll_level(self):
        """Scroll the level and update the screen."""
        scroll_change = self.scroll - self.prev_scroll
        self.real_scroll += scroll_change
        self.actual_scroll += int(scroll_change)
        scroll_diff = self.real_scroll - self.actual_scroll
        self.actual_scroll += int(scroll_diff)
        total_scroll = int(scroll_change) + int(scroll_diff)
        if total_scroll != 0:
            # Surface.scroll has better performance than blit.
            sc.draw_queue.append(dict(
                layer=1, func=sc.screen.scroll, args=(0, -total_scroll),
                rect=pg.Rect((0, 0), sc.screen.get_size())))
            if total_scroll > 0:
                scroll_rect = pg.Rect(
                    0, self.scroll + sc.screen.get_height() - total_scroll,
                    sc.screen.get_width(), total_scroll)
            elif total_scroll < 0:
                scroll_rect = pg.Rect(
                    0, self.scroll, sc.screen.get_width(), -total_scroll)
            self.level.draw_area(scroll_rect, self.scroll)

    def update_level(self, time):
        """Scroll, animate level and draw nodes and text."""
        if self.player.y_vel != 0:
            self.scroll_level()
            self.nodes.draw(self.scroll)

        # Animate level.
        if not any(node.text.active for node in self.nodes if node.text):
            if any(
                    tile['timer'] + time
                    >= tile['frames'][tile['index']].duration
                    for tile in self.level.animated_tiles):
                main_group.draw(
                    self.level.tile_height * self.level.level.height)
            self.level.animate(time, self.scroll)

    def update_sprites(self, time):
        """Update and draw each sprite."""
        if self.player.x_vel != 0 or self.player.y_vel != 0:
            self.nodes.check(self.player)
            old_rect = self.player.rect
            main_group.update(time)
            clear_rect = old_rect.union(self.player.rect)
            self.level.draw_area(clear_rect, self.scroll)
            for node in [n for n in self.nodes
                         if n.active == '1' or n.active is True]:
                if self.player.rect.colliderect(
                        (node.x_pos - node.radius, node.y_pos - node.radius,
                         node.radius*2, node.radius*2)):
                    node.draw(self.scroll)
            main_group.draw(self.level.tile_height * self.level.level.height)
        else:
            main_group.update(time)

    def on_event(self, event):
        """Call function depending on event."""
        if event.type == pg.MOUSEBUTTONDOWN:
            self.on_click(event.pos)

    def on_click(self, pos):
        """Move self.player to 'pos' or update text."""
        active_texts = [node for node in self.nodes
                        if node.text and node.text.active]
        if active_texts:
            for node in active_texts:
                node.update_text()
                if not node.text.active:
                    text_rect = node.text.rect.copy()
                    text_rect.y += self.scroll
                    sc.draw_queue.append(dict(
                        layer=1, pos=(text_rect.x, text_rect.y),
                        func=pg.draw.rect,
                        args=(sc.screen, (0, 0, 0), text_rect)))
                    self.level.draw_area(text_rect, self.scroll)
                    self.level.draw_area(pg.Rect(
                        node.x_pos - node.radius, node.y_pos - node.radius,
                        node.radius*2, node.radius*2), self.scroll)
                    node.active = False
                    [n for n in self.nodes
                        if str(n.id) == node.next_node][0].active = '1'
                    main_group.draw(
                        self.level.tile_height * self.level.level.height)
        else:
            self.player.move(
                pos, self.level.tile_height * self.level.level.height)


class BattleState(WorldState):
    """"""

    def __init__(self, level_name, anim, pos, image):
        """"""
        super(BattleState, self).__init__(level_name, anim, pos, image)
        text_box = pg.image.load('')

