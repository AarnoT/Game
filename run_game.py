"""Script to run the game."""

import pygame as pg

pg.init()

from modules.game import Game

if __name__ == '__main__':
    Game.main_loop()


