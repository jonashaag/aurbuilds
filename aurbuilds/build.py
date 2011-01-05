import os
import shutil
from aurbuilds import config
from aurbuilds.pacman import Pacman
from aurbuilds.utils import execute_command, joinpaths

CHROOT_TEMPLATE = joinpaths(config.ROOT, 'template-{arch}')
CHROOT = joinpaths(config.ROOT, 'build-{arch}')

BASEDIRS = ['var/lib/pacman', 'sys', 'proc', 'dev', 'dev/shm', 'dev/pts']
BASEPACKAGES = ['pacman', 'util-linux-ng', 'base-devel',
                'gzip', 'file', 'curl', 'wget']

def setup_environment_template(architecture):
    env = Environment(CHROOT_TEMPLATE.format(arch=architecture))

    os.makedirs(env.root)
    for basedir in BASEDIRS:
        os.makedirs(joinpaths(env.root, basedir))

    pacman = Pacman(env.root, config=joinpaths(config.STUFF, 'pacman.conf'),
                    cachedir=config.GLOBAL_PACMAN_CACHE)
    pacman.refresh_database()
    pacman.install(BASEPACKAGES)

    with env:
        for src, dst, mode in [
            ('resolv.conf', '/etc', None),
            ('pacman.conf', '/etc', None),
            ('mirrorlist-%s' % architecture, '/etc/pacman.d/mirrorlist', None),
            ('buildpkg', '/usr/bin/buildpkg', '+x'),
        ]:
            shutil.copy(joinpaths(config.STUFF, src), joinpaths(env.root, dst[1:]))
            if mode:
                env.execute('chmod', mode, dst)
        env.execute('useradd', '-m', 'build')
        env.execute('chown', '-R', 'build:build', '/home/build')
    return env

class PacmanInEnvironment(Pacman):
    def __init__(self, environ, *args, **kwargs):
        self.environ = environ
        super(PacmanInEnvironment, self).__init__(*args, **kwargs)

    def execute(self, *args):
        return self.environ.execute(*self._get_command(*args))

class Environment(object):
    def __init__(self, root, template=None):
        self.root = root
        self.template = template
        self.home = joinpaths(root, 'home', 'build')
        self.pacman = PacmanInEnvironment(self)
        self._joined = False

    def execute(self, *command):
        assert self._joined, "join first"
        execute_command('chroot', self.root, *command)

    def execute_as_build_user(self, command):
        assert isinstance(command, str)
        return self.execute('su', 'build', '-c', command)

    def __enter__(self):
        assert not self._joined, "cannot join environment twice"
        for directory in ['/dev', '/sys', '/proc']:
            execute_command('mount', '--bind', directory,
                            joinpaths(self.root, directory[1:]))
        execute_command('mount', '--bind', config.GLOBAL_PACMAN_CACHE,
                        joinpaths(self.root, 'var/cache/pacman'))
        self._joined = True

    def __exit__(self, *exc_info):
        for directory in ['dev', 'sys', 'proc', 'var/cache/pacman']:
            execute_command('umount', joinpaths(self.root, directory))
        self._joined = False

    def rollback(self):
        raise NotImplementedError

    @classmethod
    def setup_clone(cls, architecture):
        template = CHROOT_TEMPLATE.format(arch=architecture)
        root = CHROOT.format(arch=architecture)
        if not (config.DEBUG and os.path.exists(root)):
            shutil.copytree(template, root, symlinks=True)
            # XXX remove this if the Python people fixed the directory
            # permission bug in shutil.copytree
            env = cls(root)
            with env:
                env.execute('chown', '-R', 'build:build', '/home/build')
            return env
        return cls(root, template)
