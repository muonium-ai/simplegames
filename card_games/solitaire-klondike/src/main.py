#!/usr/bin python3
import argparse
import pygame
from gamemanager import GameManager

def main():
    parser = argparse.ArgumentParser(description="Play solitaire.")
    parser.add_argument('--easy_mode', dest='easy_mode', default='N', choices=['Y', 'N'], help='easy mode active')
    parser.add_argument('-autowin', dest='autowin', default=False, action="store_true")
    args = parser.parse_args()

    easy_mode = False
    if args.easy_mode == 'Y':
        easy_mode = True

    gameManager = GameManager(easy_mode, args.autowin)
    gameManager.playGame()

if __name__ == "__main__":
    main()