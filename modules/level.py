"""Module for the level, node and node group classes."""

import logging
from collections import namedtuple
from os.path import join
from math import hypot, ceil

import pygame as pg
from pytmx.util_pygame import load_pygame

from . import screen as sc
from .path import LEVEL_PATH

class Level(object):
    """
    Class for levels.

    instance variables: level, tile_obj, tile_width, tile_height,
                        tile_size, scroll, tiles, bg, zoomed
    methods: __init__, reload, load_tiles, draw_area, draw, animate,
             draw_tile
    """

    def __init__(self, tmx_file):
        """Set instance variables."""
        self.level = load_pygame(join(LEVEL_PATH, tmx_file))
        self.tile_obj = namedtuple('tile_obj', ['x', 'y', 'layer'])
        self.zoomed = False
        self.reload()

    @property
    def tile_width(self):
        """Return tile width based on screen size."""
        if self.zoomed:
            return int(
                pg.display.get_surface().get_height() / self.level.height)
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
        self.tiles = {}
        self.bg = pg.Surface((self.level.width * self.tile_width,
                              self.level.height * self.tile_height))
        self.bg.convert()
        for num, layer in enumerate(self.level.visible_layers):
            self.load_tiles(num, layer)
        # self.tiles is a dict while self.animated_tiles is a list
        self.animated_tiles = list(
            tile for tile in self.tiles.values() if tile.get('frames'))

    def load_tiles(self, layer_num, layer):
        """Load tiles each tile in the layer."""
        for tile in layer.tiles():
            tile_dict = {
                'pos' : self.tile_obj(tile[0], tile[1], layer_num),
                'images' : [pg.transform.scale(tile[2], self.tile_size)],
                'index' : 0}
            properties = self.level.get_tile_properties(
                tile[0], tile[1], layer_num)
            if properties and properties.get('frames'):
                tile_dict.update({'images' : [],
                                  'timer' : -100,
                                  'frames' : properties['frames']})
                for frame in tile_dict['frames']:
                    image = self.level.get_tile_image_by_gid(frame.gid)
                    image = pg.transform.scale(image, self.tile_size)
                    image.set_colorkey((0, 0, 0))
                    tile_dict['images'].append(image)
            self.tiles[(tile[0], tile[1], layer_num)] = tile_dict

            pos = (tile_dict['pos'].x * self.tile_width,
                   tile_dict['pos'].y * self.tile_height)
            sc.draw_queue.append(
                {'layer' : 1 if tile_dict['pos'].layer == 0 else 2,
                 'func' : self.bg.blit,
                 'args' : (tile_dict['images'][0], pos)})

    def draw_area(self, area, scroll):
        """Draw specific area of the level."""
        sc.draw_queue.append({'layer' : 11, 'surf' : self.bg,
                              'pos' : (area.x, area.y - scroll),
                              'area' : area})

    def draw(self, scroll):
        """Draw the whole level."""
        area = pg.Rect((0, scroll), sc.screen.get_size())
        sc.draw_queue.append({'layer' : 3, 'surf' : self.bg,
                              'pos' : (0, 0), 'area' : area})

    def animate(self, elapsed_time, scroll):
        """
        Update and draw each animated tile.
        Should be called every frame.
        """
        for tile in self.animated_tiles:
            tile['timer'] += elapsed_time
            if tile['timer'] >= tile['frames'][tile['index']].duration:
                self.draw_tile(scroll, tile)
                tile['timer'] -= tile['frames'][tile['index']].duration
                tile['index'] = (tile['index'] + 1) % len(tile['frames'])

    def draw_tile(self, scroll, tile):
        """
        Draw 'tile' and the one above or below it.
        Can't animate two tiles in the same pos.
        """
        tile_2 = self.tiles.get((tile['pos'].x, tile['pos'].y,
                                 1 if tile['pos'].layer == 0 else 0))
        pos = (tile['pos'].x * self.tile_width,
               tile['pos'].y * self.tile_height - scroll)
        if tile_2:
            sc.draw_queue.append(
                {'layer' : 10 if tile_2['pos'].layer == 0 else 11,
                 'func' : sc.screen.blit, 'args' : (tile_2['images'][0], pos)})
        sc.draw_queue.append(
            {'layer' : 10 if tile['pos'].layer == 0 else 11,
             'func' : sc.screen.blit,
             'args' : (tile['images'][tile['index']], pos)})


class Node(object):
    """
    Class for nodes on the level.
    Nodes can activate something when the player gets within the radius.

    class methods: from_level
    methods: __init__, scale, collides
    instance variables: x_pos, y_pos, radius, active, next_node,
                        action, name
    """

    def __init__(self, radius, pos, name, node_id, properties, text=None):
        """Initialize instance variables."""
        self.x_pos, self.y_pos = pos
        self.name = name
        self.id = node_id
        self.radius = radius
        self.text = text
        self.active = properties['active']
        self.next_node = properties['next_node']
        self.action = properties['action']

    def scale(self, multiplier):
        """Scale radius."""
        self.radius = int(self.radius * multiplier)
        self.x_pos = int(self.x_pos * multiplier)
        self.y_pos = int(self.y_pos * multiplier)
        if self.text:
            self.text.scale(multiplier)

    def collides(self, pos):
        """Check if pos collides with text."""
        x, y = pos
        return hypot(self.x_pos - x, self.y_pos - y) <= self.radius

    def draw(self, scroll):
        """Add a circle to the draw queue."""
        pos = (int(self.x_pos), int(self.y_pos - scroll))
        sc.draw_queue.append(
            {'layer' : 15, 'func' : pg.draw.circle,
             'args' : (sc.screen, (0, 0, 180), pos, self.radius)})

    def update_text(self):
        """Update and draw text."""
        self.text.next()
        if self.text.active:
            self.text.draw()


class NodeGroup(object):
    """
    Convenience class for a group of node objects.

    class methods: from_level
    instance variables: nodes
    methods: draw, scale, check, __iter__
    """

    @classmethod
    def from_level(cls, level, text_dict):
        """Return a NodeGroup from a pytmx TiledMap and text."""
        radius = pg.display.get_surface().get_width() // level.width // 2
        nodes = list()
        for obj in level.objects:
            obj.x *= sc.screen.get_width() / 1680.0
            obj.y *= sc.screen.get_height() / 1050.0
            for name, text in zip(text_dict.keys(), text_dict.values()):
                if name == obj.name:
                    nodes.append(Node(radius, (obj.x, obj.y), obj.name, obj.id,
                                      obj.properties, text=text))
                    break
            else:
                nodes.append(Node(radius, (obj.x, obj.y), obj.name, obj.id,
                                  obj.properties))
        return NodeGroup(nodes)

    def __init__(self, nodes):
        """Set instance variables."""
        self.nodes = nodes

    def __iter__(self):
        """Yield each node."""
        for node in self.nodes:
            yield node

    def scale(self, multiplier):
        """Scale each node."""
        for node in self.nodes:
            node.scale(multiplier)

    def draw(self, scroll):
        """Add each active node to the draw queue."""
        for node in [n for n in self.nodes if n.active == '1']:
            screen_rect = pg.Rect(
                (0, scroll), pg.display.get_surface().get_size())
            if screen_rect.collidepoint((node.x_pos, node.y_pos)):
                node.draw(scroll)

    def check(self, player):
        """Update the active nodes that collide with pos."""
        pos = player.rect.center
        for node in self.nodes:
            if node.active == '1' and node.collides(pos):
                if node.text:
                    node.update_text()
                    player.stop()

