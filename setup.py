"""setup file for pydeb. """
from setuptools import setup, find_packages


setup(name='pydeb',
      version='0.1',
      description='A setuptools extension to generate debian package files.',
      long_description='',
      author='Henrik Nyman',
      url='https://github.com/nyyManni/pydeb',
      author_email='h@nyymanni.com',
      license='MIT',
      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      keywords='deb build setup debian dist',
      include_package_data=True,
      platforms='POSIX',
      install_requires=[
          'jinja2'
      ],
      extras_require={
          'bson': ['bson']
      },
      entry_points={
          'distutils.commands': [
              'sdist_dsc = pydeb.commands:sdist_dsc',
              'bdist_deb = pydeb.commands:bdist_deb',
              'upload_dsc = pydeb.commands:upload_dsc',
              'upload_deb = pydeb.commands:upload_deb',
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
