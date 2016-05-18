"""
Module for battle related functions.

Contains BattleTiles class and its object var.
"""

from itertools import product
import logging
import pygame

import screen
import level

class BattleTiles(object):
    """
    Handle tiles in the battle state.

    methods: __init__, incorrect_tiles, update_tiles,
            get_solid_tiles, get_valid_tiles, draw_tiles
    instance variables:
    turn, selected_tile, move_tiles, spell_tiles, solid_tiles
    """

    def __init__(self):
        """Create variables."""
        self.turn = 0
        self.selected_tile = None
        self.move_tiles = []
        self.spell_tiles = []
        self.solid_tiles = []

    def incorrect_tiles(self, x_pos, y_pos):
        """
        Check if tiles are too far from the player position.

        Return true or false.
        """
        tile_w, tile_h = level.level.tile_w, level.level.tile_h
        return any(
            abs(tile[0] - x_pos // tile_w) + abs(tile[1] - y_pos // tile_h)
            >= 2 for tile in self.move_tiles)

    def update_tiles(self, objects, player):
        """
        Update and draw tiles.

        objects should be a list of pytmx objects.
        """
        tile_w, tile_h = level.level.tile_w, level.level.tile_h
        self.get_solid_tiles(objects)
        self.get_valid_tiles(player.x_pos // tile_w, player.y_pos // tile_h)
        self.draw_tiles()

    def get_solid_tiles(self, objects):
        """Append solid tiles to a list based on pytmx objects."""
        self.solid_tiles = []
        scroll = level.level.scroll
        tile_w, tile_h = level.level.tile_w, level.level.tile_h
        for obj in objects:
            # if hasattr(obj, 'type') and obj.type == 'solid':
            x_range = range(
                int(obj.x // tile_w), int(obj.x + obj.width) // tile_w)
            y_range = range(int(obj.y - scroll + tile_h / 2) // tile_h, int(
                obj.y + obj.height - scroll + tile_h / 2) // tile_h)
            # product is the same as a nested for-loop.
            for pos in product(x_range, y_range):
                self.solid_tiles.append(pos)

    def get_valid_tiles(self, player_column, player_row):
        """Append valid tiles around the player to a list."""
        self.move_tiles = []
        for x in range(-1, 2):
            if (player_column + x, player_row) not in self.solid_tiles:
                self.move_tiles.append((player_column + x, player_row))
        for y in range(-1, 2):
            if (player_column, player_row + y) not in self.solid_tiles:
                self.move_tiles.append((player_column, player_row + y))
        self.spell_tiles = []
        for x in range(-2, 3):
            for y in range(-2, 3):
                if x ** 2 + y ** 2 == 4:
                    self.spell_tiles.append((x + player_column, y + player_row))

    def draw_tiles(self):
        """Draw tiles onto background based on a list of coordinates."""
        scroll = level.level.scroll
        tile_w, tile_h = level.level.tile_w, level.level.tile_h
        tiles = self.move_tiles + self.solid_tiles + self.spell_tiles
        move_colors = [(0, 0, 255) for _ in range(len(self.move_tiles))]
        solid_colors = [(255, 0, 255) for _ in range(len(self.solid_tiles))]
        spell_colors = [(125, 255, 125) for _ in range(len(self.spell_tiles))]
        for tile, color in zip(tiles, move_colors + solid_colors + spell_colors):
            tile_rect = pygame.Rect((
                tile[0] * tile_w, (tile[1] * tile_h + scroll + tile_h / 2) - (
                scroll + tile_h / 2) % tile_h), (tile_w, tile_h))
            s = pygame.Surface((int(tile_rect.width), int(tile_rect.height)))
            s.fill(color)
            s.set_alpha(220)
            screen.var.midground.blit(s.convert_alpha(), tile_rect)
            # pygame.draw.rect(screen.var.midground, color, tile_rect)

var = BattleTiles()

