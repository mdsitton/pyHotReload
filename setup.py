import glob
import os
import shutil

from distutils import sysconfig
from setuptools import setup, Command
from setuptools.command.install import install

here=os.path.dirname(os.path.abspath(__file__))
site_packages_path = sysconfig.get_python_lib()

class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    CLEAN_FILES = './build ./dist ./*.pyc ./*.tgz ./*.egg-info'.split(' ')
    
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        global here

        for path_spec in self.CLEAN_FILES:
            # Make paths absolute and relative to this path
            abs_paths = glob.glob(os.path.normpath(os.path.join(here, path_spec)))
            for path in [str(p) for p in abs_paths]:
                if not path.startswith(here):
                    # Die if path in CLEAN_FILES is absolute + outside this directory
                    raise ValueError("%s is not a path inside %s" % (path, here))
                print('removing %s' % path)
                shutil.rmtree(path)


long_description="""
pyhotreload allows you to patch a system while it is running.
"""

setup(
    name='pyhotreload',
    version='0.0.1',
    description='patch a system while its running',
    long_description=long_description,

    cmdclass={
        'clean': CleanCommand,
    },

    url='https://github.com/mdsitton/pyHotReload/',
    author='Matthew Sitton',
    author_email='matthewsitton@gmail.com',
    license='',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        #'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],

    # What does your project relate to?
    keywords='hot reload',

    install_requires=[],

    packages=['hotreload'],
)
