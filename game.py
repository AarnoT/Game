"""
Main module of the game.

classes: Game
objects: game
functions: test_quit
"""
import sys
import os.path
import logging
import pygame
sys.path.append(os.path.realpath('modules'))
pygame.init()
logging.basicConfig(format='[%(asctime)s] %(message)s', level=logging.DEBUG)

import state
import screen
import text
import sprite
import level

def test_quit():
    """Test if the game should quit. Return True or False."""
    if pygame.event.peek(pygame.KEYDOWN):
        events = pygame.event.get(pygame.KEYDOWN)
        for event in events:
            if pygame.key.name(event.key) == 'escape':
                return False
        return True
    else:
        return not pygame.event.peek(pygame.QUIT)

class Game(object):
    """
    Class for the game loop and managing states.

    methods: __init__, main_loop, event_loop, resize, change_level,
    update_level, change_state, next_state
    instance variables: current_state, states, fps, clock, game_state
    """

    def __init__(self, StartState):
        """
        Instantiate StartState and create variables.

        StartState should be one of the states in the states module.
        """
        self.current_state = StartState(self)
        self.states = {
        'world_state' : state.WorldState,
        'battle_state' : state.BattleState,
        'menu_state' : state.MenuState}
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.game_state = self.current_state.name

    def main_loop(self):
        """Loop while the game is running."""
        logging.info('Main loop started.')
        running = True
        while running:
            running = test_quit()
            game.clock.tick(game.fps)
            current_fps = int(game.clock.get_fps())
            pygame.display.set_caption('The Game, FPS:{}'.format(current_fps))
            self.event_loop()
            self.current_state.update()
        logging.info('Game quitting.')

    def event_loop(self):
        """Loop through events."""
        for event in pygame.event.get():
            if event.type is pygame.VIDEORESIZE:
                self.resize(event.size)
            elif event.type is pygame.MOUSEBUTTONDOWN:
                self.current_state.handle_events()

    def resize(self, res=pygame.display.list_modes()[0], flags=None):
        """Resize the game."""
        logging.info('Resizing screen.')
        if flags is None:
            flags = screen.var.screen.get_flags()
        screen.var = screen.Screen(res, flags)
        old_w, old_h = level.level.tile_w, level.level.tile_h
        self.change_level(self.current_state.levels[0])
        self.update_level()
        for character in sprite.main_group:
            character.x_pos *= level.level.tile_w / float(old_w)
            character.y_pos *= level.level.tile_h / float(old_h)
        level.level.scroll *= level.level.tile_h / float(old_h)
        sprite.player.scale(level.level.tile_w, level.level.tile_h)
        text.var = text.TextCreate(res)
        if isinstance(self.current_state, state.MenuState):
            self.current_state.create_buttons()
            for button in self.current_state.buttons:
                pos = (button.rect.x + button.rect.width / 3, (
                    button.rect.y + button.rect.height / 2))
                button.draw(pos, level.level.scroll)
        elif isinstance(self.current_state, state.BattleState):
            self.current_state.create_buttons()

    def change_level(self, level_name):
        """Switch level to level_name."""
        level.level = level.Level(level_name)

    def update_level(self):
        """Redraws the background and the midground."""
        bg, mg = level.level.draw()
        screen.var.background.blit(bg, (0, 0))
        screen.var.midground.blit(mg, (0, 0))
        screen.var.background.convert()
        screen.var.midground.convert()

    def switch_state(self, state):
        """Check if state is valid and switch to it."""
        if state in self.states.keys():
            self.current_state = states[state]
        elif state in self.states.values():
            self.current_state = state
        else:
            raise ValueError('That isn\'t a valid state.')
        screen.var = screen.Screen(
            screen.var.screen.get_size(), screen.var.screen.get_flags())

    def next_state(self):
        """Switch to the next state."""
        next_state = self.current_state.NextState(self)
        self.current_state = next_state
        screen.var = screen.Screen(
            screen.var.screen.get_size(), screen.var.screen.get_flags())

if __name__ == '__main__':
    game = Game(state.MenuState)
    game.update_level()
    game.main_loop()

