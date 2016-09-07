"""Module for the level class."""

import logging
from collections import namedtuple
from os.path import join

import pygame as pg
from pytmx.util_pygame import load_pygame

from . import screen as sc
from .path import LEVEL_PATH

class Level(object):
    """
    Class for levels.

    instance variables: level, prev_scroll, tile_obj, tile_width,
                        tile_height, tile_size, scroll, tiles
    methods: __init__, reload, load_tiles, draw, animate
    """

    def __init__(self, tmx_file):
        """Set instance variables."""
        self.level = load_pygame(join(LEVEL_PATH, tmx_file))
        self.tile_obj = namedtuple('tile_obj', ['x', 'y', 'layer'])
        self.reload()

    @property
    def tile_width(self):
        """Return tile width based on screen size."""
        return int(pg.display.get_surface().get_width() / self.level.width)

    @property
    def tile_height(self):
        """
        Return tile size based on screen size.
        Currently the same as tile_width.
        """
        return self.tile_width

    @property
    def tile_size(self):
        """Return tile size based on screen size."""
        return self.tile_width, self.tile_height

    def reload(self):
        """Reload level in the right scale."""
        sc.background = pg.Surface((self.tile_width * self.level.width,
                                    self.tile_height * self.level.height))
        self.tiles = {}
        for num, layer in enumerate(self.level.visible_layers):
            self.load_tiles(num, layer)
        # self.tiles is a dict while self.animated_tiles is a list
        self.animated_tiles = list(
            tile for tile in self.tiles.values() if tile.get('frames'))
        self.draw()
        sc.background.convert()

    def load_tiles(self, layer_num, layer):
        """Load tiles each tile in the layer."""
        for tile in layer.tiles():
            tile_dict = {
                'pos' : self.tile_obj(tile[0], tile[1], layer_num),
                'images' : [pg.transform.scale(tile[2], self.tile_size)]}
            properties = self.level.get_tile_properties(
                tile[0], tile[1], layer_num)
            if properties and properties.get('frames'):
                tile_dict.update({'images' : [],
                                  'index' : 0,
                                  'timer' : -100,
                                  'frames' : properties['frames']})
                for frame in tile_dict['frames']:
                    image = self.level.get_tile_image_by_gid(frame.gid)
                    image = pg.transform.scale(image, self.tile_size)
                    image.set_colorkey((0, 0, 0))
                    tile_dict['images'].append(image)
            self.tiles[(tile[0], tile[1], layer_num)] = tile_dict

    def draw(self):
        """Draw tiles in each layer to the background."""
        for tile in sorted(self.tiles.values(), key=lambda v: v['pos'][2]):
            pos = (tile['pos'].x * self.tile_width,
                   tile['pos'].y * self.tile_height)
            sc.background.blit(tile['images'][0], pos)

    def animate(self, elapsed_time, scroll, draw=False):
        """
        Draw next animation frame if enough time has passed.
        Should be called every frame.
        """
        for tile in self.animated_tiles:
            tile['timer'] += elapsed_time
            if tile['timer'] >= tile['frames'][tile['index']].duration:
                # 'tile_2' is the tile above or below 'tile'.
                tile_2 = self.tiles.get((tile['pos'].x, tile['pos'].y,
                                         [1, 0][tile['pos'].layer]))
                if draw:
                    self.animate_to_background(tile, tile_2)
                else:
                    pos = (tile['pos'].x * self.tile_width,
                           tile['pos'].y * self.tile_height - scroll)
                    if tile_2:
                        sc.draw_queue.append(
                            {'layer' : [2, 6][tile_2['pos'].layer],
                             'surf' : tile_2['images'][0], 'pos' : pos})
                    sc.draw_queue.append(
                        {'layer' : [2, 6][tile['pos'].layer],
                         'surf' : tile['images'][tile['index']], 'pos' : pos})
                tile['timer'] -= tile['frames'][tile['index']].duration
                tile['index'] = (tile['index'] + 1) % len(tile['frames'])

    def animate_to_background(self, tile, tile_2):
        """Draw animated tiles onto the background."""
        pos = (tile['pos'].x * self.tile_width,
               tile['pos'].y * self.tile_height)
        if tile_2 and tile_2['pos'].layer == 0:
            sc.background.blit(tile_2['images'][0], pos)
            sc.background.blit(tile['images'][tile['index']], pos)
        if tile_2 and tile_2['pos'].layer == 1:
            sc.background.blit(tile['images'][tile['index']], pos)
            sc.background.blit(tile_2['images'][0], pos)
        else:
            sc.background.blit(tile['images'][tile['index']], pos)

