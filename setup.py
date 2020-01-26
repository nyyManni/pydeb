"""setup file for pydeb. """
import os

from setuptools import setup, find_packages


# Read metadata from the package
meta = {}
package_dir = 'src'
packages = find_packages(where='src')
for p in packages:
    path = os.path.join(package_dir, *p.split('.'))
    candidate = os.path.join(path, '_meta.py')
    if os.path.isfile(candidate):
        with open(candidate, 'rt') as f:
            exec(f.read(), meta)  # pylint: disable=exec-used

setup(name='pydeb',
      version=meta['__version__'],
      description='A setuptools extension to generate debian package files.',
      long_description='',
      author=meta['__author__'],
      url='https://github.com/nyyManni/pydeb',
      author_email='h@nyymanni.com',
      license=meta['__license__'],
      packages=packages,
      package_dir={'': package_dir},
      keywords='deb build setup debian dist',
      include_package_data=True,
      platforms='POSIX',
      install_requires=[
          'jinja2'
      ],
      entry_points={
          'distutils.commands': [
              'sdist_dsc = pydeb.commands:sdist_dsc',
              'bdist_deb = pydeb.commands:bdist_deb',
              'upload_dsc = pydeb.commands:upload_dsc',
              'upload_deb = pydeb.commands:upload_deb',
              'add_extras = pydeb.commands:add_extras',
          ]
      },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3 :: Only',
          'Operating System :: POSIX :: Linux',
          'Intended Audience :: Developers',
          'License :: MIT',
          'Topic :: Software Development :: Build Tools'
      ],
      options={
          'sdist_dsc': {
              # 'debian_revision': 1
          },
          'bdist_deb': {
              # 'sign_package': False
          }
      })
