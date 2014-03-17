#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2014 SlavikZ <slavikz@pc>
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Unity
from gi.repository import Gio, GLib
import gettext
import datetime
import dbus
import dbus.mainloop.glib

APP_NAME = 'unity-scope-everpad'
LOCAL_PATH = '/usr/share/locale/'
gettext.bindtextdomain(APP_NAME, LOCAL_PATH)
gettext.textdomain(APP_NAME)
_ = gettext.gettext

GROUP_NAME = 'com.canonical.Unity.Scope.Notes.Everpad'
UNIQUE_PATH = '/com/canonical/unity/scope/notes/everpad'

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
