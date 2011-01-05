import os
import glob
import shutil
from os.path import basename, normpath
from subprocess import Popen, PIPE

class ExecutionError(Exception):
    pass

def joinpaths(first, *rest):
    for path in rest: assert not path.startswith('/')
    return os.path.join(first, *rest)

def execute_command(*command):
    from aurbuilds import config
    capture_stdout = not config.DEBUG
    proc = Popen(command, stderr=PIPE, stdout=(PIPE if capture_stdout else None))
    if proc.wait() != 0:
        info = 'stderr: %r' % proc.stderr.read()
        if capture_stdout:
            info += '\n%r' % proc.stdout.read()
        raise ExecutionError(
            '%s exited with code %d\n%s' % (command, proc.returncode, info))

def parent_dir(filename):
    return normpath(joinpaths(basename(normpath(filename)), '..'))

def find_package_in(directory):
    files = glob.glob(joinpaths(directory, '*.pkg.*'))
    assert len(files) == 1
    return files[0]

def update_repository(architecture, package):
    from aurbuilds.config import REPO
    repo = REPO.format(arch=architecture)
    if not os.path.exists(repo):
        os.makedirs(repo)
    shutil.copy(package, repo)
    database = joinpaths(repo, 'aurbuilds.db.tar.gz')
    execute_command('repo-add', database, package)
