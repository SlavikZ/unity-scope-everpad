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
from gi.repository import Gio, GLib, Notify
import gettext
import datetime
import dbus
import dbus.mainloop.glib
import json
from html2text import html2text
from everpad.tools import get_provider, get_pad
from everpad.basetypes import Note, Tag, Notebook, Place, Resource
from everpad.const import API_VERSION


APP_NAME = 'unity-scope-everpad'
LOCAL_PATH = '/usr/share/locale/'
gettext.bindtextdomain(APP_NAME, LOCAL_PATH)
gettext.textdomain(APP_NAME)
_ = gettext.gettext

GROUP_NAME = 'com.canonical.Unity.Scope.Everpad'
UNIQUE_PATH = '/com/canonical/unity/scope/everpad'
SEARCH_URI = ''
SEARCH_HINT = _('Search Everpad notes')
NO_RESULTS_HINT = _('Sorry, there are no Everpad notes that match your search.')
PROVIDER_CREDITS = _('Powered by Everpad and Evernote')
SVG_DIR = '/usr/share/icons/unity-icon-theme/places/svg/'
PROVIDER_ICON = SVG_DIR+'service-everpad.svg'
DEFAULT_RESULT_ICON = 'everpad'
DEFAULT_RESULT_MIMETYPE = 'application/x-desktop'
DEFAULT_RESULT_TYPE = Unity.ResultType.PERSONAL

c1 = {'id': 'all_notes',
      'name':_('All Notes'),
      'icon':SVG_DIR+'group-notes.svg',
      'renderer': Unity.CategoryRenderer.HORIZONTAL_TILE}
c2 = {'id': 'pin_notes',
      'name':_('Pin Notes'),
      'icon':SVG_DIR+'group-notes.svg',
      'renderer': Unity.CategoryRenderer.HORIZONTAL_TILE}

CATEGORIES = [c1, c2]

FILTERS = []

m1 = {'id': 'last_changed',
      'type': 's',
      'field': Unity.SchemaFieldType.OPTIONAL}
m2 = {'id': 'tags',
      'type': 's',
      'field': Unity.SchemaFieldType.OPTIONAL}
EXTRA_METADATA = [m1, m2]

#dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
everpad_provider = get_provider()


# Classes below this point establish communication
# with Unity, you probably shouldn't modify them.
class MySearch (Unity.ScopeSearchBase):
    def __init__(self, search_context):
        super(MySearch, self).__init__()
        self.set_search_context(search_context)
        self.all_notes = 0
        self.pin_notes = 1


    def search(self, search, filters):
        results = []
        try:
            version = everpad_provider.get_api_version()
        except (  # dbus raise some magic
                  dbus.exceptions.UnknownMethodException,
                  dbus.exceptions.DBusException,
        ):
            version = -1
        if version != API_VERSION:
            dim = datetime.now() - getattr(self, 'last_api_notify', datetime.now())
            if dim.seconds > 600:
                Notify.init("everpad")
                Notify.Notification.new('everpad', _('Wrong everpad API version'),
                                        '').show()
                self.last_api_notify = datetime.now()
            return results
        notebooks = dbus.Array([], signature='i')
        place = 0
        #tags = dbus.Array(self.tag_filter_ids, signature='i')
        tags = dbus.Array([], signature='i')
        for note_struct in everpad_provider.find_notes(search, notebooks, tags,
                                                       place, 1000, Note.ORDER_TITLE, -1,
                                                       ):
            note = Note.from_tuple(note_struct)
            last_changed = datetime.datetime.fromtimestamp(note.updated/1000).strftime('%x')
            note_tags = ','.join(note.tags)
            note_uri = json.dumps({'id': note.id, 'search': search})
            results.append({'uri': note_uri,
                            'title': note.title,
                            'comment': html2text(note.content),
                            'category': self.pin_notes if note.pinnded else self.all_notes,
                            'last_changed': GLib.Variant('s', last_changed),
                            'tags': GLib.Variant('s', note_tags)
                            })
        return results

    def do_run(self):
        """
        Adds results to the model
        """
        try:
            result_set = self.search_context.result_set
            for i in self.search(self.search_context.search_query,self.search_context.filter_state):
                if not 'uri' in i or not i['uri'] or i['uri'] == '':
                    continue
                if not 'icon' in i or not i['icon'] or i['icon'] == '':
                    i['icon'] = DEFAULT_RESULT_ICON
                if not 'mimetype' in i or not i['mimetype'] or i['mimetype'] == '':
                    i['mimetype'] = DEFAULT_RESULT_MIMETYPE
                if not 'result_type' in i or not i['result_type'] or i['result_type'] == '':
                    i['result_type'] = DEFAULT_RESULT_TYPE
                if not 'category' in i or not i['category'] or i['category'] == '':
                    i['category'] = 0
                if not 'title' in i or not i['title']:
                    i['title'] = ''
                if not 'comment' in i or not i['comment']:
                    i['comment'] = ''
                if not 'dnd_uri' in i or not i['dnd_uri'] or i['dnd_uri'] == '':
                    i['dnd_uri'] = i['uri']
                result_set.add_result(**i)
        except Exception as error:
            print (error)


class Preview (Unity.ResultPreviewer):

    def do_run(self):
        obj = json.loads(self.result.uri)
        note_id = obj['id']
        #note = Note.from_tuple(everpad_provider.get_note(obj['id']))
        #preview = Unity.GenericPreview.new(note.title, html2text(note.content), None,)
        preview = Unity.GenericPreview.new(self.result.title, self.result.comment.strip(), None)
        image = None
        for _res in everpad_provider.get_note_resources(note_id):
            res = Resource.from_tuple(_res)
            if 'image' in res.mime:
                image = 'file://%s' % res.file_path
        if image:
            preview.props.image_source_uri = image
        if self.result.metadata and 'last_changed' in self.result.metadata and self.result.metadata['last_changed'].get_string() != '':
            preview.props.subtitle = self.result.metadata['last_changed'].get_string()
        view_action = Unity.PreviewAction.new("view", _("Edit"), None)
        preview.add_action(view_action)
        #edit = Unity.PreviewAction.new("edit", "Edit", None)
        #edit.connect('activated', self.handle_uri)
        #preview.add_action(edit)
        return preview


class Scope (Unity.AbstractScope):
    def __init__(self):
        Unity.AbstractScope.__init__(self)

    def do_get_search_hint(self):
        return SEARCH_HINT

    def do_get_schema(self):
        """
        Adds specific metadata fields
        """
        schema = Unity.Schema.new()
        if EXTRA_METADATA:
            for m in EXTRA_METADATA:
                schema.add_field(m['id'], m['type'], m['field'])
            #FIXME should be REQUIRED for credits
        schema.add_field('provider_credits', 's', Unity.SchemaFieldType.OPTIONAL)
        return schema

    def do_get_categories(self):
        """
        Adds categories
        """
        cs = Unity.CategorySet.new()
        if CATEGORIES:
            for c in CATEGORIES:
                cat = Unity.Category.new(c['id'], c['name'],
                                         Gio.ThemedIcon.new(c['icon']),
                                         c['renderer'])
                cs.add(cat)
        return cs

    def do_get_filters(self):
        '''
        Adds filters
        '''
        fs = Unity.FilterSet.new ()
        #        if FILTERS:
        #
        return fs

    def do_get_group_name(self):
        return GROUP_NAME

    def do_get_unique_name(self):
        return UNIQUE_PATH

    def do_create_search_for_query(self, search_context):
        se = MySearch (search_context)
        return se

    def do_create_previewer(self, result, metadata):
        rp = Preview()
        rp.set_scope_result(result)
        rp.set_search_metadata(metadata)
        return rp

    def do_activate(self, result, metadata, id):
        obj = json.loads(result.uri)
        everpad = get_pad()
        everpad.open_with_search_term(int(obj['id']), obj.get('search', ''))
        return Unity.ActivationResponse(handled=Unity.HandledType.HIDE_DASH, goto_uri=None)


def load_scope():
    return Scope()
