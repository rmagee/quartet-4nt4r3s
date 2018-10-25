#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import glob


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from quartet_4nt4r3s/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')

def get_data_files(path):
    data_files = []
    directories = glob.glob(path)
    for directory in directories:
        files = glob.glob(directory + '*')
        data_files.append((directory, files))
    return data_files


version = get_version("quartet_4nt4r3s", "__init__.py")


if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='quartet_4nt4r3s',
    version=version,
    description="""Parsing API for Antares""",
    long_description=readme + '\n\n' + history,
    author='Loic Duros',
    author_email='slab@serial-lab.com',
    url='https://gitlab.com/lduros/quartet_4nt4r3s',
    packages=[
        'quartet_4nt4r3s',
    ],
    data_files=get_data_files('quartet_4nt4r3s/templates/soap/'),
    include_package_data=True,
    install_requires=[],
    license="GPLv3",
    zip_safe=False,
    keywords='quartet_4nt4r3s',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
