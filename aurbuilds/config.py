from aurbuilds.utils import parent_dir, joinpaths

DEBUG = True
TARGET_ARCHITECTURES = ['i686']
ROOT = '/aurbuilds'
REPO = joinpaths(ROOT, 'repos', '{arch}')
STUFF = parent_dir(__file__)
GLOBAL_PACMAN_CACHE = '/var/cache/pacman/pkg'
PACMAN_EXE = 'pacman'
