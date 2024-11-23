from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt
import pygame
import random
import sys
from enum import Enum
from config import *
from minesweeper import Minesweeper


def main():
    pygame.init()
    filename = None
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    game = Minesweeper(filename)
    game.run()

if __name__ == "__main__":
    main()
