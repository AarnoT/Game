"""
Module for states.

classes: State, WorldState, BattleState, MenuState
"""

import logging
import pygame

import screen
import text
import battle
import sprite
import button
import level

class State(object):
    """
    Base class for game states.

    methods: __init__, update_screen
    instance variables: game, name, NextState, active
    subclasses: WorldState, BattleState, MenuState
    """

    def __init__(self, game, name):
        """Create variables. game should be the game object."""
        self.game = game
        self.name = None
        self.NextState = None
        self.active = True
        logging.info(name + ' is now active.')

    def update_screen(self):
        """Update the screen."""
        level.level.scroll_level(screen.var.screen.get_size()[1],
            sprite.player, sprite.enemy_group)
        midground_copy = screen.var.midground.copy()
        x, y = text.var.text_position
        if len(text.var.surfaces) > 0:
            midground_copy.blit(text.var.surfaces[text.var.text_index],
                (x, y + level.level.scroll))
        screen_rect = pygame.Rect(
            (0, level.level.scroll), screen.var.screen.get_size())
        screen.var.screen.blit(screen.var.background, (0, 0), screen_rect)
        screen.var.screen.blit(midground_copy, (0, 0), screen_rect)
        screen.var.screen.blit(screen.var.foreground, (0, 0), screen_rect)
        sprite.main_group.update(self.game.clock.get_time() / 16.67)
        sprite.main_group.draw(screen.var.screen)
        pygame.display.flip()
        sprite.main_group.clear(screen.var.screen, screen.var.background)

class WorldState(State):
    """
    Handle interactions in the world state.

    methods: __init__, update, handle_events
    instance variables: name, NextState, levels
    """

    def __init__(self, game):
        """Create variables. Extends parent method."""
        self.name = 'world_state'
        State.__init__(self, game, self.name)
        self.NextState = BattleState
        self.levels = ('testmap.tmx', 'testmap2.tmx')

    def update(self):
        """Update the state. Called every frame."""
        self.update_screen()

    def handle_events(self):
        """Check if player should move and if text should be shown."""
        if text.var.text_index == len(text.var.surfaces):
            sprite.player.move(pygame.mouse.get_pos())
        elif not text.var.rect.collidepoint(pygame.mouse.get_pos()):
            sprite.player.move(pygame.mouse.get_pos())
        obj = level.level.check_objects((sprite.player.x_target,
                sprite.player.y_target + level.level.scroll))
        if len(text.var.surfaces) != 0:
            text.var.more_text()
        elif text.var.rect.collidepoint(pygame.mouse.get_pos()):
            text.var.more_text()
        elif obj is not None and obj.name in text.var.text:
            if text.var.text_index == len(text.var.surfaces):
                text.var.new_text(text.var.text[obj.name])
            else:
                text.var.more_text()
        if obj is not None and obj.action == 'battle':
            self.game.next_state()
            self.game.update_level()
        elif obj is not None and obj.action == 'next map':
            level.level = level.Level('testmap2.tmx')
            self.game.update_level()

class BattleState(State):
    """
    Class for battle functionality.

    methods:
    __init__, update, handle_events, init_battle, create_buttons,
    tile_selected, action_selected, battle_over, player_stopped
    instance variables:
    name, NextState, levels, buttons, phase, active_buttons
    """

    def __init__(self, game):
        """Create variables. Extends parent method."""
        self.name = 'battle_state'
        State.__init__(self, game, self.name)
        self.NextState = WorldState
        self.levels = ('testmap.tmx',)
        self.buttons = {}
        self.phase = 'tile'
        self.active_buttons = 'option'

    def update(self):
        """Update the state. Called every frame."""
        if sprite.player.x_velocity == 0 == sprite.player.y_velocity:
            self.player_stopped()
        self.update_screen()

    def handle_events(self):
        """Call a function for the next part of the battle."""
        if sprite.player.x_velocity == 0 == sprite.player.y_velocity:
            self.game.update_level()
            if battle.var.turn != 0:
                for button in self.buttons.values():
                    button.clear(level.level.scroll)
            if battle.var.turn == 0:
                self.init_battle()
            elif self.phase == 'tile':
                self.tile_selected()
            elif self.phase == 'action':
                self.action_selected()
                self.battle_over()

    def init_battle(self):
        """Initialize a battle."""
        text.var.new_text(text.var.text['battleinfo'], (0, 0, 255))
        battle.var.turn += 1
        tile_w, tile_h = level.level.tile_w, level.level.tile_h
        sprite.skele = sprite.Enemy((5.0 * tile_w, 5.0 * tile_h), {
            'still' : ['skeleton.png'], 'moving' : ['skeleton.png']})
        sprite.player.y_pos -= (
            (sprite.player.y_pos + level.level.scroll) % level.level.tile_h)
        sprite.player.y_pos += level.level.tile_h / 2
        self.create_buttons()

    def create_buttons(self):
        """Create arguments and use them to create buttons."""
        tile_w, tile_h = level.level.tile_w, level.level.tile_h
        x_pos, y_pos = text.var.text_position[0], text.var.text_position[1]
        move_rect = pygame.Rect(x_pos + 100, y_pos + 50, 100, 50)
        spell_rect = pygame.Rect(x_pos + 500, y_pos + 50, 100, 50)

        def move_action():
            if battle.var.selected_tile in battle.var.move_tiles:
                sprite.player.move((
                    battle.var.selected_tile[0] * tile_w + tile_w / 2,
                    battle.var.selected_tile[1] * tile_w + tile_h / 2))
                sprite.skele.find_path(
                    (tile_w, tile_h), [], battle.var.solid_tiles)
            battle.var.selected_tile = None

        def spell_action():
            text.var.new_text(text.var.text['button'])
            button = self.buttons['spell_1']
            self.buttons['spell_1'].draw((button.rect.x, button.rect.y), level.level.scroll)
            button = self.buttons['spell_2']
            self.buttons['spell_2'].draw((button.rect.x, button.rect.y), level.level.scroll)
            self.active_buttons = 'spell'

        def use_spell():
            if battle.var.selected_tile in battle.var.spell_tiles:
                for enemy in sprite.enemy_group:
                    if battle.var.selected_tile == (
                        enemy.x_pos // tile_w, enemy.y_pos // tile_h):
                        enemy.health -= 50
                        sprite.skele.find_path(
                            (tile_w, tile_h), [], battle.var.solid_tiles)
                        sprite.Projectile(
                            (sprite.player.x_pos, sprite.player.y_pos),
                            (enemy.x_pos, enemy.y_pos))
            battle.var.selected_tile = None

        self.buttons['move'] = (button.Button(
            move_rect, 'Move', text.var.font, move_action))
        self.buttons['spell'] = (button.Button(
            spell_rect, 'Use a spell', text.var.font, spell_action))
        self.buttons['spell_1'] = (button.Button(
            move_rect, 'Spell 1', text.var.font, use_spell))
        self.buttons['spell_2'] = (button.Button(
            spell_rect, 'Spell 2', text.var.font, use_spell))

    def tile_selected(self):
        """Called when the player selects a tile."""
        tile_w, tile_h = level.level.tile_w, level.level.tile_h
        text.var.more_text()
        if len(text.var.surfaces) == 0:
            battle.var.update_tiles(level.level.level.objects, sprite.player)
        if battle.var.selected_tile is not None:
            if self.active_buttons == 'option':
                self.buttons['move'].check(pygame.mouse.get_pos())
                self.buttons['spell'].check(pygame.mouse.get_pos())
            elif self.active_buttons == 'spell':
                self.buttons['spell_1'].check(pygame.mouse.get_pos())
                self.buttons['spell_2'].check(pygame.mouse.get_pos())
                self.active_buttons = 'option'
        if len(text.var.surfaces) == 0:
            battle.var.selected_tile = None
        if battle.var.selected_tile is None:
            self.phase = 'action'

    def action_selected(self):
        """Draw tiles and show a text with buttons."""
        x, y = pygame.mouse.get_pos()
        tile_w, tile_h = level.level.tile_w, level.level.tile_h
        tile_rect = pygame.Rect(x - x % tile_w,
            (y + level.level.scroll) - (y + level.level.scroll) % tile_h,
            tile_w, tile_h)
        s = pygame.Surface((int(tile_rect.width), int(tile_rect.height)))
        s.fill((255, 0, 0))
        s.set_alpha(220)
        screen.var.midground.blit(s.convert_alpha(), tile_rect)
        # pygame.draw.rect(screen.var.midground, (255, 0, 0), tile_rect)
        battle.var.selected_tile = (x // tile_w, y // tile_h)
        text.var.new_text(text.var.text['button'])
        if text.var.text_index >= 0 and text.var.text_index < len(
            text.var.surfaces):
            self.phase = 'tile'
        x, y = text.var.text_position
        button = self.buttons['move']
        self.buttons['move'].draw((button.rect.x, button.rect.y), level.level.scroll)
        button = self.buttons['spell']
        self.buttons['spell'].draw((button.rect.x, button.rect.y), level.level.scroll)

    def battle_over(self):
        """End battle if all enemies are dead."""
        if len(sprite.enemy_group) <= 0:
            for character in sprite.main_group:
                if character is not sprite.player:
                    character.kill()
            battle.var = battle.BattleTiles()
            text.var.surfaces = []
            self.game.next_state()
            self.game.update_level()

    def player_stopped(self):
        """Reposition player and tiles."""
        lvl = level.level
        player = sprite.player
        offset = (player.y_pos + level.level.scroll) % level.level.tile_h - (
            level.level.tile_h / 2)
        if offset < -5 or offset > 5:
            logging.info('Repositioning player.')
            player.y_pos -= (
                (player.y_pos + level.level.scroll) % level.level.tile_h)
            player.y_pos += level.level.tile_h / 2
        if battle.var.incorrect_tiles(player.x_pos, player.y_pos):
            logging.debug('Repositioning tiles.')
            self.game.update_level()
            battle.var.move_tiles, battle.var.solid_tiles = [], []
            battle.var.update_tiles(lvl.level.objects, player)

class MenuState(State):
    """
    Class for the menu.

    methods: __init__, create_buttons, update, handle_events
    instance variables: name, NextState, levels, buttons
    """

    def __init__(self, game):
        """Create variables. Extends parent method."""
        self.name = 'menu_state'
        State.__init__(self, game, self.name)
        self.NextState = WorldState
        self.levels = ('menu.tmx',)
        self.create_buttons()
        for button in self.buttons:
            pos = (
                button.rect.x + button.rect.width / 3,
                button.rect.y + button.rect.height / 2)
            button.draw(pos, level.level.scroll)

    def create_buttons(self):
        """Create arguments and use them to create buttons."""
        def start_game():
            screen.var.midground.fill((0, 0, 0))
            self.game.next_state()
            self.game.change_level(self.game.current_state.levels[0])
            self.game.update_level()
        def fullscreen():
            self.game.resize(flags=pygame.FULLSCREEN)
        def exit_game():
            pygame.event.post(pygame.event.Event(pygame.QUIT, {}))
        text_list = ('START GAME', 'FULLSCREEN', 'EXIT GAME')
        action_list = [start_game, fullscreen, exit_game]
        self.buttons = [button.Button(pygame.Rect(
            obj.x, obj.y, obj.width, obj.height), info, text.var.font,
            action) for obj, info, action in zip(
                level.level.level.objects, text_list, action_list)]

    def update(self):
        """Update the state. Called every frame."""
        screen.var.background.fill((255, 255, 255))
        for button in self.buttons:
            pygame.draw.rect(
                screen.var.midground, (255, 255, 255), button.rect, 2)
            if button.rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(
                    screen.var.midground, (1, 1, 1), button.rect, 2)
            if self.game.current_state is not self:
                break
        self.update_screen()

    def handle_events(self):
        """If mouse is on button call button action."""
        for button in self.buttons:
            if button.rect.collidepoint(pygame.mouse.get_pos()):
                button.action()

