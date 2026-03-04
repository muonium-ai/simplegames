from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import sys, os, subprocess

if __name__ == "__main__":
    try:
        import pygame
    except ModuleNotFoundError:
        try:
            import pip
        except ModuleNotFoundError:
            sys.exit("Could not import pip package manager. Please install pip for your python distribution.")

        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pygame'])
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pygame'])

    sys.path.insert(0, "%s/src/" % os.path.dirname(os.path.realpath(__file__)))

    import main

    main.main()