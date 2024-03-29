#!/usr/bin/env python
from setuptools import setup

version = '0.0.0.1'

try:
    hash = (
        subprocess
        .check_output(shlex.split('git rev-parse --short HEAD'))
        .rstrip()
        .decode('ASCII')
    )
    commit = (
        subprocess
        .check_output(shlex.split('git rev-list --count HEAD'))
        .rstrip()
        .decode('ASCII')
    )
except:
    pass
else:
    version = '{}.dev{}+{}'.format(version, commit, hash)

setup(
    name='ultrastar-scripts',
    version=version,
    description='A collection of scripts to aid developing songs in Ultrastar format.',
    author='barbeque',
    author_email='barbeque.squared@gmail.com',
    url='https://github.com/barbeque-squared/ultrastar-scripts',
    packages=[
        'ultrastar_scripts'
    ],
    package_dir={'': 'src'},
    license='MIT',
    entry_points={
        'console_scripts': [
            'ultrastar-check = ultrastar_scripts.check:main',
            'ultrastar-fix-linebreaks = ultrastar_scripts.fix_linebreaks:main',
            'ultrastar-fix-whitespace = ultrastar_scripts.fix_whitespace:main',
            'ultrastar-multiply-bpm = ultrastar_scripts.multiply_bpm:main',
            'ultrastar-split-lyrics = ultrastar_scripts.split_lyrics:main',
            'ultrastar-songlist-csv = ultrastar_scripts.songlist_csv:main',
            'ultrastar-songlist-json = ultrastar_scripts.songlist_json:main'
        ]
    }
)
