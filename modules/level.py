"""Module for the Level class and its object level."""

from math import hypot
from collections import namedtuple
from pytmx.util_pygame import load_pygame
import logging
import pygame

import screen
import text

class Level(object):
    """
    Class for levels in the game.

    methods: __init__, load_images, set_scaling, scale_objects,
    scroll_level, draw,  activate_nect, check_objects, draw_objects
    instance variables: level, tile_w, tile_h, scroll, tiles, objs
    """

    def __init__(self, level_name):
        """Load the level and scale it."""
        res = pygame.display.get_surface().get_size()
        self.level = load_pygame('levels/' + level_name)
        self.tile_w, self.tile_h = self.level.tilewidth, self.level.tileheight
        self.scroll = 0
        self.set_scaling(res)
        self.scale_objects()
        self.tiles = []
        self.Tile = namedtuple('Tile', ['x', 'y', 'layer', 'image'])
        layer_num = sum(1 for layer in self.level.visible_layers)
        for layer in range(layer_num):
            self.load_images(layer)
        self.objs = [obj for obj in self.level.objects]
        if all(hasattr(obj, 'active') for obj in self.objs):
            self.draw_objects()

    def load_images(self, layer):
        """Load the level tiles."""
        for x in range(self.level.width):
            for y in range(self.level.height):
                image = self.level.get_tile_image(x, y, layer)
                if image is not None:
                    image = pygame.transform.scale(
                        image, (self.tile_w, self.tile_h))
                    self.tiles.append(self.Tile(
                        x * self.tile_w, y * self.tile_h, layer, image))

    def set_scaling(self, res):
        """Calculate new tile sizes."""
        if self.level.width * self.tile_w != res[0]:
            self.tile_w = res[0] / (self.level.width)
            self.tile_h = res[0] / (self.level.width)

    def scale_objects(self):
        """Scale objects based on new tile size."""
        for obj in self.level.objects:
            obj.x *= float(self.tile_w) / float(self.level.tilewidth)
            obj.y *= float(self.tile_h) / float(self.level.tileheight)
            obj.width *= float(self.tile_w) / float(self.level.tilewidth)
            obj.height *= float(self.tile_h) / float(self.level.tileheight)

    def scroll_level(self, screen_height, player, enemy_group):
        """Determine the amount the screen needs to be scrolled down."""
        if player.y_pos + self.scroll < screen_height / 2:
            self.scroll = 0
        elif screen_height > self.tile_h * self.level.height:
            self.scroll = 0
        elif player.y_pos + self.scroll > (
            self.tile_h * self.level.height - screen_height / 2):
            self.scroll = self.tile_h * self.level.height - screen_height
        else:
            self.scroll += player.y_pos - screen_height / 2
            for enemy in enemy_group:
                enemy.y_pos -= player.y_pos - screen_height / 2
            player.y_pos -= player.y_pos - screen_height / 2

    def draw(self):
        """Draw the level tiles based on layer."""
        size = (
            self.level.width * self.tile_w, self.level.height * self.tile_h)
        background = pygame.Surface(size)
        midground = pygame.Surface(size)
        for tile in self.tiles:
            if tile.layer == 0:
                background.blit(tile.image, (tile.x, tile.y))
            elif tile.layer == 1:
                midground.blit(tile.image, (tile.x, tile.y))
        background.convert()
        midground.convert()
        return background, midground

    def activate_next(self, obj, obj_list):
        """Activate next nodes in the obj_list."""
        obj.active = '0'
        for objs in obj_list:
            if objs.id == int(obj.next_node):
                objs.active = '1'
        rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
        pygame.draw.rect(screen.var.foreground, (0, 0, 0), rect)
        return obj_list

    def check_objects(self, location):
        """Check if location collides with an active object."""
        for obj in filter(lambda obj: obj.active == '1', self.objs):
            rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            x, y = location
            if hypot(x - obj.x - obj.width / 2, y - obj.y - obj.width / 2
                ) < obj.width / 2:
                if len(text.var.surfaces) == 0:
                    self.objs = self.activate_next(obj, self.objs)
                    self.draw_objects()
                return obj

    def draw_objects(self):
        """Draw active objects onto the screen as circles."""
        for obj in filter(lambda obj: obj.active == '1', self.objs):
            pygame.draw.circle(
                screen.var.foreground, ((0, 0, 255)),
                (int(obj.x + obj.width / 2),
                int(obj.y + obj.height / 2)), int(obj.width) / 2)

level = Level('menu.tmx')

