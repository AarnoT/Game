"""
Module for sprites.

classes: Sprite, Enemy, Projectile
objects: main_group, enemy_group, player
"""

from itertools import cycle
import logging
import pygame

import level

main_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

class Sprite(pygame.sprite.Sprite):
    """
    Parent class for all sprites.

    methods: __init__, load_frames, scale, draw_health, move,
    calc_velocity, check_stop, update, check_dead, animate
    instance variables: 
    x_pos, y_pos, x_target, y_target, x_velocity, y_velocity, state,
    frames, image, rect, health, previous_scroll, hp_surf
    subclasses: Enemy, Projectile
    """

    def __init__(self, spawn_pos, frames):
        """
        Create variables.

        frames should be a dictionary with keys for each state.
        """
        self.groups = main_group
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x_pos, self.y_pos = spawn_pos
        self.x_target, self.y_target = self.x_pos, self.y_pos
        self.x_velocity, self.y_velocity = 0.0, 0.0
        self.state = 'still'
        self.frames = {'delay' : cycle(range(10, 0, -1))}
        self.frames.update(frames)
        self.frames['still'] = cycle(self.load_frames(self.frames['still']))
        self.frames['moving'] = self.load_frames(self.frames['moving'])
        self.frames['moving_right'] = cycle(self.frames['moving'])
        self.frames['moving_left'] = cycle([pygame.transform.flip(
            frame, True, False) for frame in self.frames['moving']])
        self.image = self.frames['still'].next().convert_alpha()
        self.scale(level.level.tile_w, level.level.tile_h)
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.health = 100.0
        self.hp_surf = None
        self.previous_scroll = 0

    def load_frames(self, frames):
        """Load frames from an iterable of strings."""
        return [
            pygame.image.load('images/' + frame) for frame in frames]

    def scale(self, width, height):
        """Scale self.image."""
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

    def draw_health(self, tile_w):
        """Draw health as text and blit it onto the screen."""
        font = pygame.font.Font(None, int(0.25 * tile_w))
        self.hp_surf = font.render(
            '{}/100'.format(int(self.health)), 0, (255, 255, 255), (0, 0, 0))
        self.hp_surf.set_colorkey((0, 0, 0))
        pygame.display.get_surface().blit(
            self.hp_surf.convert(), self.rect.topleft)

    def move(self, pos):
        """Update velocity."""
        self.x_target, self.y_target = pos
        self.previous_scroll = level.level.scroll
        if abs(self.y_target - self.y_pos) > abs(self.x_target - self.x_pos):
            self.y_velocity, self.x_velocity = self.calc_velocity(
                self.y_target, self.x_target, self.y_pos, self.x_pos)
        elif abs(self.x_target - self.x_pos) >= abs(self.y_target - self.y_pos):
            self.x_velocity, self.y_velocity = self.calc_velocity(
                self.x_target, self.y_target, self.x_pos, self.y_pos)
        if self.x_velocity < 0:
            self.state = 'moving_left'
        else:
            self.state = 'moving_right'

    def calc_velocity(self, target_1, target_2, pos_1, pos_2):
        """Calculate new velocity based on target and return it."""
        # vel_multiplier scales based on display width
        vel_multiplier = pygame.display.get_surface().get_width() / 1360.0
        if target_1 > pos_1:
            velocity_1 = 3.0 * vel_multiplier
        elif target_1 < pos_1:
            velocity_1 = -3.0 * vel_multiplier
        else:
            velocity_1 = 0.0
        velocity_2 = 3.0 * vel_multiplier * min((target_2 - pos_2) / (
            max(abs(target_1 - pos_1), 0.00001)), 1.0)
        return velocity_1, velocity_2

    def check_dead(self):
        """Check if the sprite is dead."""
        if self.health <= 0.0:
            self.kill()

    def check_stop(self):
        """Check if sprite should stop."""
        if self.x_velocity > 0 and self.x_pos > self.x_target - 2:
            self.x_velocity = 0.0
        elif self.x_velocity < 0 and self.x_pos < self.x_target + 2:
            self.x_velocity = 0.0
        real_y = self.y_pos + level.level.scroll - self.previous_scroll
        if self.y_velocity > 0 and real_y > self.y_target - 2:
            self.y_velocity = 0.0
        elif self.y_velocity < 0 and real_y < self.y_target + 2:
            self.y_velocity = 0.0
        if self.y_velocity == 0.0 == self.x_velocity:
            self.state = 'still'

    def animate(self):
        """Update self.image to the next frame based on state."""
        if self.frames['delay'].next() == 1:
            self.image = self.frames[self.state].next().convert_alpha()
            self.scale(level.level.tile_w, level.level.tile_h)

    def update(self, time_delta):
        """Update character. Should be called every frame."""
        self.check_dead()
        self.check_stop()
        self.animate()
        self.x_pos += self.x_velocity * time_delta
        self.y_pos += self.y_velocity * time_delta
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        if self.y_velocity != 0 or self.x_velocity != 0:
            self.draw_health(level.level.tile_w)
        elif self.hp_surf is not None:
            pygame.display.get_surface().blit(self.hp_surf, self.rect.topleft)

for obj in level.level.level.objects:
    if obj.name == 'spawn':
        spawn = (float(obj.x), float(obj.y))
        break
    spawn = (100, 100)
player = Sprite(spawn, {'still' : ['guy.png'], 'moving' : [
    'dude1.png', 'dude2.png', 'dude3.png', 'dude2.png']})

class Enemy(Sprite):
    """
    Subclass of Sprite with path finding.

    methods: __init__, find_path
    """

    def __init__(self, pos, image_name):
        """Initialize parent and join enemy_group."""
        Sprite.__init__(self, pos, image_name)
        enemy_group.add(self)

    def find_path(self, tile_size, skele_pos, solid_tiles):
        """Find a path and move towards the player."""
        # Could be split into smaller functions, but it seems tricky.
        tile_w, tile_h = tile_size
        x, y = self.x_pos // tile_w, self.y_pos // tile_h
        invalid_tiles = skele_pos + solid_tiles
        path_counter = 1
        path = {}

        def path_horizontal(path, x, change):
            if (x + change, y) not in invalid_tiles + path.keys():
                path[(x + change, y)] = path_counter
                x += change
            return path, x

        def path_vertical(path, y, change):
            if (x, y + change) not in invalid_tiles + path.keys():
                path[(x, y + change)] = path_counter
                y += change
            return path, y

        def make_path(
            path, pos_1, target_1, size_1, func_1,
            pos_2, target_2, size_2, func_2):
            if pos_1 - target_1 // size_1 > 0:
                path, pos_1 = func_1(path, pos_1, -1)
            elif pos_1 - target_1 // size_1 < 0:
                path, pos_1 = func_1(path, pos_1, 1)
            elif pos_2 - target_2 // size_2 != 0:
                compare = cmp(pos_2 - target_2 // size_2, 0)
                if (pos_2 - compare, pos_1) not in invalid_tiles + path.keys():
                    path, pos_2 = func_2(path, pos_2, -compare)
                elif (
                    pos_2 + compare, pos_1) not in invalid_tiles + path.keys():
                    path, pos_2 = func_2(path, pos_2, compare)
            elif pos_1 - target_1 // size_1 > 0:
                path, pos_1 = func_1(path, pos_1, 1)
            elif pos_1 - target_1 // size_1 < 0:
                path, pos_1 = func_1(path, pos_1, -1)
            return path, pos_1, pos_2

        while abs(player.x_pos // tile_w - x) + abs(
            player.y_pos // tile_h - y) > 1 and (path_counter <= 100):
            x_diff, y_diff = abs(
                player.x_pos // tile_w - x), abs(player.y_pos // tile_h - y)
            if y_diff > x_diff:
                path, y, x = make_path(
                    path, y, player.y_pos, tile_h, path_vertical, x,
                    player.x_pos, tile_w, path_horizontal)
            else:
                path, x, y = make_path(
                    path, x, player.x_pos, tile_w, path_horizontal, y,
                    player.y_pos, tile_h, path_vertical)
            path_counter += 1

        if len(path) > 0:
            x, y = self.x_pos // tile_w, self.y_pos // tile_h
            nearby_tiles = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            move_tile = ((self.x_pos // tile_w, self.y_pos // tile_h), 0)
            for tile in [tile for tile in nearby_tiles if tile in path]:
                # Choose the tile that's the furthest on the path.
                if path[tile] > move_tile[1]:
                    move_tile = (tile, path[tile])
            self.x_target, self.y_target = move_tile[0]
            self.x_target = self.x_target * tile_w + tile_w / 2
            self.y_target = self.y_target * tile_h + tile_h / 2
        self.move((self.x_target, self.y_target))

class Projectile(Sprite):
    """
    Subclass of Sprite for projectiles.

    methods: __init__, check_dead
    """

    def __init__(self, pos_1, pos_2):
        """Initialize parent and move to target."""
        Sprite.__init__(self, pos_1, {
            'still' : ['energyball.png'], 'moving' : ['energyball.png']})
        self.move(pos_2)

    def check_dead(self):
        """Override parent method."""
        if abs(self.x_velocity) + abs(self.y_velocity) <= 0:
            self.kill()

