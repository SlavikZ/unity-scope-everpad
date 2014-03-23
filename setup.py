#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
from DistUtilsExtra.command import *

setup(name='unity-scope-everpad',
      version='0.0.1',
      author='SlavikZ',
      author_email='slavikz@PC',
      license='GNU General Public License (GPL)',
      data_files=[
    ('share/dbus-1/services', ['data/unity-scope-everpad.service']),
#    ('share/icons/unity-icon-theme/places/svg', ['data/icons/service-everpad.svg']),
    ('share/unity-scopes/everscope', ['src/everscope/unity_everpad_daemon.py']),
    ('share/unity-scopes/everscope', ['src/everscope/__init__.py']),
    ], cmdclass={'build':  build_extra.build_extra,
                 'build_i18n': build_i18n.build_i18n,})
