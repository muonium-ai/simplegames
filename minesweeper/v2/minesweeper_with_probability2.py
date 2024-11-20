from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt
import pygame
import random
from enum import Enum
from config import *
from minesweeper import Minesweeper




if __name__ == "__main__":
    game = Minesweeper()
    game.run()
