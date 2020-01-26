# pylint: disable=attribute-defined-outside-init
"""Commands to craete source and binary distributions. """

from distutils.cmd import Command
from distutils import log
from datetime import datetime
from email.utils import format_datetime

import os
import subprocess
import jinja2

from . import __version__


class sdist_dsc(Command):
    """Creates a debian source distribution (.dsc). """

    user_options = [
        ('package-name=', None, 'Package name [default: python3-<module>]'),
        ('debian-distribution=', None, 'Target distribution [default: unstable]'),
        ('python-buildsystem=', None, 'Buildsystem to use [default: pybuild]'),
        ('debian-revision=', None, 'Debian revision number [default: 1]'),
        ('debian-section=', None, 'Debian section [default: python]'),
        ('debian-urgency=', None, 'Debian section [default: low]'),
        ('dist-dir=', None, 'Directory for the build [default \'dist\']'),
        ('compat=', None, 'Debhelper compatibility level [default: 10]'),
        ('service=', None, 'Systemd service description. (can only be given in setup.py options)'),
        ('extras=', None, 'Extras to include in Depends: [default: \'\']'),

    ]

    boolean_options = []

    def initialize_options(self):
        self.package_name = None
        self.debian_distribution = 'unstable'
        self.dist_dir = 'dist'
        self.python_buildsystem = 'pybuild'
        self.debian_revision = 1
        self.debian_section = 'python'
        self.debian_urgency = 'low'
        self.compat = 10
        self.extras = ''

    def finalize_options(self):
        if self.package_name is None:
            self.package_name = 'python3-{}'.format(self.distribution.get_name()
                                                    .lower()
                                                    .replace('_', '-')
                                                    .replace('.', '-'))
        self.debian_revision = int(self.debian_revision)
        self.compat = int(self.compat)

    def run(self):

        # <dist-dir>/<package>-<version>/debian
        debian_dir = os.path.join(self.dist_dir,
                                  self.distribution.get_fullname(),
                                  'debian')
        upstream_version = self.distribution.get_version()
        package_version = '{}-{}'.format(upstream_version, self.debian_revision)

        now_rfc822 = format_datetime(datetime.now())

        dependencies = ['${misc:Depends}', '${python3:Depends}']
        build_dependencies = ['python3-setuptools', 'debhelper (>= 8)']

        if not self.distribution.ext_modules:
            build_dependencies.append('python3-all')
            architecture = 'all'
        else:
            dependencies.append('${shlibs:Depends}')
            build_dependencies.append('python3-all-dev')
            architecture = 'any'

        sdist_command = self.distribution.get_command_obj('sdist')
        sdist_command.dist_dir = self.dist_dir
        sdist_command.keep_temp = 1

        log.info('generating source distribution with sdist')
        self.run_command('sdist')

        log.info('moving the unpacked source under dist..')
        os.rename(self.distribution.get_fullname(),
                  os.path.join(self.dist_dir, self.distribution.get_fullname()))

        os.mkdir(debian_dir)

        # Prepare jinja2-renderer
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

        data = {
            'source_name': self.distribution.get_name(),
            'architecture': architecture,
            'uploaders': [],
            'debian_section': self.debian_section,
            'build_dependencies': build_dependencies,
            'dependencies': dependencies,
            'package_name': self.package_name,
            'description': self.distribution.get_description(),
            'long_description': self.distribution.get_long_description(),
            'root_dir': 'debian/{}'.format(self.package_name),
            'pydeb_version': __version__,
            'python_buildsystem': self.python_buildsystem,
            'urgency': self.debian_urgency,
            'distribution': self.debian_distribution,
            'time_now': now_rfc822,
            'package_version': package_version,
            'author': self.distribution.get_author(),
            'author_email': self.distribution.get_author_email(),
            'extras': self.extras
        }

        # Render control file
        with open(os.path.join(debian_dir, 'control'), 'wt') as f:
            f.write(env.get_template('control').render(data))

        # Render compat file
        with open(os.path.join(debian_dir, 'compat'), 'wt') as f:
            f.write('{}\n'.format(self.compat))

        # Render rules file
        with open(os.path.join(debian_dir, 'rules'), 'wt') as f:
            f.write(env.get_template('rules').render(data))

        # Render changelog
        with open(os.path.join(debian_dir, 'changelog'), 'wt') as f:
            f.write(env.get_template('changelog').render(data))


sdist_dsc.description = sdist_dsc.__doc__


class bdist_deb(Command):
    """Creates a debian binary distribution (.deb). """

    user_options = [('sign-package', None, 'Sign the resulting package'),
                    ('no-test', None, 'Do not run tests while building.')]

    boolean_options = ['sign-package', 'no-test']

    def initialize_options(self):
        self.sign_package = False
        self.no_test = False

    def finalize_options(self):
        pass

    def run(self):

        if not self.distribution.have_run.get('sdist_dsc', 0):
            self.run_command('sdist_dsc')

        sdist_dsc_command = self.get_finalized_command('sdist_dsc')
        debian_dir = os.path.join(sdist_dsc_command.dist_dir,
                                  self.distribution.get_fullname(),
                                  'debian')

        cmd = ['dpkg-buildpackage', '-rfakeroot', '-b']
        if not self.sign_package:
            cmd.append('-uc')

        env = os.environ.copy()

        source_directory = os.path.join(debian_dir, '..')

        if self.no_test:
            env['DEB_BUILD_OPTIONS'] = 'nocheck'

        print('creating into ', source_directory)
        subprocess.check_call(cmd, cwd=source_directory, env=env)


bdist_deb.description = bdist_deb.__doc__


class upload_dsc(Command):
    """Upload the source package to debian repository. """


upload_dsc.description = upload_dsc.__doc__


class upload_deb(Command):
    """Upload the binary package to debian repository. """


upload_deb.description = upload_deb.__doc__


class add_extras(Command):
    """Injects requirements from given extras_require-parameters. """

    user_options = [
        ('extras=', None, 'Extras to include in Depends: (comma-separated)[default: \'\']'),
    ]

    def initialize_options(self):
        self.sign_package = False
        self.no_test = False
        self.extras = ''

    def finalize_options(self):
        self.extras = [e for e in self.extras.split(',') if e]

    def run(self):
        install_command = self.get_finalized_command('install')
        for e in self.extras:
            extras = self.distribution.extras_require[e]
            install_command.distribution.install_requires.extend(extras)


add_extras.description = add_extras.__doc__
