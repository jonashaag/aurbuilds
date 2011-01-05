from aurbuilds import config
from aurbuilds.utils import execute_command

class Pacman(object):
    executable = config.PACMAN_EXE

    def __init__(self, root=None, config=None, cachedir=None):
        self.root = root
        self.config = config
        self.cachedir = cachedir

    def refresh_database(self):
        self.execute('-Sy')

    def install(self, packages, only_needed=True, as_dependency=False):
        args = []
        if only_needed: args.append('--needed')
        if as_dependency: args.append('--asdeps')
        args.append('-S')
        args.extend(packages)
        self.execute(*args)

    def execute(self, *args):
        execute_command(*self._get_command(*args))

    def _get_command(self, *args):
        command = [self.executable, '--noconfirm']
        if self.root:
            command.extend(['--root', self.root])
        if self.config:
            command.extend(['--config', self.config])
        if self.cachedir:
            command.extend(['--cachedir', self.cachedir])
        command.extend(args)
        return command
