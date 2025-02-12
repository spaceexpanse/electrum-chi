#!/usr/bin/env python3

# python setup.py sdist --format=zip,gztar

import os
import sys
import platform
import importlib.util
import argparse
import subprocess

from setuptools import setup, find_packages
from setuptools.command.install import install

MIN_PYTHON_VERSION = "3.6.1"
_min_python_version_tuple = tuple(map(int, (MIN_PYTHON_VERSION.split("."))))


if sys.version_info[:3] < _min_python_version_tuple:
    sys.exit("Error: Electrum-CHI requires Python version >= %s..." % MIN_PYTHON_VERSION)

with open('contrib/requirements/requirements.txt') as f:
    requirements = f.read().splitlines()

with open('contrib/requirements/requirements-hw.txt') as f:
    requirements_hw = f.read().splitlines()

# load version.py; needlessly complicated alternative to "imp.load_source":
version_spec = importlib.util.spec_from_file_location('version', 'electrum_chi/electrum/version.py')
version_module = version = importlib.util.module_from_spec(version_spec)
version_spec.loader.exec_module(version_module)

data_files = []

if platform.system() in ['Linux', 'FreeBSD', 'DragonFly']:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root=', dest='root_path', metavar='dir', default='/')
    opts, _ = parser.parse_known_args(sys.argv[1:])
    usr_share = os.path.join(sys.prefix, "share")
    icons_dirname = 'pixmaps'
    if not os.access(opts.root_path + usr_share, os.W_OK) and \
       not os.access(opts.root_path, os.W_OK):
        icons_dirname = 'icons'
        if 'XDG_DATA_HOME' in os.environ.keys():
            usr_share = os.environ['XDG_DATA_HOME']
        else:
            usr_share = os.path.expanduser('~/.local/share')
    data_files += [
        (os.path.join(usr_share, 'applications/'), ['electrum-chi.desktop']),
        (os.path.join(usr_share, icons_dirname), ['electrum_chi/electrum/gui/icons/electrum_chi.png']),
    ]

extras_require = {
    'hardware': requirements_hw,
    'gui': ['pyqt5'],
    'crypto': ['cryptography>=2.6'],
    'tests': ['pycryptodomex>=3.7', 'cryptography>=2.6', 'pyaes>=0.1a1'],
}
# 'full' extra that tries to grab everything an enduser would need (except for libsecp256k1...)
extras_require['full'] = [pkg for sublist in
                          (extras_require['hardware'], extras_require['gui'], extras_require['crypto'])
                          for pkg in sublist]
# legacy. keep 'fast' extra working
extras_require['fast'] = extras_require['crypto']


setup(
    name="Electrum-CHI",
    version=version.ELECTRUM_VERSION,
    python_requires='>={}'.format(MIN_PYTHON_VERSION),
    install_requires=requirements,
    extras_require=extras_require,
    packages=[
        'electrum_chi',
        'electrum_chi.electrum',
        'electrum_chi.electrum.gui',
        'electrum_chi.electrum.gui.qt',
        'electrum_chi.electrum.gui.qt.forms',
        'electrum_chi.electrum.plugins',
    ] + [('electrum_chi.electrum.plugins.'+pkg) for pkg in find_packages('electrum_chi/electrum/plugins')],
    package_dir={
        'electrum_chi': 'electrum_chi',
    },
    package_data={
        '': ['*.txt', '*.json', '*.ttf', '*.otf', '*.csv'],
        'electrum_chi.electrum': [
            'wordlist/*.txt',
            'locale/*/LC_MESSAGES/electrum.mo',
            'lnwire/*.csv',
        ],
        'electrum_chi.electrum.gui': [
            'icons/*',
        ],
    },
    scripts=['electrum_chi/electrum/electrum-chi'],
    data_files=data_files,
    description="Lightweight Xaya Wallet",
    author="The Xaya developers; based on Electrum by Thomas Voegtlin, Electrum-DOGE by The Electrum-DOGE contributors and Electrum-NMC by the Namecoin developers",
    author_email="info@xaya.io",
    license="GNU GPLv3+ for Electrum-DOGE components; MIT Licence for all other components",
    url="https://www.xaya.io/",
    long_description="""Lightweight Xaya Wallet""",
)
