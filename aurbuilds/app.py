from celery import Celery
from pkgbuild import Pkgbuild
from aurbuilds.build import Environment
from aurbuilds.utils import joinpaths, execute_command, find_package_in, \
                            update_repository

app = Celery('aurbuilds')
BaseTask = app.create_task_cls()

class BuildTask(BaseTask):
    def run(self, package_name, architecture):
        environ = Environment.setup_clone(architecture)
        with environ:
            environ.execute_as_build_user('buildpkg --download %s' % package_name)

            pkgbuild = Pkgbuild(joinpaths(environ.home, package_name, 'PKGBUILD'))
            makedepends = pkgbuild.parse_makedepends()
            depends = pkgbuild.parse_depends()
            if depends:
                environ.pacman.install(depends, as_dependency=True)
            if makedepends:
                environ.pacman.install(makedepends)

            environ.execute_as_build_user('buildpkg --build %s' % package_name)

        package_file = find_package_in(joinpaths(environ.home, package_name))
        update_repository(architecture, package_file)
        #environ.rollback()
